import typer
from typing import Optional
from pathlib import Path
import json

app = typer.Typer(help="Collect evaluation data")

@app.command("task", help="Collect data from task")
def collect_task(
    ctx: typer.Context,
    label: str = typer.Argument(..., help="Task label"),
    graph: tuple[int, int] = typer.Argument(..., help="Show task graph (WIDTH HEIGHT)")
):
    from tko.cli.common import load_repo
    from tko.cmds.cmd_task import CmdTask
    
    settings = ctx.obj.get("settings")
    changedir = ctx.obj.get("changedir")
    repo, _ = load_repo(changedir, force_update=False)
    if repo is None:
        return
        
    width, height = graph
    CmdTask.show_graph(settings, repo, label, width, height)

@app.command("repo", help="Collect data from this repository")
def collect_repo(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Collect as json data"),
    resume: bool = typer.Option(False, "--resume", help="Collect resume"),
    log: bool = typer.Option(False, "--log", help="Collect history log"),
    game: bool = typer.Option(False, "--game", help="Collect game info"),
    daily: bool = typer.Option(False, "--daily", help="Daily graph"),
    width: int = typer.Option(100, "--width", help="Daily graph width"),
    height: int = typer.Option(10, "--height", help="Daily graph height"),
    color: int = typer.Option(1, "--color", help="Daily graph color [0|1]")
):
    from tko.cmds.cmd_collect import CollectSingle
    
    changedir = ctx.obj.get("changedir")
    
    params = CollectSingle.CollectParams()
    params.folder = Path() if changedir is None else Path(changedir)
    params.width = width
    params.height = height
    params.daily = daily
    params.resume = resume
    params.game = game
    params.log = log
    params.json_output = json_output
    params.colored = color
    
    data = CollectSingle.collect(params)

    if params.json_output:
        print(json.dumps(data.to_dict(), indent=4, ensure_ascii=False))

if __name__ == "__main__":
    app()
