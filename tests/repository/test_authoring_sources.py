from __future__ import annotations

import tomllib
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tko.config.run_settings import RunSettings
from tko.config.settings import Settings
from tko.repository.remote import Source, SourceType
from tko.repository.repository import Repository
from tko.repository.repository_config import RepositoryLoader
from tko.repository.repository_data import RepositoryData
from tko.repository.repository_starter import RepositoryStarter
from tko.repository.task_migration import TaskDataMigration
from tko.i18n import set_language


@pytest.fixture(autouse=True)
def restore_language():
    yield
    set_language("pt")


def make_repo(tmp_path: Path) -> Repository:
    return Repository(tmp_path, RunSettings(changedir=tmp_path), git_cache=None, recursive_search=False)


def read_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def test_new_workspace_creates_labs_readme_and_authoring_source(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    settings = cast(Settings, SimpleNamespace(rs=RunSettings(changedir=tmp_path)))
    def mock_check_lang(settings: object, repo: object, selected: str | None = None) -> str:
        return selected or "py"
    monkeypatch.setattr(
        "tko.repository.repository_starter.LanguageSetter.check_prog_lang_in_text_mode",
        mock_check_lang,
    )

    starter = RepositoryStarter(settings=settings, language="py", skip_add_remote=True, force_location=True)

    assert starter.execute() is True
    assert (tmp_path / "README.md").exists()
    assert (tmp_path / "labs").is_dir()
    data = read_toml(tmp_path / ".tko" / "repository.toml")
    assert data["profile"]["authoring_source"] == "labs"
    assert data["profile"]["sources"]["labs"]["uri"] == "README.md"


def test_relative_internal_uri_loads_as_managed_source(tmp_path: Path) -> None:
    data = RepositoryData(tmp_path)
    data.load_from_dict(
        {
            "profile": {
                "authoring_source": "labs",
                "sources": {"labs": {"uri": "README.md"}},
            }
        }
    )

    remote = data.get_source("labs")
    assert remote is not None
    assert remote.is_editable is True
    assert remote.path_or_url == "README.md"


def test_save_normalizes_absolute_internal_path_to_relative_uri(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    repo.data.set_source(Source.from_local_file("python", tmp_path / "python" / "README.md"))

    RepositoryLoader(repo).save(force=True)

    data = read_toml(repo.paths.config_file)
    assert data["profile"]["sources"]["python"]["uri"] == "python/README.md"


def test_save_preserves_git_url(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    remote = Source.from_git_file("fup", "https://github.com/qxcodefup/arcade/blob/main/README.md")
    assert remote is not None
    repo.data.set_source(remote)

    RepositoryLoader(repo).save(force=True)

    data = read_toml(repo.paths.config_file)
    assert data["profile"]["sources"]["fup"]["uri"] == "https://github.com/qxcodefup/arcade/blob/main/README.md"


def test_source_classification_by_uri(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    outside = tmp_path.parent / "outside-source" / "README.md"
    git = Source.from_uri("fup", "https://github.com/qxcodefup/arcade/blob/main/README.md")

    internal = Source.from_uri("labs", "README.md")
    external = Source.from_uri("shared", outside.as_posix())

    assert repo.source_resolver.is_local_internal(internal) is True
    assert repo.source_resolver.is_local_internal(external) is False
    assert git.source_type == SourceType.GIT_SOURCE


def test_rejects_external_authoring_source(tmp_path: Path) -> None:
    set_language("en")
    data = RepositoryData(tmp_path)
    external = tmp_path.parent / "outside-authoring" / "README.md"

    with pytest.raises(ValueError, match="Source 'shared' points outside the workspace"):
        data.load_from_dict(
            {
                "profile": {
                    "authoring_source": "shared",
                    "sources": {"shared": {"uri": external.as_posix()}},
                }
            }
        )


def test_rejects_git_authoring_source_as_external(tmp_path: Path) -> None:
    set_language("en")
    data = RepositoryData(tmp_path)

    with pytest.raises(ValueError, match="Source 'fup' is external and cannot be used for authoring"):
        data.load_from_dict(
            {
                "profile": {
                    "authoring_source": "fup",
                    "sources": {"fup": {"uri": "https://github.com/qxcodefup/arcade/blob/main/README.md"}},
                }
            }
        )


def test_rejects_missing_authoring_source(tmp_path: Path) -> None:
    set_language("en")
    data = RepositoryData(tmp_path)

    with pytest.raises(ValueError, match="Source 'missing' was not found"):
        data.load_from_dict(
            {
                "profile": {
                    "authoring_source": "missing",
                    "sources": {"labs": {"uri": "README.md"}},
                }
            }
        )


def test_migrates_legacy_sandbox_fields_and_preserves_old_names(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    legacy = repo.paths.legacy_config_file
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text(
        "version: '0.2'\n"
        "sandbox_name: sandbox\n"
        "sandbox_index: sandbox.md\n"
        "expanded:\n"
        "  - sandbox@old\n"
        "selected: sandbox@old\n",
        encoding="utf-8",
    )

    # Identity and configuration conversion happen in one offline migration.
    backup = TaskDataMigration(tmp_path, {"sandbox@old": "sandbox@old"}).inspect().apply()
    RepositoryLoader(repo).load()

    assert not legacy.exists()
    assert backup is not None
    assert (backup / "before/.tko/repository.yaml").is_file()
    data = read_toml(repo.paths.config_file)
    assert data["profile"]["authoring_source"] == "sandbox"
    assert data["profile"]["sources"]["sandbox"]["uri"] == "sandbox.md"
    assert "labs" not in data["profile"]["sources"]
    assert data["state"]["selected"] == "sandbox@old"


def test_migrates_legacy_source_list_with_writable_sandbox(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    legacy = repo.paths.legacy_config_file
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text(
        "version: '0.2'\n"
        "sources:\n"
        "- name: sandbox\n"
        "  target: sandbox\n"
        "  index: README.md\n"
        "  type: local\n"
        "  writeable: true\n"
        "- name: fup\n"
        "  target: https://github.com/qxcodefup/arcade.git\n"
        "  index: README.md\n"
        "  type: git\n"
        "  writeable: false\n"
        "- name: eval1\n"
        "  target: https://github.com/senapk/fup_26_1_eval_1.git\n"
        "  index: README.md\n"
        "  type: git\n"
        "  writeable: false\n"
        "expanded:\n"
        "- fup@mat\n"
        "flags:\n"
        "  inbox: all\n"
        "  panel: skills\n"
        "  task_graph_mode: time\n"
        "  show_time: 'true'\n"
        "audit:\n"
        "  enabled: true\n"
        "  interval_seconds: null\n"
        "lang: go\n"
        "selected: fup@tetris\n"
        "selected_index: 23\n",
        encoding="utf-8",
    )

    backup = TaskDataMigration(tmp_path, {"fup@mat": "fup@mat", "fup@tetris": "fup@tetris"}).inspect().apply()
    RepositoryLoader(repo).load()

    data = read_toml(repo.paths.config_file)
    assert data["profile"]["authoring_source"] == "sandbox"
    assert data["profile"]["sources"] == {
        "sandbox": {"uri": "sandbox/README.md"},
        "fup": {"uri": "https://github.com/qxcodefup/arcade/blob/main/README.md"},
        "eval1": {"uri": "https://github.com/senapk/fup_26_1_eval_1/blob/main/README.md"},
    }
    assert data["profile"]["audit"] == {"enabled": True}
    assert data["preferences"] == {
        "inbox": "all",
        "panel": "skills",
        "task_graph_mode": "time",
        "show_time": "true",
        "lang": "go",
    }
    assert data["state"] == {
        "expanded": ["fup@mat"],
        "selected": "fup@tetris",
        "selected_index": 23,
    }
    assert backup is not None
    assert (backup / "before/.tko/repository.yaml").is_file()


def test_migration_keeps_toml_when_yaml_also_exists(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    repo.paths.config_file.parent.mkdir(parents=True, exist_ok=True)
    repo.paths.config_file.write_text(
        'version = "0.3"\n'
        '[profile]\n'
        'authoring_source = "labs"\n'
        '[profile.sources.labs]\n'
        'uri = "README.md"\n',
        encoding="utf-8",
    )
    repo.paths.legacy_config_file.write_text(
        "sandbox_name: sandbox\n"
        "sandbox_index: sandbox.md\n",
        encoding="utf-8",
    )

    TaskDataMigration(tmp_path).inspect().apply()
    RepositoryLoader(repo).load()

    assert repo.data.authoring_source == "labs"
    assert not repo.paths.legacy_config_file.exists()


def test_profile_update_preserves_preferences_and_state(tmp_path: Path) -> None:
    data = RepositoryData(tmp_path)
    data.flags = {"panel": "logs"}
    data.selected = "labs@one"
    data.expanded = ["labs@one"]

    data.update_profile_from_dict(
        {
            "authoring_source": "labs",
            "sources": {"labs": {"uri": "README.md"}, "fup": {"uri": "https://github.com/qxcodefup/arcade/blob/main/README.md"}},
        }
    )

    assert data.flags == {"panel": "logs"}
    assert data.selected == "labs@one"
    assert data.expanded == ["labs@one"]
    assert data.get_source("fup") is not None
