from pathlib import Path
from types import SimpleNamespace
from typing import Callable, cast

from _pytest.monkeypatch import MonkeyPatch
import yaml

import tko.repository.repository_starter as rep_starter_module
from tko.config.settings import Settings
from tko.repository.repository_paths import RepositoryPaths
from tko.repository.repository_starter import RepositoryStarter


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


class FakeLoader:
    def __init__(self, on_save: Callable[[], None]):
        self.on_save = on_save

    def save_config(self) -> None:
        self.on_save()


def make_settings() -> Settings:
    return cast(Settings, SimpleNamespace())


def test_create_repository_returns_none_when_user_cancels_reset(monkeypatch: MonkeyPatch, tmp_path: Path):
    def fake_parent_search(folder: Path) -> Path:
        _ = folder
        return tmp_path

    monkeypatch.setattr(rep_starter_module.RepositoryPaths, "rec_search_for_repo_parents", fake_parent_search)
    monkeypatch.setattr("builtins.input", lambda: "n")

    starter = RepositoryStarter(settings=make_settings(), folder=tmp_path)

    repo = starter.create_repository()

    assert repo is None


def test_create_repository_uses_parent_repo_when_user_accepts_overwrite(monkeypatch: MonkeyPatch, tmp_path: Path):
    parent_repo = tmp_path / "parent"
    child_folder = parent_repo / "child"
    child_folder.mkdir(parents=True)
    created_folders: list[Path] = []

    def fake_parent_search(folder: Path) -> Path:
        _ = folder
        return parent_repo

    monkeypatch.setattr(rep_starter_module.RepositoryPaths, "rec_search_for_repo_parents", fake_parent_search)
    monkeypatch.setattr("builtins.input", lambda: "s")

    def fake_repository(folder: Path) -> SimpleNamespace:
        created_folders.append(folder)
        return SimpleNamespace(folder=folder)

    monkeypatch.setattr(rep_starter_module, "Repository", fake_repository)

    starter = RepositoryStarter(settings=make_settings(), folder=child_folder)

    repo = starter.create_repository()

    assert repo is not None
    assert starter.folder == parent_repo
    assert created_folders == [parent_repo]


def test_create_repository_returns_none_when_sub_repositories_exist(monkeypatch: MonkeyPatch, tmp_path: Path):
    nested_repo = tmp_path / "discipline"

    def fake_parent_search(folder: Path) -> None:
        _ = folder
        return None

    def fake_subdir_search(folder: Path) -> list[Path]:
        _ = folder
        return [nested_repo]

    monkeypatch.setattr(rep_starter_module.RepositoryPaths, "rec_search_for_repo_parents", fake_parent_search)
    monkeypatch.setattr(rep_starter_module.RepositoryPaths, "rec_search_for_repo_subdir", fake_subdir_search)

    starter = RepositoryStarter(settings=make_settings(), folder=tmp_path)

    repo = starter.create_repository()

    assert repo is None


def test_execute_returns_false_when_repository_creation_fails(monkeypatch: MonkeyPatch, tmp_path: Path):
    def fake_create_repository(self: RepositoryStarter) -> None:
        _ = self
        return None

    monkeypatch.setattr(RepositoryStarter, "create_repository", fake_create_repository)

    starter = RepositoryStarter(settings=make_settings(), folder=tmp_path, language="py")

    assert starter.execute() is False


def test_execute_sets_language_recreates_cache_and_saves_config(monkeypatch: MonkeyPatch, tmp_path: Path):
    repo = FakeRepo(tmp_path)
    calls: dict[str, object] = {
        "rmtree": None,
        "makedirs": None,
        "saved": False,
        "language_prompt": False,
    }

    def fake_create_repository(self: RepositoryStarter) -> FakeRepo:
        _ = self
        return repo

    def fake_rmtree(path: Path) -> None:
        calls["rmtree"] = path

    def fake_loader(repo_arg: object) -> FakeLoader:
        _ = repo_arg
        return FakeLoader(lambda: calls.__setitem__("saved", True))

    def fake_check_lang_in_text_mode(settings: Settings, repo_arg: object) -> None:
        _ = (settings, repo_arg)
        calls["language_prompt"] = True

    monkeypatch.setattr(RepositoryStarter, "create_repository", fake_create_repository)
    monkeypatch.setattr(rep_starter_module.shutil, "rmtree", fake_rmtree)
    monkeypatch.setattr(rep_starter_module, "RepositoryLoader", fake_loader)
    monkeypatch.setattr(
        rep_starter_module.LanguageSetter,
        "check_lang_in_text_mode",
        fake_check_lang_in_text_mode,
    )

    starter = RepositoryStarter(settings=make_settings(), folder=tmp_path, language="py")
    repo.paths.cache_folder.mkdir(parents=True, exist_ok=True)

    assert starter.execute() is True
    assert repo.data.lang == "py"
    assert repo.saved_source is not None
    assert calls["rmtree"] == tmp_path / ".tko" / "cache"
    assert (tmp_path / ".tko" / "cache").exists()
    assert calls["saved"] is True
    assert calls["language_prompt"] is False


def test_execute_uses_language_setter_when_language_is_missing(monkeypatch: MonkeyPatch, tmp_path: Path):
    repo = FakeRepo(tmp_path)
    calls = {"language_prompt": False}

    def fake_create_repository(self: RepositoryStarter) -> FakeRepo:
        _ = self
        return repo

    def fake_loader(repo_arg: object) -> FakeLoader:
        _ = repo_arg
        return FakeLoader(lambda: None)

    def fake_check_lang_in_text_mode(settings: Settings, repo_arg: object) -> None:
        _ = settings
        calls["language_prompt"] = repo_arg is repo

    monkeypatch.setattr(RepositoryStarter, "create_repository", fake_create_repository)
    monkeypatch.setattr(rep_starter_module, "RepositoryLoader", fake_loader)
    monkeypatch.setattr(
        rep_starter_module.LanguageSetter,
        "check_lang_in_text_mode",
        fake_check_lang_in_text_mode,
    )

    starter = RepositoryStarter(settings=make_settings(), folder=tmp_path)

    assert starter.execute() is True
    assert calls["language_prompt"] is True


def test_execute_integration_creates_repository_config_with_default_sandbox(tmp_path: Path):
    repo_folder = tmp_path / "repo"
    repo_folder.mkdir()

    starter = RepositoryStarter(settings=make_settings(), folder=repo_folder, language="py")

    assert starter.execute() is True

    config_file = repo_folder / RepositoryPaths.CONFIG_FOLDER / RepositoryPaths.CFG_FILE
    cache_folder = repo_folder / RepositoryPaths.CONFIG_FOLDER / RepositoryPaths.CACHE_FOLDER
    assert config_file.exists()
    assert cache_folder.exists()

    data = yaml.safe_load(config_file.read_text(encoding="utf-8"))

    assert data["version"] == "0.2"
    assert data["lang"] == "py"
    assert len(data["sources"]) == 1
    sandbox = data["sources"][0]
    assert sandbox["name"] == "sandbox"
    assert sandbox["target"] == "base"
    assert sandbox["index"] == "../README.md"
    assert sandbox["type"] == "local"
    assert sandbox["writeable"] is True