from pathlib import Path

from typer.testing import CliRunner

from tko.cli.cli_build import app


def test_build_index_yes_removes_broken_local_target(tmp_path: Path) -> None:
    runner = CliRunner()
    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    base_dir.mkdir()
    index_path.write_text(
        "# Disciplina\n\n"
        "- [ ] `@missing` [Missing](base/missing/README.md)\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["index", str(index_path), str(base_dir), "--yes"])

    assert result.exit_code == 0
    assert "@missing" not in index_path.read_text(encoding="utf-8")
