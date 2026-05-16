import logging
from typing import Optional

import typer

from tko.app_context import AppContext
from tko.cli.common import load_repo
from tko.repository.remote_actions import RemoteActions


app = typer.Typer(help="Manage remote task sources")
logger = logging.getLogger(__name__)


@app.command("list", help="List remote task sources")
def remote_list(ctx: typer.Context):
    app_ctx: AppContext = AppContext.load_from_context(ctx)
    settings = app_ctx.settings
    repo, _, _ = load_repo(app_ctx.changedir)
    if repo is None:
        return
    rep_actions = RemoteActions(settings, repo)
    rep_actions.remote_list()


@app.command("rm", help="Remove a remote task source")
def remote_rm(ctx: typer.Context, name: str = typer.Argument(..., help="Name of the remote to be removed")):
    app_ctx: AppContext = AppContext.load_from_context(ctx)
    settings = app_ctx.settings
    repo, _, _ = load_repo(app_ctx.changedir)
    if repo is None:
        return
    rep_actions = RemoteActions(settings, repo)
    rep_actions.remote_rm(alias=name)


@app.command("add", help="Add a new task source")
def remote_add(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Name of the remote"),
    target: str = typer.Argument(..., help="Remote source: git URL, local directory or preset name"),
    quest: Optional[list[str]] = typer.Option(None, "--quest", "-q", help="Load all tasks only from selected quests"),
    to: Optional[str] = typer.Option(None, "--to", "-t", help="Quest destination for filtered tasks added with this source"),
    setup: Optional[str] = typer.Option(None, "--setup", "-s", help="SETUP JSON string to configure the remote source"),
    index: Optional[str] = typer.Option(None, "--index", "-i", help="Set a custom index relative do repo dir, default is README.md"),
    branch: str = typer.Option("main", "--branch", "-b", help="Branch name for git remote sources"),
    write: bool = typer.Option(False, "--write", "-w", help="Allow modifications for local directory remotes (default: readonly)"),
):
    default_git_alias = target[1:] if target.startswith("@") else None
    git_repository_url = target if target.startswith(("http:", "https:", "ssh:")) else None
    local_source_dir = target if not (default_git_alias or git_repository_url) else None

    try:
        app_ctx: AppContext = AppContext.load_from_context(ctx)
        settings = app_ctx.settings
        repo, _, _ = load_repo(app_ctx.changedir)
        if repo is None:
            return
        rep_actions = RemoteActions(settings, repo)
        rep_actions.remote_add(
            name=name,
            remote_default=default_git_alias,
            branch=branch,
            remote_url=git_repository_url,
            remote_dir=local_source_dir,
            index=index,
            filter_quest=quest,
            filter_task=None,
            filter_to=to,
            writeable=write,
        )
        rep_actions.print_end_msg()
    except ValueError:
        logger.exception("Erro ao adicionar fonte")


@app.command("filter", help="Manage filters for a remote task source")
def remote_filter(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Name of the remote"),
    quest: Optional[list[str]] = typer.Option(None, "--quest", "-q", help="Load all tasks only from selected quests"),
    setup: Optional[str] = typer.Option(None, "--setup", "-s", help="SETUP JSON string to configure the remote source"),
    clear: bool = typer.Option(False, "--clear", help="Clear all filters"),
    to: Optional[str] = typer.Option(None, "--to", "-t", help="Quest destination for filtered tasks added with this source"),
):
    if clear and quest:
        logger.error("Erro: --clear não pode ser usado com --quest")
        return

    app_ctx: AppContext = AppContext.load_from_context(ctx)
    settings = app_ctx.settings
    changedir = app_ctx.changedir
    repo, _, _ = load_repo(changedir)
    if repo is None:
        return
    rep_actions = RemoteActions(settings, repo)
    rep_actions.remote_filter(alias=name, filter_quest=quest, clear=clear, filter_to=to)


@app.command("set", help="Manage filters for a remote task source")
def remote_set(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Name of the remote"),
    target: Optional[str] = typer.Option(None, "--target", "-t", help="Set a new target for the remote source"),
    index: Optional[str] = typer.Option(None, "--index", "-i", help="Set a new index for the remote source"),
):
    app_ctx: AppContext = AppContext.load_from_context(ctx)
    settings = app_ctx.settings
    changedir = app_ctx.changedir
    repo, _, _ = load_repo(changedir)
    if repo is None:
        return
    rep_actions = RemoteActions(settings, repo)
    rep_actions.remote_set(alias=name, target=target, index=index)


if __name__ == "__main__":
    app()
