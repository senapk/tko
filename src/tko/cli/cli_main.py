import typer
from typing import Optional
from tko.enums.diff_mode import DiffMode
from pathlib import Path

from tko.config.settings import Settings

# This file contains the root commands that don't belong to a Typer sub-app
# but will be added directly to the main Typer app.

def register_main_commands(app: typer.Typer) -> None:
    @app.command("run", help="Runs a task in raw terminal")
    def run_cmd(
        ctx: typer.Context,
        target_list: Optional[list[str]] = typer.Argument(None, help="Solvers files, test cases or directories containing them"),
        index: Optional[int] = typer.Option(None, "--index", "-i", help="Run a specific test index"),
        language: str | None = typer.Option(None, "--language", "-l", help="Language for autoloading (e.g. py, cpp, java, go, kt)"),
        filter: bool = typer.Option(False, "--filter", "-F", help="Filter solver files in temporary directory before running"),
        eval: bool = typer.Option(False, "--eval", "-e", help="Show percentage of passed tests"),
        compact: bool = typer.Option(False, "--compact", "-c", help="Hide test case descriptions in failures"),
        all_failures: bool = typer.Option(False, "--all", help="Display all failures"),
        no_failures: bool = typer.Option(False, "--none", help="Hide failures"),
        side: bool = typer.Option(False, "--side", help="Display differences side by side"),
        down: bool = typer.Option(False, "--down", help="Display differences one above the other"),
    ) -> None:
        from tko.cli.common import load_repo
        from tko.util.param import Param
        from tko.enums.diff_count import DiffCount
        from tko.enums.diff_mode import DiffMode
        from tko.cmds.cmd_run import Run

        settings: Settings = ctx.obj

        param = Param.Basic().set_index(index)
        if all_failures and no_failures:
            raise typer.BadParameter("--all and --none cannot be used together")
        if side and down:
            raise typer.BadParameter("--side and --down cannot be used together")

        diff_count: DiffCount = (
            DiffCount.ALL if all_failures else DiffCount.NONE if no_failures else DiffCount.FIRST
        )
        param.set_diff_count(diff_count)

        if filter:
            param.set_filter(True)
        if compact:
            param.set_compact(True)

        diff_mode: DiffMode = DiffMode.SIDE if side else DiffMode.DOWN if down else settings.app.diff_mode
        param.set_diff_mode(diff_mode)

        repo, _ = load_repo(settings.rs, show_warnings=False)
        targets = [Path(target) for target in target_list] if target_list else []
        cmd_run = Run(settings, targets, param, language, repo)
        if eval:
            cmd_run.show_track_info().show_self_info()

        cmd_run.execute()

    @app.command("open", help="Open repository in interactive mode")
    def open_cmd(
            ctx: typer.Context,
    ) -> None:
        from tko.cli.common import load_repo
        from tko.cmds.cmd_open import CmdOpen
        from tko.config.check_version import CheckVersion

        settings: Settings = ctx.obj
        repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=True)
        if repo is None:
            from tko.repository.repository_starter import RepositoryStarter

            if not RepositoryStarter(settings=settings, language=None, skip_add_remote=False).execute():
                raise typer.Exit(1)
            repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=True)
            if repo is None:
                raise typer.Exit(1)
        settings.rs.changedir = repo.root_dir
        # change dir to repo root dir so that all commands run in the correct context
        import os
        os.chdir(repo.root_dir)

        from tko.repository.repository_watcher import RepositoryWatcher
        watcher = RepositoryWatcher(repo).start_watching(
            log_audit=repo.audit.enabled,
            audit_verbose=True,
            audit_interval_seconds=repo.audit.interval_seconds,
        )
        action = CmdOpen(settings, repo, watcher)

        if not settings.rs.force_offline:
            if not CheckVersion(settings).is_updated():
                action.display_need_update()

        action.execute()
        watcher.stop_watching()

    @app.command("update", help="Update a script-managed TKO installation")
    def update_cmd() -> None:
        from tko.cli.cli_config import self_update_cmd

        self_update_cmd()

    @app.command("uninstall", help="Remove a script-managed TKO installation")
    def uninstall_cmd(yes: bool = typer.Option(False, "--yes", "-y", help="Remove without confirmation")) -> None:
        from tko.cli.cli_config import uninstall_cmd as uninstall

        uninstall(yes)
