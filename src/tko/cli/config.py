import typer
from tko.app_context import AppContext
from tko.i18n import Msg, t


_CLI_CONFIG_SETTINGS_FILE = Msg(
    pt="SettingsFile\n- {settings_dir}",
    en="SettingsFile\n- {settings_dir}",
)

app = typer.Typer(help="Configure settings")

@app.command("set", help="Set default configuration values")
def config_set(
    ctx: typer.Context,
    side: bool = typer.Option(False, "--side", help="Set side_by_side diff mode"),
    down: bool = typer.Option(False, "--down", help="Set up_to_down diff mode"),
    editor : None | str = typer.Option(None, "--editor", help="Set editor command"),
    borders: None | str = typer.Option(None, "--borders", help="Enable borders [0|1]"),
    images : None | str = typer.Option(None, "--images", help="Enable images [0|1]"),
    timeout: None | int = typer.Option(None, "--timeout", help="Set timeout in sec")
):
    from tko.cmds.cmd_config import CmdConfig, ConfigParams
    app_ctx: AppContext = AppContext.load_from_context(ctx)
    settings = app_ctx.settings
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
    app_ctx: AppContext = AppContext.load_from_context(ctx)
    settings = app_ctx.settings
    print(t(_CLI_CONFIG_SETTINGS_FILE, settings_dir=settings.settings_dir))
    print(str(settings))

if __name__ == "__main__":
    app()
