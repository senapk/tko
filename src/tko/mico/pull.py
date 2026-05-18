from __future__ import annotations

import logging
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tko.util.rtext import RText
from tko.i18n import Msg, t


logger = logging.getLogger(__name__)

_PULL_UNEXPECTED_ERROR = Msg(
    pt="Erro inesperado ao executar comando git em {directory}",
    en="Unexpected error executing git command in {directory}",
)
_PULL_UP_TO_DATE = Msg(pt="Up-to-date", en="Up-to-date")
_PULL_FETCH_LABEL = Msg(pt="Fetch", en="Fetch")
_PULL_FETCH_FAILED = Msg(pt="Fetch failed: {msg}", en="Fetch failed: {msg}")
_PULL_UPDATE_LABEL = Msg(pt="Update", en="Update")
_PULL_FALLBACK_LABEL = Msg(pt="Fallback", en="Fallback")
_PULL_RESET_FAILED = Msg(pt="Reset failed: {msg}", en="Reset failed: {msg}")
_PULL_ALL_PARALLEL = Msg(
    pt="Pull de {count} repositórios ({threads} threads)",
    en="Pull of {count} repositories ({threads} threads)",
)
_PULL_ERROR_IN_REPO = Msg(
    pt="Erro ao fazer pull em {repo}",
    en="Error pulling from {repo}",
)
_PULL_COMPLETED = Msg(
    pt="Finalizado em {elapsed:.2f}s",
    en="Completed in {elapsed:.2f}s",
)


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
            logger.exception(t(_PULL_UNEXPECTED_ERROR, directory=directory))
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
            return output + RText(t(_PULL_UP_TO_DATE), "c")

        # 2. Fetch otimizado
        output += RText(t(_PULL_FETCH_LABEL), "y")
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
            return output + "\n" + t(_PULL_FETCH_FAILED, msg=msg)

        # 3. Aplicar atualização
        output += RText(t(_PULL_UPDATE_LABEL), "y")
        ok, msg = Pull.git_ok(directory, "reset", "--hard", "FETCH_HEAD")

        if not ok:
            # fallback raro (repo zoado)
            output += RText(t(_PULL_FALLBACK_LABEL), "r")
            Pull.git_ok(directory, "clean", "-fd")
            ok, msg = Pull.git_ok(directory, "reset", "--hard", f"origin/{branch}")
            if not ok:
                return output + "\n" + t(_PULL_RESET_FAILED, msg=msg)

        return output + "\n"

    @staticmethod
    def pull_all_parallel(repo_list: list[Path], max_workers: int = 10):
        print("\n" + str(RText(t(_PULL_ALL_PARALLEL, count=len(repo_list), threads=max_workers), "y")))
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
                    logger.exception(t(_PULL_ERROR_IN_REPO, repo=repo))

        elapsed = time.time() - start
        print("\n" + str(RText(t(_PULL_COMPLETED, elapsed=elapsed), "y")))
