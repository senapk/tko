from pathlib import Path

from typer.testing import CliRunner

from tko.cli.cli_index import app


def test_index_build_no_align_compacts_task_columns(tmp_path: Path) -> None:
    runner = CliRunner()
    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    task_dir = base_dir / "a"
    task_dir.mkdir(parents=True)
    (task_dir / "README.md").write_text("# A\n", encoding="utf-8")
    index_path.write_text("- [ ] `@a eval=none` [A](base/a/README.md)\n", encoding="utf-8")

    result = runner.invoke(app, ["build", str(index_path), str(base_dir), "--no-align"])

    assert result.exit_code == 0
    assert "`@a eval=none gcs=1`" in index_path.read_text(encoding="utf-8")
