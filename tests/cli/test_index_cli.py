from pathlib import Path

from click.testing import Result
from pytest import MonkeyPatch
from typer.testing import CliRunner

from tko.cli.cli_build import app
from tko.repository.git_cache import GitCache
from tko.util.git_hub_url import GitHubUrl


def _mock_remote_readme(monkeypatch: MonkeyPatch, remote_readme: Path) -> None:
    def lookup(_self: GitCache, _url: GitHubUrl, load_git: bool = False) -> tuple[Path, bool]:
        return remote_readme, True

    monkeypatch.setattr(GitCache, "git_hub_url_to_path", lookup)


def test_index_build_no_align_compacts_task_columns(tmp_path: Path) -> None:
    runner = CliRunner()
    index_path = tmp_path / "README.md"
    base_dir = tmp_path / "base"
    task_dir = base_dir / "a"
    task_dir.mkdir(parents=True)
    (task_dir / "README.md").write_text("# A\n", encoding="utf-8")
    index_path.write_text("- [ ] `@a eval=none` [A](base/a/README.md)\n", encoding="utf-8")

    result: Result = runner.invoke(app, ["index", str(index_path), "--from", str(base_dir), "--no-align"])

    assert result.exit_code == 0
    assert "`eval=none`" in index_path.read_text(encoding="utf-8")
    assert "@a" not in index_path.read_text(encoding="utf-8")


def test_index_build_discovers_tasks_from_multiple_sources(tmp_path: Path) -> None:
    index_path = tmp_path / "README.md"
    labs_task = tmp_path / "labs" / "carro"
    wiki_task = tmp_path / "wiki" / "git"
    labs_task.mkdir(parents=True)
    wiki_task.mkdir(parents=True)
    (labs_task / "README.md").write_text("# Carro\n", encoding="utf-8")
    (wiki_task / "README.md").write_text("# Git\n", encoding="utf-8")
    index_path.write_text("# Atividades\n", encoding="utf-8")

    result: Result = CliRunner().invoke(
        app,
        ["index", str(index_path), "--from", "labs", "--from", "wiki", "--no-align"],
    )

    assert result.exit_code == 0, result.output
    content = index_path.read_text(encoding="utf-8")
    assert "## labs" in content
    assert "## wiki" in content
    assert "[Carro](labs/carro/README.md)" in content
    assert "[Git](wiki/git/README.md)" in content


def test_index_pull_converts_remote_link_to_local_source_metadata(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    index_path = tmp_path / "README.md"
    remote_readme = tmp_path / "cache" / "labs" / "fila" / "README.md"
    remote_readme.parent.mkdir(parents=True)
    remote_readme.write_text("# Fila\n", encoding="utf-8")
    url = "https://github.com/org/repo/blob/main/labs/fila/README.md"
    index_path.write_text(
        f"- [ ] `@legacy eval=diff` [Fila]({url})\n", encoding="utf-8"
    )

    _mock_remote_readme(monkeypatch, remote_readme)

    result: Result = CliRunner().invoke(app, ["download", str(index_path)])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "labs" / "fila" / "README.md").read_text(encoding="utf-8") == "# Fila\n"
    assert index_path.read_text(encoding="utf-8") == (
        "- [ ] `eval=diff` [Fila](labs/fila/README.md) "
        f"<!-- source={url} -->\n"
    )


def test_index_pull_replace_uses_source_metadata_and_keeps_local_link(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
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
    (materialized / "local.txt").write_text("Alteração local\n", encoding="utf-8")
    _mock_remote_readme(monkeypatch, remote_readme)

    result: Result = CliRunner().invoke(app, ["download", str(index_path), "labs/fila", "--replace"])

    assert result.exit_code == 0, result.output
    assert (materialized / "README.md").read_text(encoding="utf-8") == "# Fila atualizada\n"
    assert not (materialized / "local.txt").exists()
    line = index_path.read_text(encoding="utf-8")
    assert "`eval=diff custom=7`" in line
    assert "[Minha fila](labs/fila/README.md)" in line
    assert line.count("<!-- source=") == 1


def test_index_pull_preserves_existing_materialized_copy(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    index_path: Path = tmp_path / "README.md"
    url: str = "https://github.com/org/repo/blob/main/labs/fila/README.md"
    line: str = f"- [ ] `eval=diff` [Fila](labs/fila/README.md) <!-- source={url} -->\n"
    index_path.write_text(line, encoding="utf-8")
    materialized: Path = tmp_path / "labs" / "fila"
    materialized.mkdir(parents=True)
    (materialized / "README.md").write_text("# Alterada localmente\n", encoding="utf-8")

    def unexpected_lookup(_self: GitCache, _url: GitHubUrl, load_git: bool = False) -> tuple[Path, bool]:
        raise AssertionError("An existing copy must not trigger a remote download")

    monkeypatch.setattr(GitCache, "git_hub_url_to_path", unexpected_lookup)
    result: Result = CliRunner().invoke(app, ["download", str(index_path)])

    assert result.exit_code == 0, result.output
    assert (materialized / "README.md").read_text(encoding="utf-8") == "# Alterada localmente\n"
    assert index_path.read_text(encoding="utf-8") == line


def test_index_pull_restores_missing_materialized_copy(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    index_path: Path = tmp_path / "README.md"
    url: str = "https://github.com/org/repo/blob/main/labs/fila/README.md"
    index_path.write_text(
        f"- [ ] `eval=diff` [Fila](labs/fila/README.md) <!-- source={url} -->\n",
        encoding="utf-8",
    )
    remote_readme: Path = tmp_path / "cache" / "labs" / "fila" / "README.md"
    remote_readme.parent.mkdir(parents=True)
    remote_readme.write_text("# Restaurada\n", encoding="utf-8")
    _mock_remote_readme(monkeypatch, remote_readme)

    result: Result = CliRunner().invoke(app, ["download", str(index_path)])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "labs" / "fila" / "README.md").read_text(encoding="utf-8") == "# Restaurada\n"


def test_index_pull_requires_replace_for_existing_remote_destination(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    index_path: Path = tmp_path / "README.md"
    url: str = "https://github.com/org/repo/blob/main/labs/fila/README.md"
    index_path.write_text(f"- [ ] `eval=diff` [Fila]({url})\n", encoding="utf-8")
    materialized: Path = tmp_path / "labs" / "fila"
    materialized.mkdir(parents=True)
    (materialized / "README.md").write_text("# Local\n", encoding="utf-8")

    def unexpected_lookup(_self: GitCache, _url: GitHubUrl, load_git: bool = False) -> tuple[Path, bool]:
        raise AssertionError("A conflicting destination must be rejected before downloading")

    monkeypatch.setattr(GitCache, "git_hub_url_to_path", unexpected_lookup)
    result: Result = CliRunner().invoke(app, ["download", str(index_path)])

    assert result.exit_code == 2
    assert "--replace" in result.output
    assert (materialized / "README.md").read_text(encoding="utf-8") == "# Local\n"
    assert f"[Fila]({url})" in index_path.read_text(encoding="utf-8")


def test_index_pull_rejects_remote_readme_at_repository_root(tmp_path: Path) -> None:
    index_path = tmp_path / "README.md"
    index_path.write_text(
        "- [ ] `eval=diff` [Root](https://github.com/org/repo/blob/main/README.md)\n",
        encoding="utf-8",
    )

    result: Result = CliRunner().invoke(app, ["download", str(index_path)])

    assert result.exit_code != 0
    assert "inside an activity folder" in result.output
