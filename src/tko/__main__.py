from __future__ import annotations

from loguru import logger
from tko.logger.loguru_settings import configure_loguru
    
import sys
import os
from pathlib import Path
import typer
from icecream import ic  # type: ignore

from tko.__init__ import __version__
from tko.cli.cli_build import app as build_app
from tko.cli.cli_class import app as class_app
from tko.cli.cli_collect import app as collect_app
from tko.cli.cli_config import app as config_app
from tko.cli.cli_main import register_main_commands
from tko.cli.cli_remote import app as remote_app
from tko.cli.cli_reset import app as reset_app
from tko.cli.cli_task import app as task_app
from tko.cli.cli_tool import app as tool_app
from tko.i18n import Msg, set_language, t


_APP_VERSION = Msg(
    pt="tko {version}",
    en="tko {version}",
)
_APP_KEYBOARD_INTERRUPT = Msg(
    pt="Interrupção de teclado",
    en="Keyboard Interrupt",
)

if os.name != "nt":
    import signal

    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

app = typer.Typer(name="tko", help=f"tko {__version__}", no_args_is_help=True, context_settings={"help_option_names": ["-h", "--help"]})


app.add_typer(build_app, name="build")
app.add_typer(task_app, name="task")
app.add_typer(config_app, name="config")
app.add_typer(reset_app, name="reset")
app.add_typer(remote_app, name="remote")
app.add_typer(collect_app, name="collect")
app.add_typer(class_app, name="class")
app.add_typer(tool_app, name="tool")

register_main_commands(app)


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    settings: Path = typer.Option(None, "-S", "--settings", help="Global Settings config directory"),
    changedir: Path = typer.Option(Path("."), "-C", "--changedir", help="Repository directory"),
    width: int | None = typer.Option(None, "-w", "--width", help="Terminal width"),
    lang: str | None = typer.Option(None, "--lang", help="Interface language (pt-BR or en)"),
    version: bool = typer.Option(False, "-v", "--version", help="Show version and exit"),
    mono: bool = typer.Option(False, "-m", "--mono", help="Disable colors"),
    debug: bool = typer.Option(False, "-D", "--debug", help="Enable debug mode"),
    local_cache: bool = typer.Option(False, "-L", "--local-cache", help="Use local cache for remote URL sources"),
    update: bool = typer.Option(False, "-U", "--update", help="Force update remote URL sources"),
    offline: bool = typer.Option(False, "-O", "--offline", help="Disable any update attempts (Offline mode)"),
):
    from tko.config.settings import Settings
    from tko.util.raw_terminal import RawTerminal
    from tko.util.rt import RenderConfig, RenderMode

    if version:
        print(t(_APP_VERSION, version=__version__))
        raise typer.Exit()

    if width is not None:
        RawTerminal.set_terminal_size(width)

    sett = Settings(settings)
    sett.load_settings()
    sett.rs.debug_mode = debug
    sett.rs.local_cache = local_cache
    sett.rs.force_update = update
    sett.rs.force_offline = offline
    sett.rs.width = width

    if lang is not None:
        sett.app.ui_language = lang
        sett.save_settings()
    set_language(sett.app.ui_language)

    if mono:
        RenderConfig.mode = RenderMode.PLAIN

    configure_loguru(sett.get_log_file())
    
    if debug:
        ic.configureOutput(includeContext=True, outputFunction=print)
        logger.level("DEBUG")
    else:
        ic.disable()

    ctx.obj = sett


def main():
    try:
        app()
    except KeyboardInterrupt:
        print(f"\n\n{t(_APP_KEYBOARD_INTERRUPT)}")
        sys.exit(1)
    except Warning as w:
        logger.warning("%s", w)
        sys.exit(1)


if __name__ == "__main__":
    main()
