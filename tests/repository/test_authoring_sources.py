from __future__ import annotations

import tomllib
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tko.config.run_settings import RunSettings
from tko.config.settings import Settings
from tko.floating.floating_input_text import FloatingInputText
from tko.game.game import Game
from tko.play.draft_creator import DraftCreator
from tko.repository.remote import Remote, SourceType
from tko.repository.repository import Repository
from tko.repository.repository_config import RepositoryLoader
from tko.repository.repository_data import RepositoryData
from tko.repository.repository_starter import RepositoryStarter
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

    remote = data.get_remote("labs")
    assert remote is not None
    assert remote.is_editable is True
    assert remote.path_or_url == "README.md"


def test_save_normalizes_absolute_internal_path_to_relative_uri(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    repo.data.set_remote(Remote.from_local_file("python", tmp_path / "python" / "README.md"))

    RepositoryLoader(repo).save(force=True)

    data = read_toml(repo.paths.config_file)
    assert data["profile"]["sources"]["python"]["uri"] == "python/README.md"


def test_save_preserves_git_url(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    remote = Remote.from_git_file("fup", "https://github.com/qxcodefup/arcade/blob/main/README.md")
    assert remote is not None
    repo.data.set_remote(remote)

    RepositoryLoader(repo).save(force=True)

    data = read_toml(repo.paths.config_file)
    assert data["profile"]["sources"]["fup"]["uri"] == "https://github.com/qxcodefup/arcade/blob/main/README.md"


def test_source_classification_by_uri(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    outside = tmp_path.parent / "outside-source" / "README.md"
    git = Remote.from_uri("fup", "https://github.com/qxcodefup/arcade/blob/main/README.md")

    internal = Remote.from_uri("labs", "README.md")
    external = Remote.from_uri("shared", outside.as_posix())

    assert repo.remote_resolver.is_local_internal(internal) is True
    assert repo.remote_resolver.is_local_internal(external) is False
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


def test_create_lab_uses_authoring_source_folder_index_and_identity(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    repo.data.lang = "py"
    (tmp_path / "README.md").write_text("# labs\n\n", encoding="utf-8")
    fman = SimpleNamespace(items=[], add_floating=lambda item: fman.items.append(item))  # type: ignore[attr-defined]
    tree = SimpleNamespace(state=SimpleNamespace(selected="", expanded=set()))  # type: ignore[arg-type]
    game = Game()
    def mock_get_languages_with_drafts() -> dict[str, Any]:
        return {}
    def mock_get_languages_settings() -> object:
        return SimpleNamespace(get_languages_with_drafts=mock_get_languages_with_drafts)
    settings_obj = cast(Settings, SimpleNamespace(get_languages_settings=mock_get_languages_settings))
    creator = DraftCreator(repo, settings_obj, fman, tree, game, lambda: None)  # type: ignore[arg-type]

    creator.create_draft()
    floating = fman.items[-1]
    assert isinstance(floating, FloatingInputText)
    floating.action("Ponteiros @ponteiros")

    assert (tmp_path / "labs" / "ponteiros" / "README.md").exists()
    index = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "labs/ponteiros/README.md" in index
    assert tree.state.selected == "labs@ponteiros"
    assert repo.data.selected == "labs@ponteiros"


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

    RepositoryLoader(repo).load()

    assert not legacy.exists()
    assert Path(str(legacy) + ".backup").exists()
    data = read_toml(repo.paths.config_file)
    assert data["profile"]["authoring_source"] == "sandbox"
    assert data["profile"]["sources"]["sandbox"]["uri"] == "sandbox.md"
    assert "labs" not in data["profile"]["sources"]
    assert data["state"]["selected"] == "sandbox@old"


def test_toml_takes_precedence_when_yaml_also_exists(tmp_path: Path) -> None:
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

    RepositoryLoader(repo).load()

    assert repo.data.authoring_source == "labs"
    assert repo.paths.legacy_config_file.exists()


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
    assert data.get_remote("fup") is not None
