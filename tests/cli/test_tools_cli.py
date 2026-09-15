from pathlib import Path

from click.testing import Result
import pytest
from typer.testing import CliRunner

from tko.cli.cli_tools import app
from tko.config.settings import Settings
from tko.util.console import Console


def test_convert_tests_writes_selected_format(tmp_path: Path) -> None:
    origin: Path = tmp_path / "cases.toml"
    origin.write_text("[[tests]]\ninput = '1'\noutput = '2'\n", encoding="utf-8")
    output: Path = tmp_path / "out.tio"
    result: Result = CliRunner().invoke(
        app, ["convert-tests", str(origin), "-o", str(output), "--sort", "--number"],
        obj=Settings(tmp_path / "settings"),
    )
    assert result.exit_code == 0, result.output
    assert output.is_file()
    assert "1" in output.read_text() and "2" in output.read_text()


def test_convert_tests_defaults_to_stdout(tmp_path: Path) -> None:
    origin: Path = tmp_path / "cases.toml"
    origin.write_text("[[tests]]\ninput = '1'\noutput = '2'\n", encoding="utf-8")
    with Console.capture() as output:
        result: Result = CliRunner().invoke(app, ["convert-tests", str(origin)], obj=Settings(tmp_path / "settings"))
    assert result.exit_code == 0, result.output
    assert "[[tests]]" in result.output + output.getvalue()


@pytest.mark.parametrize("mode", ["side", "down"])
def test_diff_compares_text_and_files(tmp_path: Path, mode: str) -> None:
    first: Path = tmp_path / "first.txt"
    second: Path = tmp_path / "second.txt"
    first.write_text("alpha\n")
    second.write_text("beta\n")
    with Console.capture() as file_output:
        files: Result = CliRunner().invoke(app, ["diff", str(first), str(second), "--input-type", "file", "--diff-mode", mode])
    with Console.capture() as text_output:
        texts: Result = CliRunner().invoke(app, ["diff", "alpha\\n", "beta\\n", "--diff-mode", mode])
    assert files.exit_code == texts.exit_code == 0
    assert file_output.getvalue() == text_output.getvalue()
    assert "alpha" in file_output.getvalue()


def test_diff_missing_file_fails(tmp_path: Path) -> None:
    result: Result = CliRunner().invoke(app, ["diff", str(tmp_path / "missing"), "other", "--input-type", "file"])
    assert result.exit_code == 1


def test_rebase_requires_output_and_rewrites_local_links(tmp_path: Path) -> None:
    origin: Path = tmp_path / "README.md"
    origin.write_text("[Task](labs/task/README.md)\n")
    destination: Path = tmp_path / "docs" / "README.md"
    destination.parent.mkdir()
    missing: Result = CliRunner().invoke(app, ["rebase", str(origin)])
    assert missing.exit_code == 2
    result: Result = CliRunner().invoke(app, ["rebase", str(origin), "-o", str(destination)])
    assert result.exit_code == 0, result.output
    assert "../labs/task/README.md" in destination.read_text()
