from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

import tko.repository.repository_paths as rep_paths_module
import tko.repository.repository as repository_module
from tko.repository.repository_paths import RepositoryPaths
from tko.repository.repository import Repository


def test_repository_uses_recursive_parent_when_found(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    parent_repo = tmp_path / "parent"
    child = parent_repo / "nested"
    child.mkdir(parents=True)

    def fake_search(folder: Path) -> Path:
        _ = folder
        return parent_repo

    monkeypatch.setattr(repository_module.RepositoryPaths, "rec_search_for_repo_parents", fake_search)

    repo = Repository(child)

    assert repo.paths.root_dir == parent_repo
    assert repo.logger.history.get_log_folder() == parent_repo / ".tko" / "log"


def test_found_and_inside_repo_checks(tmp_path: Path) -> None:
    repo = Repository(tmp_path, recursive_search=False)

    assert repo.found() is False
    assert repo.root_dir == tmp_path

    config = repo.paths.config_file
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("version: '0.2'\n", encoding="utf-8")

    assert repo.found() is True


def test_task_folder_helpers_handle_prefixed_and_plain_labels(tmp_path: Path) -> None:
    repo = Repository(tmp_path, recursive_search=False)
    task_folder = tmp_path / "disc" / "task1"
    task_folder.mkdir(parents=True)

    assert repo.get_task_folder_for_label("disc@task1") == task_folder
    assert repo.get_task_folder_for_label("task2") == tmp_path / "task2"
    assert repo.is_task_folder(task_folder) is False
    assert repo.is_task_folder(tmp_path / "task1") is True


def test_create_default_sandbox_source_binds_workspace_and_cache(tmp_path: Path) -> None:
    repo = Repository(tmp_path, recursive_search=False)

    source = repo.create_default_sandbox_source()
    source.git_cache = repo.git_cache
    source.root_dir = repo.root_dir

    assert source.is_sandbox is True
    assert source.data.name == ""
    assert source.data.target == "base"
    assert source.path.work_dir == (tmp_path / "base").resolve()


def test_set_global_cache_uses_user_cache_folder(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    repo = Repository(tmp_path, recursive_search=False)
    original = RepositoryPaths.use_global_cache_folder

    def fake_user_cache_dir(app_name: str) -> str:
        _ = app_name
        return "/tmp/global-tko"

    monkeypatch.setattr(rep_paths_module, "user_cache_dir", fake_user_cache_dir)
    monkeypatch.setattr(repository_module.RepositoryPaths, "use_global_cache_folder", False)
    try:
        repo.set_global_cache()
        assert repository_module.RepositoryPaths.use_global_cache_folder is True
        assert repo.git_cache.cache_dir == Path("/tmp/global-tko") / "cache"
    finally:
        repository_module.RepositoryPaths.use_global_cache_folder = original