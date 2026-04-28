from __future__ import annotations
import sys
import typer
from pathlib import Path
from icecream import ic # type: ignore

from tko.__init__ import __version__
from tko.cli.build import app as build_app
from tko.cli.task import app as task_app
from tko.cli.config import app as config_app
from tko.cli.reset import app as reset_app
from tko.cli.remote import app as remote_app
from tko.cli.collect import app as collect_app
from tko.cli.class_cmd import app as class_app
from tko.cli.main_cmds import register_main_commands

import os
if os.name != "nt":
    import signal
    signal.signal(signal.SIGPIPE, signal.SIG_DFL) # permit using tko in pipelines without showing broken pipe errors

app = typer.Typer(name="tko", help=f"tko {__version__}", no_args_is_help=True)

# Register sub-apps
app.add_typer(build_app, name="build")
app.add_typer(task_app, name="task")
app.add_typer(config_app, name="config")
app.add_typer(reset_app, name="reset")
app.add_typer(remote_app, name="remote")
app.add_typer(collect_app, name="collect")
app.add_typer(class_app, name="class")

# Register main commands directly
register_main_commands(app)

@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    settings: Path = typer.Option(None, "-S", "--settings", help="Global Settings config directory"),
    changedir: Path = typer.Option(Path('.'), "-C", "--changedir", help="Repository directory"),
    width: int = typer.Option(None, "-w", "--width", help="Terminal width"),
    version: bool = typer.Option(False, "-v", "--version", help="Show version and exit"),
    mono: bool = typer.Option(False, "-m", "--mono", help="Disable colors"),
    debug: bool = typer.Option(False, "-D", "--debug", help="Enable debug mode"),
    global_cache: bool = typer.Option(False, "-G", "--global-cache", help="Use global cache for remote URL sources"),
    update: bool = typer.Option(False, "-U", "--update", help="Force update remote URL sources"),
    offline: bool = typer.Option(False, "-O", "--offline", help="Disable any update attempts (Offline mode)")
):
    if version:
        print(f"tko {__version__}")
        raise typer.Exit()
        
    from tko.config.settings import Settings
    from tko.util.raw_terminal import RawTerminal
    from tko.util.text import AnsiColor
    from tko.util.rtext import RenderConfig, RenderMode

    if width is not None:
        RawTerminal.set_terminal_size(width)
        
    sett = Settings(settings)
    sett.load_settings()

    if mono:
        AnsiColor.enabled = False
        RenderConfig.mode = RenderMode.PLAIN
    else:
        AnsiColor.enabled = True

    if debug:
        ic.configureOutput(includeContext=True, outputFunction=print)
        ic.enable()
        ic("Debug mode enabled")
    else:
        ic.disable()
        
    ctx.ensure_object(dict)
    ctx.obj["settings"] = sett
    ctx.obj["changedir"] = changedir
    ctx.obj["width"] = width
    ctx.obj["global_cache"] = global_cache
    ctx.obj["update"] = update
    ctx.obj["offline"] = offline

def main():
    try:
        app()
    except KeyboardInterrupt:
        print("\n\nKeyboard Interrupt")
        sys.exit(1)
    except Warning as w:
        print(w)
        sys.exit(1)

if __name__ == '__main__':
    main()
