import typer
from typing import Optional, Literal
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
        failures: Literal["first", "all", "none"] = typer.Option("first", "--failures", help="Failures to display"),
        diff_mode: DiffMode | None = typer.Option(None, "--diff-mode", help="Diff layout"),
    ) -> None:
        from tko.cli.common import load_repo
        from tko.util.param import Param
        from tko.enums.diff_count import DiffCount
        from tko.enums.diff_mode import DiffMode
        from tko.cmds.cmd_run import Run

        settings: Settings = ctx.obj

        param = Param.Basic().set_index(index)
        counts: dict[str, DiffCount] = {"first": DiffCount.FIRST, "all": DiffCount.ALL, "none": DiffCount.NONE}
        param.set_diff_count(counts[failures])

        if filter:
            param.set_filter(True)
        if compact:
            param.set_compact(True)

        param.set_diff_mode(diff_mode if diff_mode is not None else settings.app.diff_mode)

        repo, _ = load_repo(settings.rs, show_warnings=False)
        targets = [Path(target) for target in target_list] if target_list else []
        cmd_run = Run(settings, targets, param, language, repo)
        if eval:
            cmd_run.show_track_info().show_self_info()

        cmd_run.execute()

    @app.command("open", help="Open repository in interactive mode")
    def open_cmd(
            ctx: typer.Context,
            audit: bool = typer.Option(False, "--audit", "-a", help="Enable audit watcher"),
        ) -> None:
        from tko.cli.common import load_repo
        from tko.cmds.cmd_open import CmdOpen
        from tko.config.check_version import CheckVersion

        settings: Settings = ctx.obj
        repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=True)
        if repo is None:
            raise typer.Exit(1)
        settings.rs.changedir = repo.root_dir
        # change dir to repo root dir so that all commands run in the correct context
        import os
        os.chdir(repo.root_dir)

        from tko.repository.repository_watcher import RepositoryWatcher
        watcher = RepositoryWatcher(repo).start_watching(
            log_audit=(repo.audit.enabled or audit),
            audit_verbose=True,
            audit_interval_seconds=repo.audit.interval_seconds,
        )
        action = CmdOpen(settings, repo, watcher)

        if not settings.rs.force_offline:
            if not CheckVersion(settings).is_updated():
                action.display_need_update()

        action.execute()
        watcher.stop_watching()

    @app.command("init", help="Initialize empty TKO repository")
    def init_cmd(
        ctx: typer.Context,
        language: Optional[str] = typer.Option(None, "--language", "-l", help="Default repository language (e.g. py, cpp, java, go, kt)"),
        skip: bool = typer.Option(False, "--skip-sources", "-s", help="Skip asking about default sources"),
        profile: Optional[str] = typer.Option(None, "--profile", help="Initialize from a linked profile URI"),
    ) -> None:
        from tko.repository.repository_starter import RepositoryStarter


        settings: Settings = ctx.obj

        rep_starter = RepositoryStarter(settings=settings, language=language, skip_add_remote=skip, profile_uri=profile)
        rep_starter.execute()
