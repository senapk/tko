from __future__ import annotations

from loguru import logger
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tko.util.rt import RT
from tko.util.console import Console

_PULL_UNEXPECTED_ERROR: str = "Unexpected error executing git command in {directory}"
_PULL_UP_TO_DATE: str = "Up-to-date"
_PULL_FETCH_LABEL: str = "Fetch"
_PULL_FETCH_FAILED: str = "Fetch failed: {msg}"
_PULL_UPDATE_LABEL: str = "Update"
_PULL_FALLBACK_LABEL: str = "Fallback"
_PULL_ERROR_IN_REPO: str = "Error pulling from {repo}"
_PULL_COMPLETED: str = "Completed in {elapsed:.2f}s"


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
            logger.exception(_PULL_UNEXPECTED_ERROR.format(directory=directory))
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
    def pull(directory: str) -> RT:
        repo_path = Path(directory)

        if not repo_path.is_dir() or not (repo_path / ".git").exists():
            return RT()

        output = RT(directory, "g") + " "

        branch = Pull.get_default_branch(directory)

        # 1. Skip se já atualizado
        if Pull.is_up_to_date(directory, branch):
            return output + RT(f"{_PULL_UP_TO_DATE}", "c")

        # 2. Fetch otimizado
        output += RT(f"{_PULL_FETCH_LABEL}", "y")
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
            return output + "\n" + _PULL_FETCH_FAILED.format(msg=msg)

        # 3. Aplicar atualização
        output += RT(f"{_PULL_UPDATE_LABEL}", "y")
        ok, msg = Pull.git_ok(directory, "reset", "--hard", "FETCH_HEAD")

        if not ok:
            # fallback raro (repo zoado)
            output += RT(f"{_PULL_FALLBACK_LABEL}", "r")
            Pull.git_ok(directory, "clean", "-fd")
            ok, msg = Pull.git_ok(directory, "reset", "--hard", f"origin/{branch}")
            if not ok:
                return output + f"\nReset failed: {msg}"

        return output + "\n"

    @staticmethod
    def pull_all_parallel(repo_list: list[Path], max_workers: int = 10):
        Console.print(RT("\nPull of {count} repositories ({threads} threads)".format(count=len(repo_list), threads=max_workers), "y"))
        start = time.time()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(Pull.pull, str(repo)): repo for repo in repo_list}

            for future in as_completed(futures):
                repo = futures[future]
                try:
                    output = future.result()
                    if output.plain():
                        Console.print(output)
                except Exception:
                    logger.exception(_PULL_ERROR_IN_REPO.format(repo=repo))

        elapsed = time.time() - start
        Console.print(RT(f"\n{_PULL_COMPLETED}".format(elapsed=elapsed), "y"))
