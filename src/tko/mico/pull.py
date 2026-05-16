from __future__ import annotations

import logging
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tko.util.rtext import RText


logger = logging.getLogger(__name__)


class Pull:

    @staticmethod
    def run_git_command(directory: str, command_args: list[str]) -> tuple[str, str, int]:
        try:
            result = subprocess.run(
                ["git"] + command_args,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=120,
            )
            return result.stdout, result.stderr, result.returncode
        except FileNotFoundError:
            return "", "git not found", 127
        except Exception:
            logger.exception("Erro inesperado ao executar comando git em %s", directory)
            return "", "unexpected error", 1

    @staticmethod
    def git_ok(directory: str, *args: str) -> tuple[bool, str]:
        stdout, stderr, code = Pull.run_git_command(directory, list(args))
        return code == 0, stderr or stdout

    @staticmethod
    def get_default_branch(directory: str) -> str:
        stdout, _, code = Pull.run_git_command(
            directory,
            ["symbolic-ref", "refs/remotes/origin/HEAD"]
        )
        if code == 0 and stdout:
            return stdout.strip().split("/")[-1]
        return "main"

    @staticmethod
    def is_up_to_date(directory: str, branch: str) -> bool:
        local, _, _ = Pull.run_git_command(directory, ["rev-parse", "HEAD"])
        remote, _, _ = Pull.run_git_command(directory, ["ls-remote", "origin", branch])

        if not remote:
            return False

        remote_hash = remote.split()[0]
        return local.strip() == remote_hash

    @staticmethod
    def pull(directory: str) -> RText:
        repo_path = Path(directory)

        if not repo_path.is_dir() or not (repo_path / ".git").exists():
            return RText()

        output = RText(directory, "g") + " "

        branch = Pull.get_default_branch(directory)

        # 1. Skip se já atualizado
        if Pull.is_up_to_date(directory, branch):
            return output + RText("Up-to-date", "c")

        # 2. Fetch otimizado
        output += RText("Fetch ", "y")
        ok, msg = Pull.git_ok(
            directory,
            "fetch",
            "--prune",
            "--filter=blob:none",
            "--tags",
            "origin",
            branch
        )
        if not ok:
            return output + "\nFetch failed: " + msg

        # 3. Aplicar atualização
        output += RText("Update ", "y")
        ok, msg = Pull.git_ok(directory, "reset", "--hard", "FETCH_HEAD")

        if not ok:
            # fallback raro (repo zoado)
            output += RText("Fallback ", "r")
            Pull.git_ok(directory, "clean", "-fd")
            ok, msg = Pull.git_ok(directory, "reset", "--hard", f"origin/{branch}")
            if not ok:
                return output + "\nReset failed: " + msg

        return output + "\n"

    @staticmethod
    def pull_all_parallel(repo_list: list[Path], max_workers: int = 10):
        print("\n" + str(RText(f"Pull de {len(repo_list)} repositórios ({max_workers} threads)", "y")))
        start = time.time()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(Pull.pull, str(repo)): repo for repo in repo_list}

            for future in as_completed(futures):
                repo = futures[future]
                try:
                    output = future.result()
                    if output.plain():
                        print(output)
                except Exception:
                    logger.exception("Erro ao fazer pull em %s", repo)

        elapsed = time.time() - start
        print("\n" + str(RText(f"Finalizado em {elapsed:.2f}s", "y")))
