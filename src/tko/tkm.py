from __future__ import annotations

import sys
import typer

from tko.__init__ import __version__
from tko.config.settings import Settings
from tko.cli.cli_audit import app as audit_app
from tko.cli.cli_collect import app as collect_app
from tko.cli.cli_index import app as index_app
from tko.cli.cli_tools import app as utility_app
from tko.__main__ import main_callback, _APP_KEYBOARD_INTERRUPT
from tko.util.console import Console

app = typer.Typer(name="tkm", help=f"tkm {__version__}", no_args_is_help=True, context_settings={"help_option_names": ["-h", "--help"]})
app.add_typer(audit_app, name="audit")
app.add_typer(collect_app, name="collect")
app.add_typer(index_app, name="index")
app.add_typer(utility_app, name="tool")

task_app = typer.Typer(help="Build and check task content", no_args_is_help=True)
tests_app = typer.Typer(help="Convert and list test cases", no_args_is_help=True)
app.add_typer(task_app, name="task")
app.add_typer(tests_app, name="tests")


@task_app.command("build", help="Build task artifacts")
def task_build(
    ctx: typer.Context,
    targets: list[str] = typer.Argument([]),
    check: bool = typer.Option(False, "--check", "-c"),
    brief: bool = typer.Option(False, "--brief", "-b"),
    moodle: bool = typer.Option(False, "--moodle", "-m"),
    erase: bool = typer.Option(False, "--erase", "-e"),
) -> None:
    from pathlib import Path
    from tko.feno.build import build_task

    settings: Settings = ctx.obj
    if not build_task([Path(target) for target in targets], moodle, check, erase, brief, settings):
        raise typer.Exit(1)


@task_app.command("check", help="Run each language found under activity src directories")
def task_check(ctx: typer.Context, targets: list[str] = typer.Argument([])) -> None:
    from pathlib import Path
    from tko.cli.cli_task import _check_activity
    from tko.cli.common import load_repo

    settings: Settings = ctx.obj
    activities = [Path(target).resolve() for target in targets] if targets else [Path.cwd()]
    repo, _ = load_repo(settings.rs, show_warnings=False)
    succeeded: bool = True
    for activity in activities:
        if not activity.is_dir():
            typer.echo(f"Activity is not a directory: {activity}", err=True)
            succeeded = False
            continue
        succeeded = _check_activity(settings, repo, activity) and succeeded
    if not succeeded:
        raise typer.Exit(1)


@tests_app.command("convert", help="Convert test cases between supported formats")
def tests_convert(
    ctx: typer.Context,
    origins: list[str] = typer.Argument(...),
    output: str | None = typer.Option(None, "--output", "-o"),
    read_pattern: str = typer.Option("@.in @.sol", "--read-pattern"),
    write_pattern: str = typer.Option("@.in @.sol", "--write-pattern"),
    unlabel: bool = typer.Option(False, "--unlabel", "-u"),
    number: bool = typer.Option(False, "--number", "-n"),
    sort: bool = typer.Option(False, "--sort", "-s"),
) -> None:
    from pathlib import Path
    from tko.cmds.cmd_build import CmdBuild
    from tko.util.param import Param

    settings: Settings = ctx.obj
    manip = Param.Manip().set_unlabel(unlabel).set_to_sort(sort).set_to_number(number)
    CmdBuild(
        None if output is None else Path(output),
        [Path(origin) for origin in origins],
        manip,
        settings,
        read_pattern=read_pattern,
        write_pattern=write_pattern,
    ).execute()


@tests_app.command("list", help="List test cases without running a solver")
def tests_list(targets: list[str] = typer.Argument(...)) -> None:
    from pathlib import Path
    from tko.loader.test_discovery import TestDiscovery
    from tko.run.unit import Unit

    for target in targets:
        path: Path = Path(target)
        units: list[Unit] = TestDiscovery.discover(path)
        typer.echo(f"{path}: {len(units)} test(s)")
        for unit in units:
            typer.echo(f"  {unit.case or unit.index} ({unit.source})")


app.callback()(main_callback)


def main() -> None:
    from tko.repository.task_data_format import MigrationRequiredError

    try:
        app()
    except MigrationRequiredError as exc:
        Console.print(str(exc))
        sys.exit(1)
    except KeyboardInterrupt:
        Console.print(f"\n\n{_APP_KEYBOARD_INTERRUPT}")
        sys.exit(1)


if __name__ == "__main__":
    main()
