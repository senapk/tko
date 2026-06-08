import typer
from pathlib import Path
from typing import Optional

from tko.config.settings import Settings

app = typer.Typer(help="Manage individual tasks")

@app.command("open", help="Open a task in tui")
def task_open(
    ctx: typer.Context,
    target_list: Optional[list[str]] = typer.Argument(None, help="Solvers, test cases or directories to load"),
    index: Optional[int] = typer.Option(None, "--index", "-i", help="Run a specific test index"),
    pattern: str = typer.Option("@.in @.sol", "--pattern", "-p", help="Input/output file pattern (default: '@.in @.sol')"),
    filter: bool = typer.Option(False, "--filter", "-f", help="Filter solver files in temporary directory before running")
):
    from tko.util.param import Param
    from tko.util.pattern_loader import PatternLoader
    from tko.cmds.cmd_run import Run
    
    settings: Settings = ctx.obj    
    PatternLoader.pattern = pattern
    param = Param.Basic().set_index(index)
    if settings:
        param.set_diff_mode(settings.app.diff_mode)
    if filter:
        param.set_filter(True)
        
    targets = [Path(x) for x in target_list] if target_list else []
    cmd_run = Run(settings, targets, param, None, )
    cmd_run.set_curses()
    cmd_run.execute()

@app.command("list", help="List tasks")
def task_list(
    ctx: typer.Context,
    all: bool = typer.Option(False, "--all", "-a", help="Show all tasks"),
    down: bool = typer.Option(False, "--down", "-d", help="Show downloaded tasks only"),
    quests: bool = typer.Option(False, "--quest", "-q", help="Show quests")
):
    from tko.cli.common import load_repo
    from tko.cmds.cmd_open import CmdOpen
    
    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs)
    if repo is None:
        return
        
    action = CmdOpen(settings, repo)
    action.list(show_all=all, only_down=down, show_quests=quests)


@app.command("down", help="Download a task by full key")
def task_down(
    ctx: typer.Context,
    full_key: str = typer.Argument(..., help="Task full key (e.g. fup@mumia)")
):
    from tko.cli.common import load_repo
    from tko.cmds.cmd_down import CmdDown

    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs)
    if repo is None:
        return

    try:
        CmdDown(repo, full_key, settings).execute()
    except (Warning, ValueError) as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
