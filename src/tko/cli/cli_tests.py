from pathlib import Path

import typer

from tko.config.settings import Settings

app: typer.Typer = typer.Typer(help="List and convert test cases", no_args_is_help=True)


@app.command("convert", help="Convert test cases between supported formats")
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
    from tko.cmds.cmd_build import CmdBuild
    from tko.util.param import Param

    settings: Settings = ctx.obj
    manipulation: Param.Manip = Param.Manip().set_unlabel(unlabel).set_to_sort(sort).set_to_number(number)
    CmdBuild(
        None if output is None else Path(output),
        [Path(origin) for origin in origins],
        manipulation,
        settings,
        read_pattern=read_pattern,
        write_pattern=write_pattern,
    ).execute()


@app.command("list", help="List test cases without running a solver")
def tests_list(targets: list[str] = typer.Argument(...)) -> None:
    from tko.loader.test_discovery import TestDiscovery
    from tko.run.unit import Unit

    for target in targets:
        path: Path = Path(target)
        units: list[Unit] = TestDiscovery.discover(path)
        typer.echo(f"{path}: {len(units)} test(s)")
        for unit in units:
            typer.echo(f"  {unit.case or unit.index} ({unit.source})")
