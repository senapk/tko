from loguru import logger
from typing import Optional

import typer

from tko.cli.common import load_repo
from tko.config.settings import Settings
from tko.i18n import Msg
from tko.repository.remote_actions import RemoteActions


app = typer.Typer(help="Manage remote task sources")


_CLI_REMOTE_ADD_SOURCE_ERROR = Msg.parse(
    pt="Erro ao adicionar fonte",
    en="Error adding source",
)
_CLI_REMOTE_CLEAR_WITH_QUEST_ERROR = Msg.parse(
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


@app.command("add", help="Add a new remote task source")
def remote_add(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Name of the remote"),
    target: str = typer.Argument(..., help="Remote source: git blob URL to file, local file or preset name"),
    write: bool = typer.Option(False, "--write", "-w", help="Allow modifications for local directory remotes (default: readonly)"),
):
    try:
        settings: Settings = ctx.obj
        repo, _ = load_repo(settings.rs)
        if repo is None:
            return
        rep_actions = RemoteActions(settings, repo)
        rep_actions.remote_add(
            name=name,
            target=target,
            writeable=write,
        )

    except ValueError:
        logger.exception(f"{_CLI_REMOTE_ADD_SOURCE_ERROR}")


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
    rep_actions.remote_set(alias=name, target=target)


if __name__ == "__main__":
    app()
