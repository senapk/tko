from __future__ import annotations

import typer

from tko.config.settings import Settings
from tko.i18n import Msg
from tko.util.console import Console

app = typer.Typer(help="Manage repository audit configuration", no_args_is_help=True)


@app.command("on", help="Enable persistent audit in the repository")
def audit_on(
    ctx: typer.Context,
    interval: int | None = typer.Option(None, "--interval", "-i", min=1, help="Audit interval in seconds"),
) -> None:
    from tko.cli.common import load_repo
    from tko.repository.repository_config import RepositoryLoader

    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=True)
    if repo is None:
        return
    repo.audit.enabled = True
    if interval is not None:
        repo.audit.interval_seconds = interval
    RepositoryLoader(repo).save()
    Console.print(Msg.parse(pt="Auditoria persistente habilitada", en="Persistent audit enabled").t())


@app.command("off", help="Disable persistent audit in the repository")
def audit_off(ctx: typer.Context) -> None:
    from tko.cli.common import load_repo
    from tko.repository.repository_config import RepositoryLoader

    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=True)
    if repo is None:
        return
    repo.audit.enabled = False
    repo.audit.interval_seconds = None
    RepositoryLoader(repo).save()
    Console.print(Msg.parse(pt="Auditoria persistente desabilitada", en="Persistent audit disabled").t())


@app.command("status", help="Show persistent audit configuration")
def audit_status(ctx: typer.Context) -> None:
    from tko.cli.common import load_repo

    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=True)
    if repo is None:
        return
    enabled = Msg.parse(pt="habilitada", en="enabled") if repo.audit.enabled else Msg.parse(pt="desabilitada", en="disabled")
    interval = repo.audit.interval_seconds
    status = Msg.parse(pt="Auditoria persistente: {status}", en="Persistent audit: {status}").t().format(status=enabled)
    if interval is not None:
        status += f" ({interval}s)"
    Console.print(status)
