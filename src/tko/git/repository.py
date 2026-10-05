"""Typed subprocess boundary for the educational Git sync flow."""

from __future__ import annotations

import shlex
import subprocess
from typing import Protocol

from tko.git.console import SyncReporter, translate


class GitError(RuntimeError):
    """A Git operation failed or the repository cannot be synchronized."""


class GitSyncOps(Protocol):
    def is_repository(self) -> bool: ...
    def current_branch(self) -> str: ...
    def has_remote(self, remote: str = "origin") -> bool: ...
    def is_merge_in_progress(self) -> bool: ...
    def conflicted_files(self) -> list[str]: ...
    def ensure_no_staged_conflict_markers(self) -> None: ...
    def finish_merge(self) -> None: ...
    def has_local_changes(self) -> bool: ...
    def has_staged_changes(self) -> bool: ...
    def status(self) -> None: ...
    def stage_all(self) -> None: ...
    def staged_diff_stat(self) -> None: ...
    def commit(self, message: str) -> None: ...
    def fetch(self, remote: str = "origin") -> None: ...
    def remote_has_updates(self, branch: str, remote: str = "origin") -> bool: ...
    def merge_fast_forward(self, remote_branch: str) -> bool: ...
    def merge(self, remote_branch: str) -> bool: ...
    def has_commits_to_push(self) -> bool: ...
    def push(self, branch: str, remote: str = "origin") -> None: ...
    def get_config(self, key: str) -> str: ...
    def set_config(self, key: str, value: str) -> None: ...


class GitRepository:
    def __init__(self, console: SyncReporter, executable: str = "git") -> None:
        self.console: SyncReporter = console
        self.executable: str = executable

    def run(
        self, *args: str, check: bool = True, capture_output: bool = False,
        echo: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        command: list[str] = [self.executable, "--no-pager", *args]
        display_command: str = shlex.join(command)
        self.console.command(display_command)
        try:
            result: subprocess.CompletedProcess[str] = subprocess.run(
                command, text=True, capture_output=capture_output, check=False,
            )
        except OSError as error:
            raise GitError(translate("Git não está disponível: ", "Git is unavailable: ") + str(error)) from error
        if capture_output and echo:
            if result.stdout:
                self.console.write(result.stdout.rstrip())
            if result.stderr:
                self.console.write(result.stderr.rstrip())
        if check and result.returncode != 0:
            detail: str = result.stderr.strip() if result.stderr else ""
            if detail:
                raise GitError(f"{display_command}\n{detail}")
            raise GitError(
                translate("Comando falhou", "Command failed")
                + f" ({result.returncode}): {display_command}"
            )
        return result

    def output(self, *args: str, echo: bool = True) -> str:
        return self.run(*args, capture_output=True, echo=echo).stdout.strip()

    def succeeds(self, *args: str) -> bool:
        return self.run(*args, check=False, capture_output=True, echo=False).returncode == 0

    def is_repository(self) -> bool:
        result: subprocess.CompletedProcess[str] = self.run(
            "rev-parse", "--is-inside-work-tree", check=False,
            capture_output=True, echo=False,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"

    def current_branch(self) -> str:
        branch: str = self.output("rev-parse", "--abbrev-ref", "HEAD")
        if branch == "HEAD":
            raise GitError(translate("Você está em HEAD destacado.", "You are in detached HEAD."))
        return branch

    def has_remote(self, remote: str = "origin") -> bool:
        return self.succeeds("remote", "get-url", remote)

    def is_merge_in_progress(self) -> bool:
        return self.succeeds("rev-parse", "-q", "--verify", "MERGE_HEAD")

    def conflicted_files(self) -> list[str]:
        output: str = self.output("diff", "--name-only", "--diff-filter=U")
        return [file for file in output.splitlines() if file.strip()]

    def conflict_marker_files(self) -> list[str]:
        result: subprocess.CompletedProcess[str] = self.run(
            "grep", "--cached", "-l", "-E", r"^(<<<<<<<|>>>>>>>)",
            check=False, capture_output=True, echo=False,
        )
        if result.returncode == 1:
            return []
        if result.returncode != 0:
            raise GitError(translate(
                "Não foi possível verificar os marcadores de conflito.",
                "Could not check conflict markers.",
            ))
        return [file for file in result.stdout.splitlines() if file.strip()]

    def ensure_no_staged_conflict_markers(self) -> None:
        files: list[str] = self.conflict_marker_files()
        if files:
            listing: str = "\n".join(f"  - {file}" for file in files)
            raise GitError(translate(
                "Ainda existem marcadores de conflito nestes arquivos:\n",
                "Conflict markers remain in these files:\n",
            ) + listing + "\n" + translate(
                "Remova os marcadores, resolva os conflitos e execute tko git sync novamente.",
                "Remove the markers, resolve the conflicts, and run tko git sync again.",
            ))

    def finish_merge(self) -> None:
        self.stage_all()
        self.ensure_no_staged_conflict_markers()
        self.run("commit", "--no-edit")

    def has_unstaged_changes(self) -> bool:
        return not self.succeeds("diff", "--quiet")

    def has_staged_changes(self) -> bool:
        return not self.succeeds("diff", "--cached", "--quiet")

    def has_untracked_files(self) -> bool:
        output: str = self.output("status", "--porcelain", "--untracked-files=all", echo=False)
        return any(line.startswith("??") for line in output.splitlines())

    def has_local_changes(self) -> bool:
        return self.has_unstaged_changes() or self.has_staged_changes() or self.has_untracked_files()

    def status(self) -> None:
        self.run("status", "--short", check=False)

    def stage_all(self) -> None:
        self.run("add", "-A")

    def staged_diff_stat(self) -> None:
        self.run("diff", "--cached", "--stat")

    def commit(self, message: str) -> None:
        self.run("commit", "-m", message)

    def fetch(self, remote: str = "origin") -> None:
        self.run("fetch", remote)

    def remote_has_updates(self, branch: str, remote: str = "origin") -> bool:
        output: str = self.output("rev-list", "--left-right", "--count", f"HEAD...{remote}/{branch}")
        parts: list[str] = output.split()
        if len(parts) != 2:
            raise GitError(translate(
                "Não foi possível comparar os repositórios local e remoto.",
                "Could not compare the local and remote repositories.",
            ))
        try:
            return int(parts[1]) > 0
        except ValueError as error:
            raise GitError(translate(
                "Resposta inválida ao comparar os repositórios.",
                "Invalid result while comparing the repositories.",
            )) from error

    def merge_fast_forward(self, remote_branch: str) -> bool:
        return self.run("merge", "--ff-only", remote_branch, check=False).returncode == 0

    def merge(self, remote_branch: str) -> bool:
        return self.run("merge", "--no-edit", remote_branch, check=False).returncode == 0

    def has_upstream(self) -> bool:
        return self.succeeds("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")

    def has_commits_to_push(self) -> bool:
        if not self.has_upstream():
            return True
        count: str = self.output("rev-list", "--count", "@{u}..HEAD")
        try:
            return int(count) > 0
        except ValueError as error:
            raise GitError(translate("Contagem de commits inválida.", "Invalid commit count.")) from error

    def push(self, branch: str, remote: str = "origin") -> None:
        if self.has_upstream():
            self.run("push")
        else:
            self.run("push", "-u", remote, branch)

    def get_config(self, key: str) -> str:
        result: subprocess.CompletedProcess[str] = self.run(
            "config", "--get", key, check=False, capture_output=True, echo=False,
        )
        return result.stdout.strip() if result.returncode == 0 else ""

    def set_config(self, key: str, value: str) -> None:
        self.run("config", key, value)
