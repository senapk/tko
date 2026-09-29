import subprocess
import sys
from pathlib import Path

import typer
from typing import Literal
from tko.enums.diff_mode import DiffMode
from tko.config.settings import Settings
from tko.util.console import Console
from tko.util.rt import RT

app = typer.Typer(help="Manage global preferences", no_args_is_help=True)

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


@app.command("reset", help="Reset global cache, settings or language configuration")
def config_reset(
    ctx: typer.Context,
    target: Literal["cache", "settings", "languages"] = typer.Argument(...),
) -> None:
    settings: Settings = ctx.obj
    if target == "cache":
        from tko.config.user_data import UserData
        from tko.repository.git_cache import GitCache

        GitCache(cache_dir=UserData.global_cache_dir(), update_mode=settings.rs.update_mode).clear_cache()
    elif target == "settings":
        settings.reset().save_settings()
        Console.print(settings.get_settings_file())
    else:
        from tko.config.languages_settings import LanguagesSettings

        settings.get_languages_file().unlink(missing_ok=True)
        settings.get_languages_sample().write_text(
            LanguagesSettings(settings.get_languages_file()).build_file_sample(), encoding="utf-8"
        )
        Console.print(settings.get_languages_file())


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

if __name__ == "__main__":
    app()
