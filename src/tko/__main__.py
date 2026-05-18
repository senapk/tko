from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import typer
from icecream import ic  # type: ignore

from tko.__init__ import __version__
from tko.app_context import AppContext
from tko.cli.build import app as build_app
from tko.cli.class_cmd import app as class_app
from tko.cli.collect import app as collect_app
from tko.cli.config import app as config_app
from tko.cli.main_cmds import register_main_commands
from tko.cli.remote_cli import app as remote_app
from tko.cli.reset import app as reset_app
from tko.cli.task_cli import app as task_app
from tko.cli.tool import app as tool_app
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
logger = logging.getLogger(__name__)

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
    global_cache: bool = typer.Option(False, "-G", "--global-cache", help="Use global cache for remote URL sources"),
    update: bool = typer.Option(False, "-U", "--update", help="Force update remote URL sources"),
    offline: bool = typer.Option(False, "-O", "--offline", help="Disable any update attempts (Offline mode)"),
):
    from tko.config.settings import Settings
    from tko.util.raw_terminal import RawTerminal
    from tko.util.rtext import RenderConfig, RenderMode

    if version:
        print(t(_APP_VERSION, version=__version__))
        raise typer.Exit()

    if width is not None:
        RawTerminal.set_terminal_size(width)

    sett = Settings(settings)
    sett.load_settings()
    if lang is not None:
        sett.app.ui_language = lang
        sett.save_settings()
    set_language(sett.app.ui_language)

    if mono:
        RenderConfig.mode = RenderMode.PLAIN

    if debug:
        ic.configureOutput(includeContext=True, outputFunction=print)
        ic.enable()
        ic("Debug mode enabled")
    else:
        ic.disable()

    ctx.ensure_object(dict)
    ctx.obj = AppContext(
        settings=sett,
        changedir=changedir,
        width=width,
        global_cache=global_cache,
        update=update,
        offline=offline,
    )


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
