import subprocess
import sys
from pathlib import Path

import typer
from typing import Literal
from tko.enums.diff_mode import DiffMode
from tko.cli.cli_profile import app as profile_app
from tko.cli.cli_source import app as source_app

from tko.config.settings import Settings
from tko.util.console import Console
from tko.util.rt import RT

app = typer.Typer(help="Manage installation, global preferences and repository configuration", no_args_is_help=True)
app.add_typer(profile_app, name="profile")
app.add_typer(source_app, name="source")

@app.command("set", help="Set default configuration values")
def config_set(
    ctx: typer.Context,
    diff_mode: DiffMode | None = typer.Option(None, "--diff-mode", help="Default diff layout"),
    editor : None | str = typer.Option(None, "--editor", help="Set editor command"),
    images: Literal["0", "1"] | None = typer.Option(None, "--images", help="Enable images [0|1]"),
    timeout: None | int = typer.Option(None, "--timeout", min=1, help="Set timeout in sec"),
) -> None:
    from tko.cmds.cmd_config import CmdConfig, ConfigParams
    settings: Settings = ctx.obj
    param: ConfigParams = ConfigParams()
    param.diff_mode = diff_mode
    param.images = images
    param.editor = editor
    param.timeout = timeout

    if settings:
        CmdConfig.execute(settings, param)

@app.command("list", help="List default configuration values")
def config_list(ctx: typer.Context) -> None:
    settings: Settings = ctx.obj
    Console.print(RT.parse(str(settings)))


@app.command("reset", help="Reset global configuration to factory defaults")
def config_reset(ctx: typer.Context) -> None:
    settings: Settings = ctx.obj
    settings.reset().save_settings()
    Console.print(settings.get_settings_file())


@app.command("self-update", help="Update a script-managed TKO installation")
def self_update_cmd() -> None:
    from tko.installation import InstallationMethod, ManagedInstallation, installation_method, run_self_update

    installation: ManagedInstallation | None = ManagedInstallation.from_executable(Path(sys.executable))
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

    installation: ManagedInstallation | None = ManagedInstallation.from_executable(Path(sys.executable))
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

@app.command("clear-cache", help="Clear the global Git cache for remote sources")
def config_clear_cache(ctx: typer.Context) -> None:
    from tko.config.user_data import UserData
    from tko.repository.git_cache import GitCache

    settings: Settings = ctx.obj
    cache: GitCache = GitCache(cache_dir=UserData.global_cache_dir(), update_mode=settings.rs.update_mode)
    cache.clear_cache()


if __name__ == "__main__":
    app()
