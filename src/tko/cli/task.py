import typer
from pathlib import Path
from typing import Optional

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
    
    settings = ctx.obj.get("settings") if ctx.obj else None
    
    PatternLoader.pattern = pattern
    param = Param.Basic().set_index(index)
    if settings:
        param.set_diff_mode(settings.app.diff_mode)
    if filter:
        param.set_filter(True)
        
    targets = [Path(x) for x in target_list] if target_list else []
    cmd_run = Run(settings, targets, param)
    cmd_run.set_curses()
    cmd_run.execute()

@app.command("list", help="List tasks")
def task_list(
    ctx: typer.Context,
    all: bool = typer.Option(False, "--all", "-a", help="Show all tasks")
):
    from tko.cli.common import load_repo
    from tko.cmds.cmd_open import CmdOpen
    
    settings = ctx.obj.get("settings") if ctx.obj else None
    changedir = ctx.obj.get("changedir") if ctx.obj else Path('.')
    global_cache = ctx.obj.get("global_cache", False) if ctx.obj else False
    update = ctx.obj.get("update", False) if ctx.obj else False
    
    repo, _ = load_repo(changedir, show_warnings=True, auto_load=True, global_cache=global_cache, force_update=update)
    if repo is None:
        return
        
    action = CmdOpen(settings, repo, update)
    action.list(show_all=all)

if __name__ == "__main__":
    app()
