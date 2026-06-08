from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

import tko.repository.repository as repository_module
from tko.config.run_settings import RunSettings
from tko.config.user_data import UserData
from tko.repository.repository import Repository


def make_run_settings(tmp_path: Path, local_cache: bool = True) -> RunSettings:
    return RunSettings(changedir=tmp_path, local_cache=local_cache)


def test_repository_uses_recursive_parent_when_found(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    parent_repo = tmp_path / "parent"
    child = parent_repo / "nested"
    child.mkdir(parents=True)

    def fake_search(folder: Path) -> Path:
        _ = folder
        return parent_repo

    monkeypatch.setattr(repository_module.RepositoryPaths, "rec_search_for_repo_parents", fake_search)

    repo = Repository(child, make_run_settings(child))

    assert repo.paths.root_dir == parent_repo
    assert repo.logger.history.get_log_folder() == parent_repo / ".tko" / "log"


def test_found_and_inside_repo_checks(tmp_path: Path) -> None:
    repo = Repository(tmp_path, make_run_settings(tmp_path), recursive_search=False)

    assert repo.found() is False
    assert repo.root_dir == tmp_path

    config = repo.paths.config_file
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("version: '0.2'\n", encoding="utf-8")

    assert repo.found() is True


def test_task_folder_helpers_handle_prefixed_and_plain_labels(tmp_path: Path) -> None:
    repo = Repository(tmp_path, make_run_settings(tmp_path), recursive_search=False)
    task_folder = tmp_path / "disc" / "task1"
    task_folder.mkdir(parents=True)

    assert repo.get_task_folder_for_label("disc@task1") == task_folder
    assert repo.get_task_folder_for_label("task2") == tmp_path / "task2"
    assert repo.is_task_folder(task_folder) is False
    assert repo.is_task_folder(tmp_path / "task1") is True


def test_create_default_sandbox_source_binds_workspace_and_cache(tmp_path: Path) -> None:
    repo = Repository(tmp_path, make_run_settings(tmp_path), recursive_search=False)

    source = repo.create_default_sandbox_source()
    source.git_cache = repo.git_cache
    source.root_dir = repo.root_dir

    assert source.is_sandbox is True
    assert source.data.name == "sandbox"
    assert source.data.target == "sandbox"
    assert source.path.work_dir == (tmp_path / "sandbox").resolve()


def test_repository_uses_global_cache_when_local_cache_is_disabled(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    global_cache = tmp_path / "global-cache"

    monkeypatch.setattr(UserData, "global_cache_dir", lambda: global_cache)

    repo = Repository(tmp_path, make_run_settings(tmp_path, local_cache=False), recursive_search=False)

    assert repo.git_cache.cache_dir == global_cache
