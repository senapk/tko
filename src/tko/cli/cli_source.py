from __future__ import annotations

from typing import Optional

import typer
from loguru import logger

from tko.cli.common import load_repo
from tko.config.settings import Settings
from tko.i18n import Msg
from tko.repository.source_actions import SourceActions


app = typer.Typer(help="Manage task sources")


_CLI_SOURCE_ADD_ERROR = Msg.parse(
    pt="Erro ao adicionar fonte",
    en="Error adding source",
)
_CLI_SOURCE_UPDATE_ERROR = Msg.parse(
    pt="Erro ao atualizar fonte",
    en="Error updating source",
)


@app.command("list", help="List task sources")
def source_list(ctx: typer.Context):
    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs)
    if repo is None:
        return
    source_actions = SourceActions(settings, repo)
    source_actions.list_sources()


@app.command("rm", help="Remove a task source")
def source_rm(ctx: typer.Context, label: str = typer.Argument(..., help="Source label to remove")):
    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs)
    if repo is None:
        return
    source_actions = SourceActions(settings, repo)
    source_actions.remove_source(label=label)


@app.command("add", help="Add a task source")
def source_add(
    ctx: typer.Context,
    label: str = typer.Argument(..., help="Unique source label"),
    uri: str = typer.Argument(..., help="Source index URI"),
    authoring: bool = typer.Option(False, "--authoring", help="Use this managed source when creating new Labs"),
):
    try:
        settings: Settings = ctx.obj
        repo, _ = load_repo(settings.rs)
        if repo is None:
            return
        source_actions = SourceActions(settings, repo)
        source_actions.add_source(label=label, uri=uri, authoring=authoring)
    except ValueError:
        logger.exception(f"{_CLI_SOURCE_ADD_ERROR}")


@app.command("set", help="Update a task source URI")
def source_set(
    ctx: typer.Context,
    label: str = typer.Argument(..., help="Source label"),
    uri: Optional[str] = typer.Option(None, "--uri", "-u", help="Set a new URI for the source index"),
):
    try:
        settings: Settings = ctx.obj
        repo, _ = load_repo(settings.rs)
        if repo is None:
            return
        source_actions = SourceActions(settings, repo)
        source_actions.update_source(label=label, uri=uri)
    except ValueError:
        logger.exception(f"{_CLI_SOURCE_UPDATE_ERROR}")


@app.command("set-authoring", help="Select the source used when creating new Labs")
def source_set_authoring(
    ctx: typer.Context,
    label: str = typer.Argument(..., help="Managed source label"),
):
    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs)
    if repo is None:
        return
    source_actions = SourceActions(settings, repo)
    source_actions.set_authoring_source(label=label)


if __name__ == "__main__":
    app()
