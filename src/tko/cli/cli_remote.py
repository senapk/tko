from loguru import logger
from typing import Optional

import typer

from tko.cli.common import load_repo
from tko.config.settings import Settings
from tko.i18n import Msg
from tko.repository.remote_actions import RemoteActions


app = typer.Typer(help="Manage remote task sources")


_CLI_REMOTE_ADD_SOURCE_ERROR = Msg(
    pt="Erro ao adicionar fonte",
    en="Error adding source",
)
_CLI_REMOTE_CLEAR_WITH_QUEST_ERROR = Msg(
    pt="Erro: --clear não pode ser usado com --quest",
    en="Error: --clear cannot be used with --quest",
)


@app.command("list", help="List remote task sources")
def remote_list(ctx: typer.Context):
    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs)
    if repo is None:
        return
    rep_actions = RemoteActions(settings, repo)
    rep_actions.remote_list()


@app.command("rm", help="Remove a remote task source")
def remote_rm(ctx: typer.Context, name: str = typer.Argument(..., help="Name of the remote to be removed")):
    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs)
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
        settings: Settings = ctx.obj
        repo, _ = load_repo(settings.rs)
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
            filter_to=to,
            writeable=write,
        )

    except ValueError:
        logger.exception(f"{_CLI_REMOTE_ADD_SOURCE_ERROR}")


@app.command("filter", help="Manage filters for a remote task source")
def remote_filter(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Name of the remote"),
    quest: Optional[list[str]] = typer.Option(None, "--quest", "-q", help="Load all tasks only from selected quests"),
    clear: bool = typer.Option(False, "--clear", help="Clear all filters"),
    to: Optional[str] = typer.Option(None, "--to", "-t", help="Quest destination for filtered tasks added with this source"),
):
    if clear and quest:
        logger.error(f"{_CLI_REMOTE_CLEAR_WITH_QUEST_ERROR}")
        return

    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs)
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
    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs)
    if repo is None:
        return
    rep_actions = RemoteActions(settings, repo)
    rep_actions.remote_set(alias=name, target=target, index=index)


if __name__ == "__main__":
    app()
