from __future__ import annotations

import argparse
from tko.util.text import Text
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
from pathlib import Path


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
        except Exception as e:
            return "", f"unexpected error: {e}", 1

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
    def pull(directory: str) -> Text:
        repo_path = Path(directory)

        if not repo_path.is_dir() or not (repo_path / ".git").exists():
            return Text()

        output = Text("g") + directory + " "

        branch = Pull.get_default_branch(directory)

        # 1. Skip se já atualizado
        if Pull.is_up_to_date(directory, branch):
            return output + Text("c") + "Up-to-date"

        # 2. Fetch otimizado
        output += Text("y") + "Fetch "
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
        output += Text("y") + "Update "
        ok, msg = Pull.git_ok(directory, "reset", "--hard", "FETCH_HEAD")

        if not ok:
            # fallback raro (repo zoado)
            output += Text("r") + "Fallback "
            Pull.git_ok(directory, "clean", "-fd")
            ok, msg = Pull.git_ok(directory, "reset", "--hard", f"origin/{branch}")
            if not ok:
                return output + "\nReset failed: " + msg

        return output + "\n"

    @staticmethod
    def pull_all_parallel(repo_list: list[Path], max_workers: int = 10):
        print(f"\n{Text('y')}Pull de {len(repo_list)} repositórios ({max_workers} threads){Text('e')}")
        start = time.time()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(Pull.pull, str(repo)): repo for repo in repo_list}

            for future in as_completed(futures):
                repo = futures[future]
                try:
                    output = future.result()
                    if output.get_str():
                        print(output)
                except Exception as exc:
                    print(f"{Text('r')}Erro em {repo}: {exc}{Text('e')}")

        elapsed = time.time() - start
        print(f"\n{Text('y')}Finalizado em {elapsed:.2f}s{Text('e')}")


def pull_all_parallel_main(args: argparse.Namespace) -> None:
    path_list = [Path(p) for p in args.path]
    n_threads = args.threads if args.threads else 10
    Pull.pull_all_parallel(path_list, n_threads)