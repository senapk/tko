from pathlib import Path
from types import SimpleNamespace
from typing import Callable, cast

from _pytest.monkeypatch import MonkeyPatch

import tko.repository.repository_starter as rep_starter_module
from tko.config.run_settings import RunSettings
from tko.config.settings import Settings
from tko.repository.repository_starter import RepositoryStarter
from tko.util.console import Console


class FakeSource:
    def __init__(self, workspace: Path):
        self.workspace = workspace

    def get_workspace(self) -> Path:
        return self.workspace


class FakeRepo:
    def __init__(self, root: Path):
        self.root = root
        self.saved_source = None
        self.data = SimpleNamespace(lang="", set_remote=self._set_source)
        self.paths = SimpleNamespace(cache_folder=root / ".tko" / "cache")

    def _set_source(self, source: FakeSource):
        self.saved_source = source

    def create_default_sandbox_source(self) -> FakeSource:
        return FakeSource(self.root / "base")


class FakeRepositoryConfig:
    def __init__(self, on_save: Callable[[], None]):
        self.on_save = on_save

    def save(self) -> None:
        self.on_save()


def make_settings(tmp_path: Path) -> Settings:
    return cast(Settings, SimpleNamespace(rs=RunSettings(changedir=tmp_path, local_cache=True)))


def test_validate_path_returns_false_when_user_cancels_reset(monkeypatch: MonkeyPatch, tmp_path: Path):
    def fake_parent_search(folder: Path) -> Path:
        _ = folder
        return tmp_path

    monkeypatch.setattr(rep_starter_module.RepositoryPaths, "rec_search_for_repo_parents", fake_parent_search)
    monkeypatch.setattr("builtins.input", lambda: "n")

    starter = RepositoryStarter(settings=make_settings(tmp_path), language=None, skip_add_remote=True)

    is_valid = starter.validate_path()

    assert is_valid is False


def test_validate_path_uses_parent_repo_when_user_accepts_overwrite(monkeypatch: MonkeyPatch, tmp_path: Path):
    parent_repo = tmp_path / "parent"
    child_folder = parent_repo / "child"
    child_folder.mkdir(parents=True)

    def fake_parent_search(folder: Path) -> Path:
        _ = folder
        return parent_repo

    monkeypatch.setattr(rep_starter_module.RepositoryPaths, "rec_search_for_repo_parents", fake_parent_search)
    monkeypatch.setattr("builtins.input", lambda: "y")

    with Console.capture() as _:
        starter = RepositoryStarter(settings=make_settings(child_folder), language=None, skip_add_remote=True, force_location=True)
        is_valid = starter.validate_path()

    assert is_valid is True
    assert starter.folder == parent_repo


def test_validate_path_returns_false_when_sub_repositories_exist(monkeypatch: MonkeyPatch, tmp_path: Path):
    nested_repo = tmp_path / "discipline"

    def fake_parent_search(folder: Path) -> None:
        _ = folder
        return None

    def fake_subdir_search(folder: Path) -> list[Path]:
        _ = folder
        return [nested_repo]

    monkeypatch.setattr(rep_starter_module.RepositoryPaths, "rec_search_for_repo_parents", fake_parent_search)
    monkeypatch.setattr(rep_starter_module.RepositoryPaths, "rec_search_for_repo_subdir", fake_subdir_search)

    starter = RepositoryStarter(settings=make_settings(tmp_path), language=None, skip_add_remote=True)

    is_valid = starter.validate_path()

    assert is_valid is False


def test_execute_returns_false_when_path_is_not_valid(monkeypatch: MonkeyPatch, tmp_path: Path):
    def fake_validate_path(self: RepositoryStarter) -> bool:
        _ = self
        return False

    monkeypatch.setattr(RepositoryStarter, "validate_path", fake_validate_path)

    starter = RepositoryStarter(settings=make_settings(tmp_path), language="py", skip_add_remote=True)

    assert starter.execute() is False


def test_execute_sets_language_recreates_cache_and_saves_config(monkeypatch: MonkeyPatch, tmp_path: Path):
    repo = FakeRepo(tmp_path)
    created_folders: list[Path] = []
    calls: dict[str, object] = {
        "saved": False,
        "language_prompt": False,
        "printed_end": False,
    }

    def fake_repository(folder: Path, rs: RunSettings) -> FakeRepo:
        _ = rs
        created_folders.append(folder)
        return repo

    def fake_repository_config(repo_arg: object) -> FakeRepositoryConfig:
        _ = repo_arg
        return FakeRepositoryConfig(lambda: calls.__setitem__("saved", True))

    def fake_check_lang_in_text_mode(settings: Settings, repo_arg: object, selected: str | None = None) -> str:
        _ = (settings, repo_arg)
        calls["language_prompt"] = True
        return selected or "py"

    monkeypatch.setattr(rep_starter_module, "Repository", fake_repository)
    monkeypatch.setattr(rep_starter_module, "RepositoryConfig", fake_repository_config)
    monkeypatch.setattr(
        rep_starter_module.LanguageSetter,
        "check_prog_lang_in_text_mode",
        fake_check_lang_in_text_mode,
    )

    starter = RepositoryStarter(settings=make_settings(tmp_path), language="py", skip_add_remote=True, force_location=True)
    repo.paths.cache_folder.mkdir(parents=True, exist_ok=True)

    with Console.capture() as _:
        assert starter.execute() is True

    assert starter.repo is repo
    assert starter.language == "py"
    assert repo.saved_source is not None
    assert created_folders == [tmp_path]
    assert calls["saved"] is True
    assert calls["language_prompt"] is True




# def test_execute_integration_creates_repository_config_with_default_sandbox(tmp_path: Path):
#     repo_folder = tmp_path / "repo"
#     repo_folder.mkdir()

#     starter = RepositoryStarter(settings=make_settings(), folder=repo_folder, language="py", skip=True)

#     assert starter.execute() is True

#     config_file = repo_folder / RepositoryPaths.CONFIG_FOLDER / RepositoryPaths.CFG_FILE
#     cache_folder = repo_folder / RepositoryPaths.CONFIG_FOLDER / RepositoryPaths.CACHE_FOLDER
#     assert config_file.exists()
#     assert cache_folder.exists()

#     data = yaml.safe_load(config_file.read_text(encoding="utf-8"))

#     assert data["version"] == "0.2"
#     assert data["lang"] == "py"
#     assert len(data["sources"]) == 1
#     sandbox = data["sources"][0]
#     assert sandbox["name"] == "sandbox"
#     assert sandbox["target"] == "base"
#     assert sandbox["index"] == "../README.md"
#     assert sandbox["type"] == "local"
#     assert sandbox["writeable"] is True
