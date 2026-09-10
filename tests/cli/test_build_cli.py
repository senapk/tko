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
        "- [ ] `@missing eval=none` [Missing](base/missing/README.md)\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["index", str(index_path), str(base_dir), "--yes"])

    assert result.exit_code == 0
    assert "@missing" not in index_path.read_text(encoding="utf-8")


def test_build_index_no_align_compacts_task_columns(tmp_path: Path) -> None:
    runner = CliRunner()
    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    task_dir = base_dir / "a"
    task_dir.mkdir(parents=True)
    (task_dir / "README.md").write_text("# A\n", encoding="utf-8")
    index_path.write_text("- [ ] `@a eval=none` [A](base/a/README.md)\n", encoding="utf-8")

    result = runner.invoke(app, ["index", str(index_path), str(base_dir), "--no-align"])

    assert result.exit_code == 0
    assert "`eval=none`" in index_path.read_text(encoding="utf-8")
