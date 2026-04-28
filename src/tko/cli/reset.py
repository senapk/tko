import typer

app = typer.Typer(help="Reset configuration")

@app.command("cache", help="Clear configuration cache")
def reset_cache(ctx: typer.Context):
    from tko.cli.common import load_repo
    
    changedir = ctx.obj.get("changedir") if ctx.obj else None
    repo, _ = load_repo(changedir)
    if repo is None:
        print("Nenhum repositório TKO encontrado.")
        return
    repo.git_cache.clear_cache()

@app.command("global", help="Reset global configuration to factory default")
def reset_global(ctx: typer.Context):
    settings = ctx.obj.get("settings")
    if settings:
        sp = settings.reset().save_settings()
        print(sp.get_settings_file())

@app.command("languages", help="Reset languages configuration to factory default")
def reset_languages(ctx: typer.Context):
    settings = ctx.obj.get("settings")
    if settings:
        settings.get_languages_settings().reset().save_file_settings()
        print(settings.get_languages_file())

if __name__ == "__main__":
    app()
