from __future__ import annotations

import tomllib
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tko.config.run_settings import RunSettings
from tko.config.settings import Settings
from tko.repository.remote import Remote, SourceType
from tko.repository.repository import Repository
from tko.repository.source_actions import SourceActions
from tko.util.console import Console


def make_repo(tmp_path: Path) -> Repository:
    return Repository(tmp_path, RunSettings(changedir=tmp_path), git_cache=None, recursive_search=False)


def make_settings() -> Settings:
    def mock_has_alias_git(_alias: str) -> bool:
        return False
    def mock_get_alias_git(_alias: str) -> None:
        return None
    return cast(Settings, SimpleNamespace(has_alias_git=mock_has_alias_git, get_alias_git=mock_get_alias_git))


def read_config(repo: Repository) -> dict[str, Any]:
    return tomllib.loads(repo.paths.config_file.read_text(encoding="utf-8"))


def test_list_sources_shows_context_uri_and_authoring(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    outside = tmp_path.parent / "source-actions-outside" / "README.md"
    outside.parent.mkdir(exist_ok=True)
    outside.write_text("# outside\n", encoding="utf-8")
    repo.data.set_source(Remote.from_uri("base", outside.as_posix()))
    actions = SourceActions(make_settings(), repo)

    with Console.capture() as capture:
        actions.list_sources()

    output = capture.getvalue()
    assert "LABEL  CONTEXTO  URI  AUTORIA" in output
    assert "labs  managed  README.md  yes" in output
    assert f"base  local  {outside.as_posix()}  no" in output


def test_add_source_saves_internal_uri_as_relative(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    actions = SourceActions(make_settings(), repo)

    assert actions.add_source("python", (tmp_path / "python" / "README.md").as_posix()) is True

    data = read_config(repo)
    assert data["profile"]["sources"]["python"]["uri"] == "python/README.md"


def test_add_source_with_authoring_sets_authoring_atomically(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    actions = SourceActions(make_settings(), repo)

    assert actions.add_source("python", "python/README.md", authoring=True) is True

    data = read_config(repo)
    assert data["profile"]["authoring_source"] == "python"
    assert data["profile"]["sources"]["python"]["uri"] == "python/README.md"


def test_add_source_with_external_authoring_rolls_back(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    outside = tmp_path.parent / "source-actions-authoring" / "README.md"
    outside.parent.mkdir(exist_ok=True)
    outside.write_text("# outside\n", encoding="utf-8")
    actions = SourceActions(make_settings(), repo)

    assert actions.add_source("outside", outside.as_posix(), authoring=True) is False

    assert repo.data.get_source("outside") is None
    assert repo.data.authoring_source == "labs"
    assert not repo.paths.config_file.exists()


def test_set_authoring_source_changes_only_reference(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    repo.data.set_source(Remote.from_uri("python", "python/README.md"))
    actions = SourceActions(make_settings(), repo)

    assert actions.set_authoring_source("python") is True

    data = read_config(repo)
    assert data["profile"]["authoring_source"] == "python"


def test_update_source_uri_refuses_to_make_authoring_source_external(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    outside = tmp_path.parent / "source-actions-update" / "README.md"
    outside.parent.mkdir(exist_ok=True)
    outside.write_text("# outside\n", encoding="utf-8")
    actions = SourceActions(make_settings(), repo)

    assert actions.update_source("labs", outside.as_posix()) is False

    assert repo.data.get_source("labs").path_or_url == "README.md"  # type: ignore[union-attr]


def test_update_source_uri_recalculates_context_and_saves_relative(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    actions = SourceActions(make_settings(), repo)

    assert actions.update_source("labs", "outro/README.md") is True

    data = read_config(repo)
    assert data["profile"]["sources"]["labs"]["uri"] == "outro/README.md"


def test_remove_source_refuses_authoring_source(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    actions = SourceActions(make_settings(), repo)

    assert actions.remove_source("labs") is False

    assert repo.data.get_source("labs") is not None


def test_remove_source_does_not_delete_materialized_folder(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    materialized = tmp_path / "python" / "task"
    materialized.mkdir(parents=True)
    repo.data.set_source(Remote.from_uri("python", "python/README.md"))
    actions = SourceActions(make_settings(), repo)

    assert actions.remove_source("python") is True

    assert materialized.exists()
    assert repo.data.get_source("python") is None


def test_external_path_is_preserved_when_saved(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    outside = tmp_path.parent / "source-actions-external" / "README.md"
    outside.parent.mkdir(exist_ok=True)
    outside.write_text("# outside\n", encoding="utf-8")
    actions = SourceActions(make_settings(), repo)

    assert actions.add_source("base", outside.as_posix()) is True

    data = read_config(repo)
    assert data["profile"]["sources"]["base"]["uri"] == outside.as_posix()


def test_git_url_context_is_preserved_without_new_string_classifier(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    actions = SourceActions(make_settings(), repo)
    def mock_git_clone(_link: str) -> bool:
        return True
    def mock_git_hub_url_to_path(_url: str, load_git: bool) -> tuple[Path, bool]:
        return tmp_path / "README.md", True
    monkeypatch.setattr(actions, "git_clone_repository", mock_git_clone)
    monkeypatch.setattr(repo.git_cache, "git_hub_url_to_path", mock_git_hub_url_to_path)
    (tmp_path / "README.md").write_text("# git\n", encoding="utf-8")

    assert actions.add_source("fup", "https://github.com/qxcodefup/arcade/blob/main/README.md") is True

    source = repo.data.get_source("fup")
    assert source is not None
    assert source.source_type == SourceType.GIT_SOURCE
    data = read_config(repo)
    assert data["profile"]["sources"]["fup"]["uri"] == "https://github.com/qxcodefup/arcade/blob/main/README.md"
