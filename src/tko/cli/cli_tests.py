from pathlib import Path
import json
import re
import tomllib

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


@app.command("update-outputs", help="Run a solver for existing TOML cases and review new outputs")
def tests_update_outputs(
    ctx: typer.Context,
    test_file: Path = typer.Argument(..., exists=True, dir_okay=False),
    language: str = typer.Option(..., "--lang", "-l"),
    solver: Path = typer.Option(..., "--solver", exists=True, dir_okay=False),
    write: bool = typer.Option(False, "--write", help="Write the reviewed outputs to the file"),
) -> None:
    """Preview expected output updates; --write applies them after every run succeeds."""
    from tko.run.solver_builder import CompileError, SolverBuilder
    from tko.util.runner import Runner

    settings: Settings = ctx.obj
    source_text: str = test_file.read_text(encoding="utf-8")
    try:
        parsed: dict[str, object] = tomllib.loads(source_text)
    except tomllib.TOMLDecodeError as error:
        raise typer.BadParameter(f"Invalid TOML: {error}", param_hint="TEST_FILE") from error
    raw_cases: object = parsed.get("tests")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise typer.BadParameter("The file must contain at least one [[tests]] case")
    if "load" in parsed:
        raise typer.BadParameter("Files using `load` cannot be updated directly; update the referenced file")
    cases: list[dict[str, object]] = []
    for index, raw_case in enumerate(raw_cases, start=1):
        if not isinstance(raw_case, dict) or not isinstance(raw_case.get("input"), str) or not isinstance(raw_case.get("output"), str):
            raise typer.BadParameter(f"Case {index} must have string input and output fields")
        cases.append(raw_case)
    if solver.suffix.lstrip(".") != language:
        raise typer.BadParameter("--lang must match the solver file extension")
    builder: SolverBuilder = SolverBuilder([solver.resolve()], settings)
    try:
        executable, _ = builder.get_executable()
    except CompileError as error:
        raise typer.BadParameter(f"Compilation failed: {error}") from error
    if builder.has_compile_error():
        raise typer.BadParameter(f"Compilation failed:\n{executable.get_error_msg().plain()}")
    command, folder = executable.get_command()
    replacements: list[tuple[int, int, str, int]] = []
    table_starts: list[int] = [match.start() for match in re.finditer(r"(?m)^\s*\[\[tests\]\]\s*(?:#.*)?$", source_text)]
    if len(table_starts) != len(cases):
        raise typer.BadParameter("Could not safely locate each [[tests]] table in the source text")
    table_starts.append(len(source_text))
    for index, case in enumerate(cases):
        input_data: str = str(case["input"])
        expected: str = str(case["output"])
        if input_data and not input_data.endswith("\n"):
            input_data += "\n"
        if expected and not expected.endswith("\n"):
            expected += "\n"
        return_code, stdout, stderr = Runner.subprocess_run(command, input_data=input_data, folder=folder)
        if return_code != 0:
            raise typer.BadParameter(f"Case {index + 1} execution failed (exit {return_code}):\n{stderr or stdout}")
        if stdout != expected:
            start: int = table_starts[index]
            end: int = table_starts[index + 1]
            output_matches: list[re.Match[str]] = list(re.finditer(r"(?m)^\s*output\s*=\s*(?:'''[\s\S]*?'''|\"\"\"[\s\S]*?\"\"\"|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')", source_text[start:end]))
            if len(output_matches) != 1:
                raise typer.BadParameter(f"Could not safely locate output for case {index + 1}")
            output_match: re.Match[str] = output_matches[0]
            value_start: int = start + output_match.start()
            value_end: int = start + output_match.end()
            prefix: str = output_match.group(0).split("=", 1)[0] + "= "
            serialized_output: str = f"'''\n{stdout}'''" if "'''" not in stdout else json.dumps(stdout, ensure_ascii=False)
            replacements.append((value_start, value_end, prefix + serialized_output, index))
            label: str = str(case.get("label", f"case {index + 1}"))
            typer.echo(f"Changed: {label}")
            typer.echo(f"  old: {expected!r}")
            typer.echo(f"  new: {stdout!r}")
    if not replacements:
        typer.echo("All outputs already match.")
        return
    if not write:
        typer.echo("Preview only. Rerun with --write to save these outputs.")
        return
    updated_text: str = source_text
    for start, end, value, _ in reversed(replacements):
        updated_text = updated_text[:start] + value + updated_text[end:]
    test_file.write_text(updated_text, encoding="utf-8")
    typer.echo(f"Updated {len(replacements)} output(s) in {test_file}.")
