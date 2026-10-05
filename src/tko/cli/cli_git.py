"""Simplified Git commands for students."""

from __future__ import annotations

import typer
from pathlib import Path

from tko.git.console import SyncConsole, create_console, translate
from tko.git.reset_remote import RemoteReset, ResetResult
from tko.git.repository import GitError, GitRepository
from tko.git.sync import MergeCompleted, SyncApplication, UserCancelled


app: typer.Typer = typer.Typer(help="Simplified Git commands", no_args_is_help=True)


@app.command("reset-to-remote", help="Delete all local changes and untracked files, then reset to origin")
def git_reset_to_remote(
    path: list[Path] = typer.Argument(..., help="Paths to repositories"),
    threads: int = typer.Option(10, "--threads", "-t", min=1, help="Number of parallel workers"),
) -> None:
    results: list[ResetResult] = RemoteReset.reset_many(path, threads)
    if any(not result.success for result in results):
        raise typer.Exit(1)


@app.command("sync", help="Commit, fetch, merge, and push origin/main")
def git_sync() -> None:
    console: SyncConsole = create_console()
    application: SyncApplication = SyncApplication(GitRepository(console), console)
    try:
        application.run()
    except MergeCompleted:
        return
    except UserCancelled:
        console.warn(translate("Operação encerrada.", "Operation stopped."))
    except GitError as error:
        console.error(str(error))
        raise typer.Exit(1) from error
    except KeyboardInterrupt as error:
        console.warn(translate("Operação cancelada pelo usuário.", "Operation cancelled by user."))
        raise typer.Exit(130) from error
