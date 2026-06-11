import typer
import json

from tko.collect.collect_single import CollectParams
from tko.config.settings import Settings
from tko.util.console import Console

app = typer.Typer(help="Collect evaluation data")

@app.command("task", help="Collect data from task")
def collect_task(
    ctx: typer.Context,
    label: str = typer.Argument(..., help="Task label"),
    graph: tuple[int, int] = typer.Argument(..., help="Show task graph (WIDTH HEIGHT)")
):
    from tko.cli.common import load_repo
    from tko.cmds.cmd_task import CmdTask
    
    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs)
    if repo is None:
        return
        
    width, height = graph
    CmdTask.show_graph(settings, repo, label, width, height)

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
    color: int = typer.Option(1, "--color", help="Daily graph color [0|1]")
):
    from tko.collect.collect_single import CollectSingle
    
    settings: Settings = ctx.obj
    
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
