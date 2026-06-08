import typer

from tko.config.settings import Settings

app = typer.Typer(help="Configure settings")

@app.command("set", help="Set default configuration values")
def config_set(
    ctx: typer.Context,
    side: bool = typer.Option(False, "--side", help="Set side_by_side diff mode"),
    down: bool = typer.Option(False, "--down", help="Set up_to_down diff mode"),
    editor : None | str = typer.Option(None, "--editor", help="Set editor command"),
    images : None | str = typer.Option(None, "--images", help="Enable images [0|1]"),
    timeout: None | int = typer.Option(None, "--timeout", help="Set timeout in sec")
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
    print(str(settings))

if __name__ == "__main__":
    app()
