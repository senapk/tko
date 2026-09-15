"""Commands for building, inspecting and running individual activities."""
from pathlib import Path
from dataclasses import replace
from tko.config.run_settings import RunSettings

import typer

from tko.cli.common import load_repo
from tko.cli.task_selector import TaskSelector
from tko.config.settings import Settings
from tko.enums.diff_mode import DiffMode
from tko.game.task import Task
from tko.repository.repository import Repository

app = typer.Typer(help="Manage individual tasks")


def _repository(settings: Settings, path: Path | None = None) -> Repository:
    rs: RunSettings = settings.rs
    if path is not None:
        resolved: Path = path.resolve()
        rs = replace(rs, changedir=resolved if resolved.is_dir() else resolved.parent)
    repo, _ = load_repo(rs, show_warnings=True, auto_load=True)
    if repo is None:
        raise typer.Exit(1)
    return repo


def _validate_paths(paths: list[Path] | None, fzf: bool) -> None:
    if paths and fzf:
        raise typer.BadParameter("Paths cannot be combined with --fzf")
    for path in paths or []:
        if not path.exists():
            raise typer.BadParameter(f"Path not found: {path}")


def _selected_task(selector: TaskSelector, path: Path | None, fzf: bool) -> Task:
    try:
        task: Task | None = selector.select_path(path, use_fzf=fzf)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    if task is None:
        typer.echo("No materialized task selected")
        raise typer.Exit(0)
    return task


@app.command("build", help="Build task artifacts and update task README.md")
def task_build(
    targets: list[Path] | None = typer.Argument(None, help="Task directories"),
    check: bool = typer.Option(False, "--check", "-c", help="Check if the file needs to be rebuilt"),
    brief: bool = typer.Option(False, "--brief", "-b", help="Brief mode"),
    moodle: str | None = typer.Option(None, "--moodle", "-m", help="GitHub repository URL for Moodle VPL build"),
    erase: bool = typer.Option(False, "--erase", "-e", help="Erase temporary files"),
) -> None:
    from tko.feno.build import build_task

    build_task(targets=targets or [], remote_url=moodle, check=check, erase=erase, brief=brief)


@app.command("show", help="Show task information, files, scores and graph")
def task_show(
    ctx: typer.Context,
    path: Path | None = typer.Argument(None, help="Existing task directory or file; defaults to the current activity"),
    width: int = typer.Option(100, "--width", "-w", min=1, help="Graph width"),
    height: int = typer.Option(12, "--height", min=1, help="Graph height"),
    graph_only: bool = typer.Option(False, "--graph-only", help="Show only the history graph"),
    fzf: bool = typer.Option(False, "--fzf", "-f", help="Select a task with fzf"),
) -> None:
    from tko.cmds.cmd_task import CmdTask

    _validate_paths([path] if path is not None else None, fzf)
    settings: Settings = ctx.obj
    repo: Repository = _repository(settings, path)
    task: Task = _selected_task(TaskSelector(repo, settings), path, fzf)
    if graph_only:
        CmdTask.show_graph(settings, repo, task.basic.full_key, width, height)
    else:
        CmdTask.show(settings, repo, task.basic.full_key, width, height)


@app.command("open", help="Run a task in the interactive test interface")
def task_open(
    ctx: typer.Context,
    target_list: list[Path] | None = typer.Argument(None, help="Existing solver files, test files or directories"),
    index: int | None = typer.Option(None, "--index", "-i", help="Run a specific test index"),
    filter: bool = typer.Option(False, "--filter", "-F", help="Filter solver files in a temporary directory"),
    diff_mode: DiffMode | None = typer.Option(None, "--diff-mode", help="Diff layout"),
    fzf: bool = typer.Option(False, "--fzf", "-f", help="Select a task with fzf"),
) -> None:
    from tko.util.param import Param
    from tko.cmds.cmd_run import Run

    _validate_paths(target_list, fzf)
    settings: Settings = ctx.obj
    repo: Repository = _repository(settings, target_list[0] if target_list else None)
    param: Param.Basic = Param.Basic().set_index(index)
    param.set_diff_mode(diff_mode if diff_mode is not None else settings.app.diff_mode)
    param.set_filter(filter)
    selected_task: Task | None = None
    targets: list[Path] = target_list or []
    if not targets:
        selector: TaskSelector = TaskSelector(repo, settings)
        selected_task = _selected_task(selector, None, fzf)
        targets = [selector.task_folder(selected_task)]
    cmd_run: Run = Run(settings=settings, target_list=targets, param=param, language=None, repo=repo)
    if selected_task is not None:
        cmd_run.set_task(repo, selected_task)
    cmd_run.set_tui()
    cmd_run.execute()


@app.command("list", help="List tasks")
def task_list(
    ctx: typer.Context,
    all: bool = typer.Option(False, "--all", "-a", help="Show all tasks"),
    downloaded: bool = typer.Option(False, "--downloaded", help="Show downloaded tasks only"),
    quests: bool = typer.Option(False, "--quest", "-q", help="Show quests"),
) -> None:
    from tko.cmds.cmd_open import CmdOpen

    settings: Settings = ctx.obj
    repo: Repository = _repository(settings)
    CmdOpen(settings, repo).list(show_all=all, only_down=downloaded, show_quests=quests)


@app.command("tests", help="List test cases without running a solver")
def task_tests(
    ctx: typer.Context,
    target_list: list[Path] | None = typer.Argument(None, help="Existing README, test files or activity directories"),
    fzf: bool = typer.Option(False, "--fzf", "-f", help="Select a task with fzf"),
) -> None:
    from tko.loader.test_discovery import TestDiscovery
    from tko.run.unit import Unit

    _validate_paths(target_list, fzf)
    targets: list[Path] = target_list or []
    if not targets:
        settings: Settings = ctx.obj
        repo: Repository = _repository(settings)
        selector: TaskSelector = TaskSelector(repo, settings)
        task: Task = _selected_task(selector, None, fzf)
        targets = [selector.task_folder(task)]
    for target in targets:
        try:
            units: list[Unit] = TestDiscovery.discover(target)
        except (OSError, ValueError) as error:
            typer.echo(f"Unable to inspect {target}: {error}", err=True)
            raise typer.Exit(1) from error
        typer.echo(f"{target}: {len(units)} test(s)")
        for unit in units:
            label: str = unit.case or str(unit.index)
            typer.echo(f"  {label} ({unit.source})")


@app.command("download", help="Download an activity by key or interactive selection")
def task_download(
    ctx: typer.Context,
    pattern: str | None = typer.Argument(None, help="Task key, such as course@labs/fila"),
    fzf: bool = typer.Option(False, "--fzf", "-f", help="Select a task with fzf"),
) -> None:
    from tko.cmds.cmd_down import CmdDown

    settings: Settings = ctx.obj
    repo: Repository = _repository(settings)
    task: Task | None = TaskSelector(repo, settings).select(pattern, fzf, mode="downloadable")
    if task is None:
        typer.echo("No downloadable task selected")
        raise typer.Exit(0)
    try:
        CmdDown(repo, task.basic.full_key, settings).execute()
    except (Warning, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


if __name__ == "__main__":
    app()
