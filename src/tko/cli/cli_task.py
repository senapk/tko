from shutil import which

import typer
from pathlib import Path
from typing import Optional
from tko.cli.common import load_repo
from tko.cli.selector import select_with_fzf, select_with_number
from tko.game.task import Task

from tko.config.settings import Settings

def save_key_on_repo(repo_path: Path, key: str):
    key_file = repo_path / ".tko" / ".fzf"
    key_file.parent.mkdir(parents=True, exist_ok=True)
    key_file.write_text(key)

def load_key_from_repo(repo_path: Path) -> Optional[str]:
    key_file = repo_path / ".tko" / ".fzf"
    if key_file.exists():
        return key_file.read_text().strip()
    return None

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
    repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=True)
    
    targets = [Path(x) for x in target_list] if target_list else []
    cmd_run = Run(settings=settings, target_list=targets, param=param, language=None, repo=repo)
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


@app.command("down", help="Download a task using key, fzf or number selection")
def task_down(
    ctx: typer.Context,
    pattern: str | None = typer.Argument(None, help="Task key (e.g. fup@mumia)"),
    fzf: bool = typer.Option(False, "--fzf", "-f", help="Use fzf to select a task")
):
    from tko.cli.common import load_repo
    from tko.cmds.cmd_down import CmdDown
    from tko.cmds.cmd_open import CmdOpen

    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=True)
    if repo is None:
        return
    
    action = CmdOpen(settings, repo)
    tree = action.build_tree(show_all=True, full_key=False, quests_keys=True)
    items = [
        (elem.basic.full_key, x.plain() if settings.rs.monochrome else x.ansi()) 
        for x, elem in tree.get_rendered_items(show_selected=False)
        if isinstance(elem, Task) and elem.resource.is_make and elem.resource.is_import_type
    ]
    if not items:
        typer.echo("No downloadable tasks found")
        raise typer.Exit(code=0)
    found = False

    if pattern is not None:
        found = len([ (key, text) for key, text in items if pattern == key ]) == 1

    if found and pattern is not None:
        result = pattern
    else:    
        has_fzf = which("fzf") is not None
        if fzf and has_fzf:
            last_selected_key = load_key_from_repo(repo.paths.root_dir)
            result = select_with_fzf(items, pattern, selected=last_selected_key)
        else:
            result = select_with_number(items, pattern)
        if result is None:
            typer.echo("No task selected")
            raise typer.Exit(code=0)
        save_key_on_repo(repo.paths.root_dir, result)
    
    try:
        CmdDown(repo, result, settings).execute()
    except (Warning, ValueError) as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
