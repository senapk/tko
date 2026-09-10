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
    assert "`eval=none`" in index_path.read_text(encoding="utf-8")
    assert "@a" not in index_path.read_text(encoding="utf-8")


def test_index_download_converts_remote_link_to_local_source_metadata(tmp_path: Path, monkeypatch) -> None:
    index_path = tmp_path / "README.md"
    remote_readme = tmp_path / "cache" / "labs" / "fila" / "README.md"
    remote_readme.parent.mkdir(parents=True)
    remote_readme.write_text("# Fila\n", encoding="utf-8")
    url = "https://github.com/org/repo/blob/main/labs/fila/README.md"
    index_path.write_text(
        f"- [ ] `@legacy eval=diff` [Fila]({url})\n", encoding="utf-8"
    )

    monkeypatch.setattr(
        "tko.cli.cli_index.GitCache.git_hub_url_to_path",
        lambda _self, _url, load_git: (remote_readme, True),
    )

    result = CliRunner().invoke(app, ["download", str(index_path)])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "labs" / "fila" / "README.md").read_text(encoding="utf-8") == "# Fila\n"
    assert index_path.read_text(encoding="utf-8") == (
        "- [ ] `eval=diff` [Fila](labs/fila/README.md) "
        f"<!-- source={url} -->\n"
    )


def test_index_update_uses_source_metadata_and_keeps_local_link(tmp_path: Path, monkeypatch) -> None:
    index_path = tmp_path / "README.md"
    url = "https://github.com/org/repo/blob/main/labs/fila/README.md"
    index_path.write_text(
        "- [ ] `eval=diff custom=7` [Minha fila](labs/fila/README.md) "
        f"<!-- source={url} -->\n",
        encoding="utf-8",
    )
    remote_readme = tmp_path / "cache" / "labs" / "fila" / "README.md"
    remote_readme.parent.mkdir(parents=True)
    remote_readme.write_text("# Fila atualizada\n", encoding="utf-8")
    materialized = tmp_path / "labs" / "fila"
    materialized.mkdir(parents=True)
    (materialized / "README.md").write_text("# Antiga\n", encoding="utf-8")
    monkeypatch.setattr(
        "tko.cli.cli_index.GitCache.git_hub_url_to_path",
        lambda _self, _url, load_git: (remote_readme, True),
    )

    result = CliRunner().invoke(app, ["update", str(index_path), "labs/fila"])

    assert result.exit_code == 0, result.output
    assert (materialized / "README.md").read_text(encoding="utf-8") == "# Fila atualizada\n"
    line = index_path.read_text(encoding="utf-8")
    assert "`eval=diff custom=7`" in line
    assert "[Minha fila](labs/fila/README.md)" in line
    assert line.count("<!-- source=") == 1


def test_index_download_rejects_remote_readme_at_repository_root(tmp_path: Path) -> None:
    index_path = tmp_path / "README.md"
    index_path.write_text(
        "- [ ] `eval=diff` [Root](https://github.com/org/repo/blob/main/README.md)\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["download", str(index_path)])

    assert result.exit_code != 0
    assert "inside an activity folder" in result.output
