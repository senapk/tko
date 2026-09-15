from pathlib import Path
import typer
import json

from tko.collect.collect_single import CollectParams
from tko.config.settings import Settings
from tko.repository.repository_paths import RepositoryPaths
from tko.util.console import Console

app = typer.Typer(help="Collect evaluation data")

@app.command("tasks", help="Collect tasks report from many repositories")
def collect_tasks(
    ctx: typer.Context,
    path: list[str] = typer.Argument(..., help="Paths to repos"),
    csv: str = typer.Option(..., "--csv", help="Output CSV file"),
) -> None:
    from tko.collect.collect_many import CollectMany

    settings: Settings = ctx.obj
    repos = [Path(p) for p in path]

    CollectMany.load_tasks(settings.rs, repos, tasks_path=csv)

@app.command("skills", help="Collect skills report from many repositories")
def collect_skills(
    ctx: typer.Context,
    path: list[str] = typer.Argument(..., help="Paths to repos"),
    csv: str = typer.Option(..., "--csv", help="Output CSV file"),
    source: str = typer.Option(..., "--source", "-s", help="Source target to load quests"),
    language: str = typer.Option(..., "--language", "-l", help="Programming language for skills"),
) -> None:
    from tko.collect.collect_many import CollectMany

    settings: Settings = ctx.obj
    repos = [Path(p) for p in path]
    CollectMany.load_skills(rs=settings.rs, git_dir_list=repos, skills_path=csv, remote_index=source, prog_lang=language)

@app.command("repo", help="Collect data from this repository")
def collect_repo(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Collect as json data"),
    resume: bool = typer.Option(False, "--resume", help="Collect resume"),
    history: bool = typer.Option(False, "--history", help="Collect compacted history"),
    log: bool = typer.Option(False, "--log", help="Collect history log"),
    game: bool = typer.Option(False, "--game", help="Collect game info"),
    daily: bool = typer.Option(False, "--daily", help="Daily graph"),
    width: int = typer.Option(100, "--width", help="Daily graph width"),
    height: int = typer.Option(10, "--height", help="Daily graph height"),
    color: int = typer.Option(1, "--color", min=0, max=1, help="Daily graph color [0|1]")
) -> None:
    from tko.collect.collect_single import CollectSingle
    
    settings: Settings = ctx.obj
    
    if RepositoryPaths.rec_search_for_repo_parents(settings.rs.changedir) is None:
        typer.echo("No TKO repository found", err=True)
        raise typer.Exit(1)
    params = CollectParams()
    params.folder = settings.rs.changedir
    params.width = width
    params.height = height
    params.daily = daily
    params.resume = resume
    params.history = history
    params.game = game
    params.log = log
    params.json_output = json_output
    params.colored = color
    
    data = CollectSingle.collect(settings.rs, params)

    if params.json_output:
        Console.print(json.dumps(data.get_dict(), indent=4, ensure_ascii=False))

if __name__ == "__main__":
    app()
