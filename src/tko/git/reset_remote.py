"""Replace working trees in several repositories with their remote branches."""

from __future__ import annotations

import subprocess
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from tko.git.console import translate
from tko.util.console import Console


@dataclass(frozen=True, slots=True)
class ResetResult:
    repository: Path
    success: bool
    message: str


class RemoteReset:
    @staticmethod
    def run_git_command(directory: Path, *args: str) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                ["git", *args], cwd=directory, capture_output=True,
                text=True, timeout=120, check=False,
            )
        except FileNotFoundError as error:
            raise RuntimeError(translate("Git não encontrado.", "Git was not found.")) from error
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(translate("Git excedeu o tempo limite.", "Git timed out.")) from error
        except OSError as error:
            raise RuntimeError(str(error)) from error

    @staticmethod
    def default_branch(directory: Path) -> str:
        result: subprocess.CompletedProcess[str] = RemoteReset.run_git_command(
            directory, "symbolic-ref", "--short", "refs/remotes/origin/HEAD",
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().rsplit("/", 1)[-1]
        return "main"

    @staticmethod
    def reset(directory: Path) -> ResetResult:
        if not directory.is_dir():
            return ResetResult(directory, False, translate(
                "Diretório não encontrado.", "Directory not found.",
            ))
        try:
            repository: subprocess.CompletedProcess[str] = RemoteReset.run_git_command(
                directory, "rev-parse", "--is-inside-work-tree",
            )
            if repository.returncode != 0 or repository.stdout.strip() != "true":
                return ResetResult(directory, False, translate(
                    "Este diretório não é um repositório Git.",
                    "This directory is not a Git repository.",
                ))
            branch: str = RemoteReset.default_branch(directory)
            fetched: subprocess.CompletedProcess[str] = RemoteReset.run_git_command(
                directory, "fetch", "--prune", "--filter=blob:none",
                "--tags", "origin", branch,
            )
            if fetched.returncode != 0:
                return ResetResult(directory, False, translate(
                    "Falha ao buscar atualizações: ", "Fetch failed: ",
                ) + (fetched.stderr.strip() or fetched.stdout.strip()))
            cleaned: subprocess.CompletedProcess[str] = RemoteReset.run_git_command(
                directory, "clean", "-ffdx",
            )
            if cleaned.returncode != 0:
                return ResetResult(directory, False, translate(
                    "Falha ao remover arquivos locais: ",
                    "Could not remove local files: ",
                ) + (cleaned.stderr.strip() or cleaned.stdout.strip()))
            reset: subprocess.CompletedProcess[str] = RemoteReset.run_git_command(
                directory, "reset", "--hard", "FETCH_HEAD",
            )
            if reset.returncode != 0:
                return ResetResult(directory, False, translate(
                    "Falha ao substituir arquivos locais: ",
                    "Could not reset local files: ",
                ) + (reset.stderr.strip() or reset.stdout.strip()))
            return ResetResult(directory, True, translate(
                f"Arquivos locais substituídos por origin/{branch}.",
                f"Local files replaced with origin/{branch}.",
            ))
        except RuntimeError as error:
            return ResetResult(directory, False, str(error))

    @staticmethod
    def reset_many(repositories: list[Path], max_workers: int = 10) -> list[ResetResult]:
        Console.print(translate(
            f"Atualizando {len(repositories)} repositório(s) com {max_workers} tarefa(s).",
            f"Resetting {len(repositories)} repositories with {max_workers} workers.",
        ))
        started: float = time.monotonic()
        results: list[ResetResult] = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures: dict[Future[ResetResult], Path] = {
                executor.submit(RemoteReset.reset, repository): repository
                for repository in repositories
            }
            for future in as_completed(futures):
                result: ResetResult = future.result()
                results.append(result)
                label: str = "OK" if result.success else translate("ERRO", "ERROR")
                Console.print(f"{result.repository}: [{label}] {result.message}")
        elapsed: float = time.monotonic() - started
        Console.print(translate(
            f"Concluído em {elapsed:.2f}s.", f"Completed in {elapsed:.2f}s.",
        ))
        return results
