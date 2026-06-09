import typer

from tko.config.settings import Settings
from tko.i18n import Msg, t

app = typer.Typer(help="Configure settings")

_CONFIG_AUDIT_ENABLED = Msg(
    pt="Auditoria do repositório: ON",
    en="Repository audit: ON",
)
_CONFIG_AUDIT_DISABLED = Msg(
    pt="Auditoria do repositório: OFF",
    en="Repository audit: OFF",
)

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


@app.command("audit", help="Enable or disable repository audit mode")
def config_audit(
    ctx: typer.Context,
    on: bool = typer.Option(False, "--on", help="Enable repository audit mode"),
    off: bool = typer.Option(False, "--off", help="Disable repository audit mode"),
):
    if on and off:
        raise typer.BadParameter("Use only one option: --on or --off")

    from tko.cli.common import load_repo
    from tko.repository.repository_config import RepositoryConfig

    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=False)
    if repo is None:
        return

    repo_config = RepositoryConfig(repo).load()

    if on:
        repo.data.audit.enabled = True
        repo_config.save(force=True)
        print(t(_CONFIG_AUDIT_ENABLED))
        return

    if off:
        repo.data.audit.enabled = False
        repo_config.save(force=True)
        print(t(_CONFIG_AUDIT_DISABLED))
        return

    if repo.data.audit.enabled:
        print(t(_CONFIG_AUDIT_ENABLED))
    else:
        print(t(_CONFIG_AUDIT_DISABLED))

if __name__ == "__main__":
    app()
