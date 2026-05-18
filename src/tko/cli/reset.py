import typer

from tko.app_context import AppContext
from tko.i18n import Msg, t


_RESET_NO_REPO = Msg(
    pt="Nenhum repositório TKO encontrado.",
    en="No TKO repository found.",
)

app = typer.Typer(help="Reset configuration")

@app.command("cache", help="Clear configuration cache")
def reset_cache(ctx: typer.Context):
    from tko.cli.common import load_repo
    app_ctx: AppContext = AppContext.load_from_context(ctx)
    changedir = app_ctx.changedir
    repo, _, _ = load_repo(changedir)
    if repo is None:
        print(t(_RESET_NO_REPO))
        return
    repo.git_cache.clear_cache()

@app.command("global", help="Reset global configuration to factory default")
def reset_global(ctx: typer.Context):
    app_ctx: AppContext = AppContext.load_from_context(ctx)
    settings = app_ctx.settings
    sp = settings.reset().save_settings()
    print(sp.get_settings_file())

@app.command("languages", help="Reset languages configuration to factory default")
def reset_languages(ctx: typer.Context):
    app_ctx: AppContext = AppContext.load_from_context(ctx)
    settings = app_ctx.settings
    settings.get_languages_settings().reset().save_file_settings()
    print(settings.get_languages_file())

if __name__ == "__main__":
    app()
