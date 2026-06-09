import typer
from tko.i18n import Msg, t
from tko.config.settings import Settings


_RESET_NO_REPO = Msg(
    pt="Nenhum repositório TKO encontrado.",
    en="No TKO repository found.",
)

app = typer.Typer(help="Reset configuration")

@app.command("cache", help="Clear configuration cache")
def reset_cache(ctx: typer.Context):
    from tko.cli.common import load_repo
    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs, auto_load=False)
    if repo is None:
        print(t(_RESET_NO_REPO))
        return
    repo.git_cache.clear_cache()

@app.command("global", help="Reset global configuration to factory default")
def reset_global(ctx: typer.Context):
    settings: Settings = ctx.obj    
    sp = settings.reset().save_settings()
    print(sp.get_settings_file())

if __name__ == "__main__":
    app()
