import time

import typer

from tko.config.settings import Settings
from loguru import logger
from tko.i18n import Msg, t
from tko.util.console import Console

app = typer.Typer(help="Audit repository activity")


@app.callback(invoke_without_command=True)
def audit_callback(
    ctx: typer.Context,
    interval: int | None = typer.Option(None, "--interval", "-i", help="Snapshot interval in seconds"),
):
    if ctx.invoked_subcommand is not None:
        return

    from tko.cli.common import load_repo
    from tko.repository.repository_watcher import RepositoryWatcher

    settings: Settings = ctx.obj
    settings.rs.force_offline = True
    repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=True)
    if repo is None:
        return

    interval_seconds = 60
    if interval is not None:
        if interval <= 0:
            raise typer.BadParameter("interval must be greater than zero")
        interval_seconds = interval

    watcher = RepositoryWatcher(repo)
    watcher.start_watching(audit=True, audit_verbose=True, audit_interval_seconds=interval_seconds)
    logger.info(t(Msg(pt="Monitor de auditoria iniciado. Aperte Ctrl+C para finalizar.", 
                      en="Audit watcher started. Press Ctrl+C to stop.")))
    
    Console.print(t(Msg(pt="Abra o tko em outro terminal para fazer as tarefas", 
                        en="Open tko in another terminal to perform tasks")))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        watcher.stop_watching()
        logger.info(t(Msg(pt="Monitor de auditoria parado.", en="Audit watcher stopped.")))


if __name__ == "__main__":
    app()
