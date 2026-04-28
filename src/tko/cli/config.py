import typer
from typing import Optional

app = typer.Typer(help="Configure settings")

@app.command("set", help="Set default configuration values")
def config_set(
    ctx: typer.Context,
    side: bool = typer.Option(False, "--side", help="Set side_by_side diff mode"),
    down: bool = typer.Option(False, "--down", help="Set up_to_down diff mode"),
    editor: Optional[str] = typer.Option(None, "--editor", help="Set editor command"),
    borders: Optional[str] = typer.Option(None, "--borders", help="Enable borders [0|1]"),
    images: Optional[str] = typer.Option(None, "--images", help="Enable images [0|1]"),
    timeout: Optional[int] = typer.Option(None, "--timeout", help="Set timeout in sec")
):
    from tko.cmds.cmd_config import CmdConfig, ConfigParams
    
    settings = ctx.obj.get("settings") if ctx.obj else None
    param = ConfigParams()
    param.side = side
    param.down = down
    param.images = images
    param.editor = editor
    param.borders = borders
    param.timeout = timeout
    
    if settings:
        CmdConfig.execute(settings, param)

@app.command("list", help="List default configuration values")
def config_list(ctx: typer.Context):
    settings = ctx.obj.get("settings") if ctx.obj else None
    if settings:
        print(f"SettingsFile\n- {settings.settings_dir}")
        print(str(settings))

if __name__ == "__main__":
    app()
