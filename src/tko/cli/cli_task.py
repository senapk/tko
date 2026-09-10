import typer
from pathlib import Path
from typing import Optional
from tko.cli.common import load_repo
from tko.cli.task_selector import TaskSelector

from tko.config.settings import Settings

app = typer.Typer(help="Manage individual tasks")


@app.command("show", help="Show task information, files, scores and graph")
def task_show(
    ctx: typer.Context,
    label: str | None = typer.Argument(None, help="Task key (for example: labs/fila or course@labs/fila)"),
    width: int = typer.Option(100, "--width", "-w", help="Graph width"),
    height: int = typer.Option(12, "--height", help="Graph height"),
    fzf: bool = typer.Option(False, "--fzf", "-f", help="Use fzf to select a task"),
):
    from tko.cmds.cmd_task import CmdTask

    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=True)
    if repo is None:
        raise typer.Exit(code=1)
    try:
        task = TaskSelector(repo, settings).select(label, fzf)
        if task is None:
            typer.echo("No materialized task selected")
            raise typer.Exit(code=0)
        CmdTask.show(settings, repo, task.basic.full_key, width, height)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1)
@app.command("open", help="Open a task in tui")
def task_open(
    ctx: typer.Context,
    target_list: Optional[list[str]] = typer.Argument(None, help="Solvers, test cases or directories to load"),
    index: Optional[int] = typer.Option(None, "--index", "-i", help="Run a specific test index"),
    pattern: str = typer.Option("@.in @.sol", "--pattern", "-p", help="Input/output file pattern (default: '@.in @.sol')"),
    filter: bool = typer.Option(False, "--filter", "-F", help="Filter solver files in temporary directory before running"),
    fzf: bool = typer.Option(False, "--fzf", "-f", help="Use fzf to select a task"),
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
    repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=True)
    if repo is None:
        raise typer.Exit(code=1)

    selected_task = None
    if not target_list:
        selected_task = TaskSelector(repo, settings).select(use_fzf=fzf)
        if selected_task is None:
            typer.echo("No materialized task selected")
            raise typer.Exit(code=0)
        target_folder = TaskSelector(repo, settings).task_folder(selected_task)
        target_list = [str(target_folder)]

    targets = [Path(x) for x in target_list]
    cmd_run = Run(settings=settings, target_list=targets, param=param, language=None, repo=repo)
    if selected_task is not None:
        cmd_run.set_task(repo, selected_task)
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
    repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=True)
    if repo is None:
        return
        
    action = CmdOpen(settings, repo)
    action.list(show_all=all, only_down=down, show_quests=quests)


@app.command("tests", help="List test cases without running a solver")
def task_tests(
    ctx: typer.Context,
    target_list: Optional[list[str]] = typer.Argument(None, help="README, test file or activity directory"),
    fzf: bool = typer.Option(False, "--fzf", "-f", help="Use fzf to select a task"),
):
    from tko.loader.test_discovery import TestDiscovery

    if not target_list:
        settings: Settings = ctx.obj
        repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=True)
        if repo is None:
            raise typer.Exit(code=1)
        task = TaskSelector(repo, settings).select(use_fzf=fzf)
        if task is None:
            typer.echo("No materialized task selected")
            raise typer.Exit(code=0)
        target_list = [str(TaskSelector(repo, settings).task_folder(task))]

    for target_text in target_list:
        target = Path(target_text)
        try:
            units = TestDiscovery.discover(target)
        except (FileNotFoundError, ValueError) as error:
            typer.echo(f"Unable to inspect {target}: {error}", err=True)
            raise typer.Exit(code=1)

        typer.echo(f"{target}: {len(units)} test(s)")
        for unit in units:
            label = unit.case or str(unit.index)
            typer.echo(f"  {label} ({unit.source})")


@app.command("down", help="Download a task using key, fzf or number selection")
def task_down(
    ctx: typer.Context,
    pattern: str | None = typer.Argument(None, help="Task key (e.g. fup@mumia)"),
    fzf: bool = typer.Option(False, "--fzf", "-f", help="Use fzf to select a task")
):
    from tko.cmds.cmd_down import CmdDown
    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=True)
    if repo is None:
        return
    
    selector = TaskSelector(repo, settings)
    result_task = selector.select(pattern, fzf, mode="downloadable")
    if result_task is None:
        typer.echo("No downloadable task selected")
        raise typer.Exit(code=0)
    result = result_task.basic.full_key
    
    try:
        CmdDown(repo, result, settings).execute()
    except (Warning, ValueError) as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
