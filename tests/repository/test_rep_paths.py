from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

import tko.repository.rep_paths as rep_paths_module
from tko.repository.rep_paths import RepPaths


def test_walk_to_root_yields_path_until_filesystem_root(tmp_path: Path):
    start = tmp_path / "a" / "b"
    start.mkdir(parents=True)

    walked = list(RepPaths.walk_to_root(start))

    assert walked[0] == start.resolve()
    assert walked[-1] == Path("/")
    assert tmp_path.resolve() in walked


def test_rec_search_for_repo_parents_finds_nearest_parent_repository(tmp_path: Path):
    repo_root = tmp_path / "repo"
    nested = repo_root / "src" / "module"
    config_file = repo_root / RepPaths.CONFIG_FOLDER / RepPaths.CFG_FILE
    config_file.parent.mkdir(parents=True)
    config_file.write_text("version: '0.2'\n", encoding="utf-8")
    nested.mkdir(parents=True)

    found = RepPaths.rec_search_for_repo_parents(nested)

    assert found == repo_root


def test_rec_search_for_repo_subdir_finds_nested_repositories(tmp_path: Path):
    repo_a = tmp_path / "a"
    repo_b = tmp_path / "deep" / "b"
    for repo in [repo_a, repo_b]:
        config = repo / RepPaths.CONFIG_FOLDER / RepPaths.CFG_FILE
        config.parent.mkdir(parents=True)
        config.write_text("version: '0.2'\n", encoding="utf-8")

    found = RepPaths.rec_search_for_repo_subdir(tmp_path)

    assert sorted(found) == sorted([repo_a, repo_b])


def test_path_helpers_return_expected_locations(tmp_path: Path):
    paths = RepPaths(tmp_path)

    assert paths.get_root_dir() == tmp_path
    assert paths.get_track_folder() == tmp_path / ".tko" / "track"
    assert paths.get_log_folder() == tmp_path / ".tko" / "log"
    assert paths.get_cache_folder() == tmp_path / ".tko" / "cache"
    assert paths.get_track_task_folder("repo@task") == tmp_path / ".tko" / "track" / "repo@task"
    assert paths.get_config_folder() == tmp_path / ".tko"
    assert paths.get_config_file() == tmp_path / ".tko" / "repository.yaml"
    assert paths.get_config_backup_file() == tmp_path / ".tko" / "repository.yaml.backup"
    assert paths.get_old_history_file() == tmp_path / ".tko" / "history.csv"
    assert paths.get_repo_root_dir() == tmp_path


def test_get_cache_folder_uses_global_cache_when_enabled(monkeypatch: MonkeyPatch, tmp_path: Path):
    paths = RepPaths(tmp_path)

    def fake_user_cache_dir(app_name: str) -> str:
        _ = app_name
        return "/tmp/tko-cache-home"

    monkeypatch.setattr(rep_paths_module, "user_cache_dir", fake_user_cache_dir)
    original = RepPaths.use_global_cache_folder
    RepPaths.use_global_cache_folder = True
    try:
        assert paths.get_cache_folder() == Path("/tmp/tko-cache-home") / "cache"
    finally:
        RepPaths.use_global_cache_folder = original


def test_has_local_config_file_reflects_config_presence(tmp_path: Path):
    paths = RepPaths(tmp_path)
    assert paths.has_local_config_file() is False

    config_file = paths.get_config_file()
    config_file.parent.mkdir(parents=True)
    config_file.write_text("version: '0.2'\n", encoding="utf-8")

    assert paths.has_local_config_file() is True