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
completion_app = typer.Typer(help="Manage shell completion", no_args_is_help=True)
app.add_typer(completion_app, name="completion")


ShellName = Literal["bash", "zsh", "fish", "powershell", "pwsh"]
_SUPPORTED_SHELLS: dict[str, ShellName] = {
    "bash": "bash",
    "zsh": "zsh",
    "fish": "fish",
    "powershell": "powershell",
    "pwsh": "pwsh",
}


def _completion_context(shell: ShellName | None) -> tuple[str, str, str]:
    import shellingham

    prog_name: str = "tko"
    complete_var: str = f"_{prog_name.replace('-', '_').upper()}_COMPLETE"
    if shell is None:
        try:
            detected_shell: str
            detected_shell, _shell_path = shellingham.detect_shell()
        except shellingham.ShellDetectionFailure:
            typer.echo("Não foi possível detectar o shell. Informe --shell.", err=True)
            raise typer.Exit(1)
        shell = _SUPPORTED_SHELLS.get(detected_shell)
        if shell is None:
            typer.echo(f"Shell não suportado: {detected_shell}. Informe --shell.", err=True)
            raise typer.Exit(1)
    return prog_name, complete_var, shell


@completion_app.command("install", help="Install shell completion")
def completion_install(
    shell: ShellName | None = typer.Option(None, "--shell", help="Shell to configure"),
) -> None:
    from typer.completion import install

    prog_name, complete_var, selected_shell = _completion_context(shell)
    installed_shell, path = install(
        shell=selected_shell,
        prog_name=prog_name,
        complete_var=complete_var,
    )
    typer.secho(f"{installed_shell} completion installed in {path}", fg="green")
    typer.echo("Completion will take effect once you restart the terminal")


@completion_app.command("show", help="Show the shell completion script")
def completion_show(
    shell: ShellName | None = typer.Option(None, "--shell", help="Shell to generate for"),
) -> None:
    from typer.completion import get_completion_script

    prog_name, complete_var, selected_shell = _completion_context(shell)
    typer.echo(
        get_completion_script(
            prog_name=prog_name,
            complete_var=complete_var,
            shell=selected_shell,
        )
    )


@completion_app.command("uninstall", help="Remove shell completion")
def completion_uninstall(
    shell: ShellName | None = typer.Option(None, "--shell", help="Shell to clean up"),
) -> None:
    _prog_name, _complete_var, selected_shell = _completion_context(shell)
    home: Path = Path.home()

    if selected_shell == "bash":
        completion_path: Path = home / ".bash_completions" / "tko.sh"
        rc_path: Path = home / ".bashrc"
        source_line: str = f"source '{completion_path}'"
        if rc_path.is_file():
            lines: list[str] = rc_path.read_text(encoding="utf-8").splitlines(keepends=True)
            filtered_lines: list[str] = [line for line in lines if line.rstrip("\r\n") != source_line]
            if filtered_lines != lines:
                rc_path.write_text("".join(filtered_lines), encoding="utf-8")
    elif selected_shell == "zsh":
        completion_path = home / ".zfunc" / "_tko"
    elif selected_shell == "fish":
        completion_path = home / ".config" / "fish" / "completions" / "tko.fish"
    else:
        executable: str = selected_shell
        try:
            result: subprocess.CompletedProcess[str] = subprocess.run(
                [executable, "-NoProfile", "-Command", "echo", "$profile"],
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as error:
            typer.echo(f"Não foi possível localizar o perfil do PowerShell: {error}", err=True)
            raise typer.Exit(1) from error
        completion_path = Path(result.stdout.strip())
        from typer.completion import get_completion_script

        script: str = get_completion_script(
            prog_name="tko",
            complete_var="_TKO_COMPLETE",
            shell=selected_shell,
        )
        if completion_path.is_file():
            profile_content: str = completion_path.read_text(encoding="utf-8")
            installed_block: str = f"{script}\n"
            updated_content: str = profile_content.replace(installed_block, "", 1)
            if updated_content != profile_content:
                completion_path.write_text(updated_content, encoding="utf-8")

        typer.echo(f"PowerShell completion removed from {completion_path}")
        return

    existed: bool = completion_path.is_file()
    completion_path.unlink(missing_ok=True)
    if existed:
        typer.echo(f"{selected_shell} completion removed from {completion_path}")
    else:
        typer.echo(f"No {selected_shell} completion found at {completion_path}")


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
