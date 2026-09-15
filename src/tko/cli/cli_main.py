import typer
from typing import Optional
from pathlib import Path
import subprocess
import sys

from tko.config.settings import Settings

# This file contains the root commands that don't belong to a Typer sub-app 
# but will be added directly to the main Typer app.

def register_main_commands(app: typer.Typer):
    @app.command("self-update", help="Update a script-managed TKO installation")
    def self_update_cmd() -> None:
        from tko.installation import InstallationMethod, ManagedInstallation, installation_method, run_self_update

        installation = ManagedInstallation.from_executable(Path(sys.executable))
        if installation is None:
            if installation_method() == InstallationMethod.PIPX:
                typer.echo("Esta instalação usa pipx. Execute: pipx upgrade tko")
            else:
                typer.echo("Esta instalação não é gerenciada pelo instalador do TKO.", err=True)
            raise typer.Exit(1)
        try:
            run_self_update(installation)
        except subprocess.CalledProcessError as error:
            typer.echo(f"Não foi possível atualizar o TKO: {error}", err=True)
            raise typer.Exit(1) from error
        typer.echo("TKO atualizado.")

    @app.command("uninstall", help="Remove a script-managed TKO installation")
    def uninstall_cmd(yes: bool = typer.Option(False, "--yes", "-y", help="Remove without confirmation")) -> None:
        from tko.installation import InstallationMethod, ManagedInstallation, installation_method, remove_managed_installation

        installation = ManagedInstallation.from_executable(Path(sys.executable))
        if installation is None:
            if installation_method() == InstallationMethod.PIPX:
                typer.echo("Esta instalação usa pipx e não será removida. Execute: pipx uninstall tko")
            else:
                typer.echo("Esta instalação não é gerenciada pelo instalador do TKO.", err=True)
            raise typer.Exit(1)
        if not yes and not typer.confirm("Remover a instalação gerenciada do TKO?"):
            typer.echo("Remoção cancelada.")
            return
        remove_managed_installation(installation)
        typer.echo("TKO removido.")

    @app.command("run", help="Runs a task in raw terminal")
    def run_cmd( # type: ignore
        ctx: typer.Context,
        target_list: Optional[list[str]] = typer.Argument(None, help="Solvers files, test cases or directories containing them"),
        index: Optional[int] = typer.Option(None, "--index", "-i", help="Run a specific test index"),
        language: str = typer.Option(None, "--lang", "-l", help="Language for autoloading (e.g. py, cpp, java, go, kt)"),
        filter: bool = typer.Option(False, "--filter", "-f", help="Filter solver files in temporary directory before running"),
        eval: bool = typer.Option(False, "--eval", "-e", help="Show percentage of passed tests"),
        compact: bool = typer.Option(False, "--compact", "-c", help="Hide test case descriptions in failures"),
        none: bool = typer.Option(False, "--none", "-n", help="Hide all failures"),
        all: bool = typer.Option(False, "--all", "-a", help="Show all failures"),
        down: bool = typer.Option(False, "--down", "-d", help="Diff mode: top-to-bottom"),
        side: bool = typer.Option(False, "--side", "-s", help="Diff mode: side-by-side")
    ):
        from tko.cli.common import load_repo
        from tko.util.param import Param
        from tko.enums.diff_count import DiffCount
        from tko.enums.diff_mode import DiffMode
        from tko.cmds.cmd_run import Run
        
        settings: Settings = ctx.obj

        param = Param.Basic().set_index(index)
        if none:
            param.set_diff_count(DiffCount.NONE)
        elif all:
            param.set_diff_count(DiffCount.ALL)
        else:
            param.set_diff_count(DiffCount.FIRST)

        if filter:
            param.set_filter(True)
        if compact:
            param.set_compact(True)

        if not side and not down:
            param.set_diff_mode(settings.app.diff_mode if settings else DiffMode.SIDE)
        elif side:
            param.set_diff_mode(DiffMode.SIDE)
        elif down:
            param.set_diff_mode(DiffMode.DOWN)

        repo, _ = load_repo(settings.rs, show_warnings=False)
        targets = [Path(target) for target in target_list] if target_list else []
        cmd_run = Run(settings, targets, param, language, repo)
        if eval:
            cmd_run.show_track_info().show_self_info()

        cmd_run.execute()

    @app.command("open", help="Open repository in interactive mode")
    def open_cmd( # type: ignore
            ctx: typer.Context, 
            audit: bool = typer.Option(False, "--audit", "-a", help="Enable audit watcher"),
        ): 
        from tko.cli.common import load_repo
        from tko.cmds.cmd_open import CmdOpen
        from tko.config.check_version import CheckVersion

        settings: Settings = ctx.obj        
        repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=True)
        if repo is None:
            return
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
    def init_cmd( # type: ignore
        ctx: typer.Context,
        language: Optional[str] = typer.Option(None, "--language", "-l", help="Default repository language (e.g. py, cpp, java, go, kt)"),
        skip: bool = typer.Option(False, "--skip-sources", "--skip-remotes", "-s", help="Skip asking about default sources"),
        profile: Optional[str] = typer.Option(None, "--profile", help="Initialize from a linked profile URI"),
    ):
        from tko.repository.repository_starter import RepositoryStarter
        

        settings: Settings = ctx.obj
        
        rep_starter = RepositoryStarter(settings=settings, language=language, skip_add_remote=skip, profile_uri=profile)
        rep_starter.execute()
