from __future__ import annotations
from typing import Literal

from tko.logger.loguru_settings import configure_loguru
    
import sys
import os
from pathlib import Path
import typer
from icecream import ic  # type: ignore

from tko.__init__ import __version__
from tko.cli.cli_audit import app as audit_app
from tko.cli.cli_collect import app as collect_app
from tko.cli.cli_config import app as config_app
from tko.cli.cli_main import register_main_commands
from tko.cli.cli_task import app as task_app
from tko.cli.cli_index import app as index_app
from tko.cli.cli_tools import app as tool_app
from tko.i18n import Msg, set_language
from tko.util.Renderer import RenderMode
from tko.util.console import Console


_APP_KEYBOARD_INTERRUPT = Msg.parse(
    pt="Interrupção de teclado",
    en="Keyboard Interrupt",
)

if os.name != "nt":
    import signal

    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

app = typer.Typer(name="tko", help=f"tko {__version__}", no_args_is_help=True, context_settings={"help_option_names": ["-h", "--help"]})


app.add_typer(audit_app, name="audit")
app.add_typer(task_app, name="task")
app.add_typer(index_app, name="index")
app.add_typer(config_app, name="config")
app.add_typer(collect_app, name="collect")
app.add_typer(tool_app, name="tool")

register_main_commands(app)


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    settings: Path | None = typer.Option(None, "-S", "--settings", help="Global Settings config directory"),
    changedir: Path = typer.Option(Path("."), "-C", "--changedir", help="Working directory for commands and relative paths"),
    width: int | None = typer.Option(None, "-w", "--width", help="Terminal width"),
    ui_language: Literal["pt", "en"] | None = typer.Option(None, "--ui-language", help="Interface language"),
    version: bool = typer.Option(False, "-v", "--version", help="Show version and exit"),
    mono: bool = typer.Option(False, "-m", "--mono", help="Disable colors"),
    debug: bool = typer.Option(False, "-D", "--debug", help="Enable debug mode"),
    update: bool = typer.Option(False, "-U", "--update", help="Force update external URL sources"),
    offline: bool = typer.Option(False, "-O", "--offline", help="Disable any update attempts (Offline mode)"),
) -> None:
    from tko.config.settings import Settings
    from tko.util.raw_terminal import RawTerminal
    from tko.util.console import PrintWriter

    if version:
        Console.print("tko {version}".format(version=__version__))
        raise typer.Exit()

    if width is not None:
        RawTerminal.set_terminal_size(width)

    original_dir: Path = Path.cwd()
    settings_dir: Path | None = settings.resolve() if settings is not None else None
    effective_dir: Path = changedir.resolve()
    if not effective_dir.is_dir():
        raise typer.BadParameter(f"Directory not found: {changedir}", param_hint="--changedir")
    os.chdir(effective_dir)
    ctx.call_on_close(lambda: os.chdir(original_dir))
    sett: Settings = Settings(settings_dir)
    sett.get_settings_dir().mkdir(parents=True, exist_ok=True)
    sett.load_settings()
    sett.rs.changedir = effective_dir
    sett.rs.debug_mode = debug
    sett.rs.force_update = update
    sett.rs.force_offline = offline
    sett.rs.width = width
    sett.rs.monochrome = mono

    if ui_language is not None:
        sett.app.ui_language = ui_language
        sett.save_settings()
    set_language(sett.app.ui_language)

    if mono:
        Console.stdout = PrintWriter(sys.stdout, RenderMode.PLAIN)
        Console.stderr = PrintWriter(sys.stderr, RenderMode.PLAIN)

    configure_loguru(sett.get_log_file(), debug)
    
    ctx.obj = sett


def main() -> None:
    from tko.repository.task_data_format import MigrationRequiredError

    try:
        app()
    except MigrationRequiredError as exc:
        Console.print(str(exc))
        sys.exit(1)
    except KeyboardInterrupt:
        Console.print(f"\n\n{_APP_KEYBOARD_INTERRUPT}")
        sys.exit(1)
    # except Warning as w:
    #     logger.warning("%s", w)
    #     sys.exit(1)


if __name__ == "__main__":
    main()
