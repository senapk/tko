from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

import tko.repository.repository as repository_module
from tko.config.run_settings import RunSettings
from tko.config.user_data import UserData
from tko.repository.repository import Repository


def make_run_settings(tmp_path: Path) -> RunSettings:
    return RunSettings(changedir=tmp_path)


def test_repository_uses_recursive_parent_when_found(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    parent_repo = tmp_path / "parent"
    child = parent_repo / "nested"
    child.mkdir(parents=True)

    def fake_search(folder: Path) -> Path:
        _ = folder
        return parent_repo

    monkeypatch.setattr(repository_module.RepositoryPaths, "rec_search_for_repo_parents", fake_search)

    repo = Repository(child, make_run_settings(child), git_cache=None)

    assert repo.paths.root_dir == parent_repo
    assert repo.logger.history.get_log_folder() == parent_repo / ".tko" / "log"


def test_found_and_inside_repo_checks(tmp_path: Path) -> None:
    repo = Repository(tmp_path, make_run_settings(tmp_path), git_cache=None, recursive_search=False)

    assert repo.found() is False
    assert repo.root_dir == tmp_path

    config = repo.paths.config_file
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text('version = "0.3"\n', encoding="utf-8")

    assert repo.found() is True


def test_task_folder_helpers_handle_prefixed_and_plain_labels(tmp_path: Path) -> None:
    repo = Repository(tmp_path, make_run_settings(tmp_path), git_cache=None, recursive_search=False)
    task_folder = tmp_path / "disc" / "task1"
    task_folder.mkdir(parents=True)

    assert repo.get_task_folder_for_label("disc@task1") == task_folder
    assert repo.get_task_folder_for_label("task2") == tmp_path / "task2"
    assert repo.is_task_folder(task_folder) is False
    assert repo.is_task_folder(tmp_path / "task1") is True


def test_task_folder_helper_does_not_add_labs_prefix(tmp_path: Path) -> None:
    repo = Repository(tmp_path, make_run_settings(tmp_path), git_cache=None, recursive_search=False)
    canonical = tmp_path / "disc" / "labs" / "carro"
    canonical.mkdir(parents=True)

    assert repo.get_task_folder_for_label("disc@carro") == tmp_path / "disc/carro"


def test_task_folder_helper_does_not_remove_labs_prefix(tmp_path: Path) -> None:
    repo = Repository(tmp_path, make_run_settings(tmp_path), git_cache=None, recursive_search=False)
    legacy = tmp_path / "disc" / "carro"
    legacy.mkdir(parents=True)

    assert repo.get_task_folder_for_label("disc@labs/carro") == tmp_path / "disc/labs/carro"


def test_authoring_remote_resolves_against_workspace(tmp_path: Path) -> None:
    repo = Repository(tmp_path, make_run_settings(tmp_path), git_cache=None, recursive_search=False)

    remote = repo.data.get_authoring_source()
    assert remote is not None
    index_file, found = repo.source_resolver.resolve_index_file(remote, load_git=False)

    assert remote.name == "labs"
    assert remote.path_or_url == "README.md"
    assert remote.is_editable is True
    assert index_file == (tmp_path / "README.md").resolve()
    assert found is False


def test_repository_uses_global_cache_when_local_cache_is_disabled(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    global_cache = tmp_path / "global-cache"

    monkeypatch.setattr(UserData, "global_cache_dir", lambda: global_cache)

    repo = Repository(tmp_path, make_run_settings(tmp_path), git_cache=None, recursive_search=False)

    assert repo.git_cache.cache_dir == global_cache


def test_task_folder_helper_uses_exact_local_task_location(tmp_path: Path) -> None:
    from tko.game.task import Task
    from tko.game.task_location import TaskLocation
    from tko.game.task_enums import EvalMode

    repo: Repository = Repository(tmp_path, make_run_settings(tmp_path), None, recursive_search=False)
    task: Task = Task()
    task.basic.source_name = "course"
    task.basic.key = "labs/animal"
    task.location = TaskLocation(index_path=tmp_path / "README.md", raw_link="labs/animal/README.md", eval=EvalMode.DIFF)
    repo.game.tasks[task.basic.full_key] = task
    assert repo.get_task_folder_for_label("course@labs/animal") == tmp_path / "labs/animal"
