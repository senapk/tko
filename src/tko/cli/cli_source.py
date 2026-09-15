from __future__ import annotations

from typing import Optional

import typer

from tko.cli.common import load_repo
from tko.config.settings import Settings
from tko.repository.source_actions import SourceActions


app = typer.Typer(help="Manage task sources")


@app.command("list", help="List task sources")
def source_list(ctx: typer.Context) -> None:
    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs)
    if repo is None:
        raise typer.Exit(1)
    source_actions = SourceActions(settings, repo)
    source_actions.list_sources()


@app.command("remove", help="Remove a task source")
def source_remove(ctx: typer.Context, label: str = typer.Argument(..., help="Source label to remove")) -> None:
    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs)
    if repo is None:
        raise typer.Exit(1)
    source_actions = SourceActions(settings, repo)
    if not source_actions.remove_source(label=label):
        raise typer.Exit(1)


@app.command("add", help="Add a task source")
def source_add(
    ctx: typer.Context,
    label: str = typer.Argument(..., help="Unique source label"),
    uri: str = typer.Argument(..., help="Source index URI"),
    authoring: bool = typer.Option(False, "--authoring", help="Use this managed source when creating new Labs"),
) -> None:
    try:
        settings: Settings = ctx.obj
        repo, _ = load_repo(settings.rs)
        if repo is None:
            raise typer.Exit(1)
        source_actions = SourceActions(settings, repo)
        if not source_actions.add_source(label=label, uri=uri, authoring=authoring):
            raise typer.Exit(1)
    except (ValueError, Warning) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


@app.command("set", help="Update a source URI or select it for authoring")
def source_set(
    ctx: typer.Context,
    label: str = typer.Argument(..., help="Source label"),
    uri: Optional[str] = typer.Option(None, "--uri", "-u", help="Set a new URI for the source index"),
    authoring: bool = typer.Option(False, "--authoring", help="Use this source when creating new Labs"),
) -> None:
    if uri is None and not authoring:
        raise typer.BadParameter("Specify --uri or --authoring")
    try:
        settings: Settings = ctx.obj
        repo, _ = load_repo(settings.rs)
        if repo is None:
            raise typer.Exit(1)
        source_actions = SourceActions(settings, repo)
        if not source_actions.update_source(label=label, uri=uri, authoring=authoring):
            raise typer.Exit(1)
    except (ValueError, Warning) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


if __name__ == "__main__":
    app()
