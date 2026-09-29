"""Commands for building, inspecting and running individual activities."""
from pathlib import Path
from dataclasses import replace
from tko.config.run_settings import RunSettings

import typer

from tko.cli.common import load_repo
from tko.cli.task_selector import TaskSelector
from tko.config.settings import Settings
from tko.enums.diff_count import DiffCount
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


def _languages_for_activity(activity: Path) -> list[str]:
    source_root: Path = activity / "src"
    if not source_root.is_dir():
        return []
    return sorted(path.name for path in source_root.iterdir() if path.is_dir())


def _check_activity(settings: Settings, repo: Repository | None, activity: Path) -> bool:
    from tko.cmds.cmd_run import Run
    from tko.util.param import Param

    languages: list[str] = _languages_for_activity(activity)
    if not languages:
        typer.echo(f"Nenhuma linguagem encontrada em {activity / 'src'}", err=True)
        return False

    succeeded: bool = True
    for language in languages:
        typer.echo(f"{activity} [{language}]")
        param: Param.Basic = Param.Basic()
        param.set_compact(True)
        param.set_diff_count(DiffCount.NONE)
        command: Run = Run(
            settings=settings,
            target_list=[activity],
            param=param,
            language=language,
            repo=repo,
        )
        try:
            result: int = command.execute()
        except Exception as error:
            typer.echo(f"Falha em {activity} [{language}]: {error}", err=True)
            succeeded = False
            continue
        if result != 100:
            succeeded = False
    return succeeded


def _selected_task(selector: TaskSelector, path: Path | None, fzf: bool) -> Task:
    try:
        task: Task | None = selector.select_path(path, use_fzf=fzf)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    if task is None:
        typer.echo("No materialized task selected")
        raise typer.Exit(0)
    return task


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


@app.command("list", help="List components and tests in a task")
def task_list(
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
        activity: Path = target if target.is_dir() else target.parent
        source_root: Path = activity / "src"
        components: list[Path] = sorted(path for path in source_root.rglob("*") if path.is_file()) if source_root.is_dir() else []
        typer.echo(f"{target}: {len(components)} component(s), {len(units)} test(s)")
        for component in components:
            typer.echo(f"  component: {component.relative_to(activity)}")
        for unit in units:
            label: str = unit.case or str(unit.index)
            typer.echo(f"  {label} ({unit.source})")


@app.command("down", help="Download an activity by key or interactive selection")
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
