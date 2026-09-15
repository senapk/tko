from typer.testing import CliRunner
import re

from tko.cli.cli_tools import app


def test_util_tests_converts_origins(monkeypatch):
    captured = {}

    class FakeCmdBuild:
        def __init__(self, target, origins, manip, settings, read_pattern, write_pattern):
            captured["target"] = target
            captured["origins"] = origins
            captured["manip"] = manip
            captured["settings"] = settings
            captured["read_pattern"] = read_pattern
            captured["write_pattern"] = write_pattern

        def execute(self):
            captured["executed"] = True

    monkeypatch.setattr("tko.cmds.cmd_build.CmdBuild", FakeCmdBuild)
    settings = object()
    result = CliRunner().invoke(
        app,
        [
            "tests", "one.toml", "two.tio", "--output", "out.tio", "--sort", "--number",
            "--read-pattern", "input-@.txt output-@.txt",
            "--write-pattern", "@.in @.sol",
        ],
        obj=settings,
    )

    assert result.exit_code == 0
    assert captured["target"].name == "out.tio"
    assert [path.name for path in captured["origins"]] == ["one.toml", "two.tio"]
    assert captured["manip"].to_sort is True
    assert captured["manip"].to_number is True
    assert captured["settings"] is settings
    assert captured["read_pattern"] == "input-@.txt output-@.txt"
    assert captured["write_pattern"] == "@.in @.sol"
    assert captured["executed"] is True


def test_util_tests_allows_stdout_output(monkeypatch):
    captured = {}

    class FakeCmdBuild:
        def __init__(self, target, origins, manip, settings, read_pattern, write_pattern):
            captured["target"] = target

        def execute(self):
            captured["executed"] = True

    monkeypatch.setattr("tko.cmds.cmd_build.CmdBuild", FakeCmdBuild)
    result = CliRunner().invoke(app, ["tests", "tests.toml"])

    assert result.exit_code == 0
    assert captured["target"] is None
    assert captured["executed"] is True


def test_util_tests_does_not_expose_width_option():
    result = CliRunner().invoke(app, ["tests", "--help"])
    plain_help = re.sub(r"\s+", "", re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", result.stdout))

    assert result.exit_code == 0
    assert "--width" not in plain_help
    assert "--read-pattern" in plain_help
    assert "--write-pattern" in plain_help
