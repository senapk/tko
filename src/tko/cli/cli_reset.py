import typer
from tko.config.user_data import UserData
from tko.i18n import Msg
from tko.config.settings import Settings
from tko.repository.git_cache import GitCache
from tko.util.console import Console


_RESET_NO_REPO = Msg(
    pt="Nenhum repositório TKO encontrado.",
    en="No TKO repository found.",
)

app = typer.Typer(help="Reset configuration")

@app.command("cache", help="Clear configuration cache")
def reset_cache(ctx: typer.Context):
    settings: Settings = ctx.obj    
    git_cache = GitCache(cache_dir=UserData.global_cache_dir(), update_mode=settings.rs.update_mode)
    git_cache.clear_cache()

@app.command("global", help="Reset global configuration to factory default")
def reset_global(ctx: typer.Context):
    settings: Settings = ctx.obj    
    sp = settings.reset().save_settings()
    Console.print(sp.get_settings_file())

if __name__ == "__main__":
    app()
