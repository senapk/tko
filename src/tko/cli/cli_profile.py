from __future__ import annotations

from datetime import datetime, timedelta

import typer

from tko.cli.common import load_repo
from tko.config.settings import Settings
from tko.i18n import Msg
from tko.repository.linked_profile import LinkedProfileService
from tko.repository.repository_config import RepositoryLoader
from tko.util.console import Console


app = typer.Typer(help="Manage linked profile")

_PROFILE_NOT_LINKED = Msg.text(pt="Workspace não vinculado", en="Workspace is not linked")
_PROFILE_LINKED = Msg.text(pt="Perfil vinculado: {uri}", en="Linked profile: {uri}")
_PROFILE_UPDATED = Msg.text(pt="Perfil atualizado", en="Profile updated")
_PROFILE_UNLINKED = Msg.text(pt="Perfil desvinculado", en="Profile unlinked")
_PROFILE_STATUS = Msg.text(
    pt="Profile: {name}\nURI: {uri}\nRevision: {revision}\nLast update: {updated_at}\nNext check: {next_check}\nStatus: {status}",
    en="Profile: {name}\nURI: {uri}\nRevision: {revision}\nLast update: {updated_at}\nNext check: {next_check}\nStatus: {status}",
)


@app.command("link", help="Link this workspace to a profile URI")
def profile_link(ctx: typer.Context, uri: str = typer.Argument(..., help="Profile URI")):
    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs)
    if repo is None:
        return
    loaded = LinkedProfileService(repo).load(uri, force_git_update=True)
    LinkedProfileService(repo).apply_loaded(loaded)
    RepositoryLoader(repo).save(force=True)
    Console.print(_PROFILE_LINKED.t().format(uri=loaded.link.uri))


@app.command("status", help="Show linked profile status")
def profile_status(ctx: typer.Context):
    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs)
    if repo is None:
        return
    link = repo.data.link
    if link is None:
        Console.print(_PROFILE_NOT_LINKED.t())
        return
    updated = _parse_time(link.updated_at)
    next_check = ""
    if updated is not None:
        next_check = (updated + timedelta(minutes=link.refresh_minutes)).strftime("%Y-%m-%d %H:%M")
    Console.print(
        _PROFILE_STATUS.t().format(
            name=repo.data.profile_name or "(unnamed)",
            uri=link.uri,
            revision=link.revision or link.content_hash or "",
            updated_at=updated.strftime("%Y-%m-%d %H:%M") if updated is not None else link.updated_at,
            next_check=next_check,
            status="linked",
        )
    )


@app.command("update", help="Force linked profile update")
def profile_update(ctx: typer.Context):
    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs)
    if repo is None:
        return
    if not repo.data.is_linked:
        Console.print(_PROFILE_NOT_LINKED.t())
        return
    if LinkedProfileService(repo).refresh_if_due(force=True):
        RepositoryLoader(repo).save(force=True)
    Console.print(_PROFILE_UPDATED.t())


@app.command("unlink", help="Keep current profile locally and remove profile link")
def profile_unlink(ctx: typer.Context):
    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs)
    if repo is None:
        return
    if repo.data.link is None:
        Console.print(_PROFILE_NOT_LINKED.t())
        return
    repo.data.link = None
    RepositoryLoader(repo).save(force=True)
    Console.print(_PROFILE_UNLINKED.t())


def _parse_time(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
