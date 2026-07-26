import typer

from tko.cli.common import load_repo
from tko.config.settings import Settings
from tko.repository.repository import Repository
from tko.repository.repository_config import RepositoryLoader
from tko.util.console import Console
from tko.util.rt import RT

app = typer.Typer(help="Configure settings")

@app.command("set", help="Set default configuration values")
def config_set(
    ctx: typer.Context,
    side: bool = typer.Option(False, "--side", help="Set side_by_side diff mode"),
    down: bool = typer.Option(False, "--down", help="Set up_to_down diff mode"),
    editor : None | str = typer.Option(None, "--editor", help="Set editor command"),
    images : None | str = typer.Option(None, "--images", help="Enable images [0|1]"),
    timeout: None | int = typer.Option(None, "--timeout", help="Set timeout in sec"),
):
    from tko.cmds.cmd_config import CmdConfig, ConfigParams
    settings: Settings = ctx.obj
    param = ConfigParams()
    param.side = side
    param.down = down
    param.images = images
    param.editor = editor
    param.timeout = timeout

    if settings:
        CmdConfig.execute(settings, param)

@app.command("list", help="List default configuration values")
def config_list(ctx: typer.Context):
    settings: Settings = ctx.obj
    Console.print(RT.parse(str(settings)))


@app.command("sandbox", help="Set default configuration values")
def config_sandbox(
    ctx: typer.Context,
    dir : None | str = typer.Option(None, "--dir", help="Set sandbox directory"),
    index : None | str = typer.Option(None, "--index", help="Set sandbox index file"),
):
    settings: Settings = ctx.obj
    settings.rs.force_offline = True
    repo: Repository | None = None
    repo, _ = load_repo(settings.rs, auto_load=False)
    if repo is None:
        Console.print(RT.parse("No repository loaded."))
        return
    if dir is not None:
        Console.print(RT.parse(f"Sandbox directory set to: {dir}"))
        repo.data.sandbox_dir = dir
    if index is not None:
        repo.data.sandbox_index_file = index
        Console.print(RT.parse(f"Sandbox index set to: {index}"))
    if dir is not None or index is not None:
        RepositoryLoader(repo).save()


if __name__ == "__main__":
    app()
