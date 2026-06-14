from pathlib import Path
from tko.config.run_settings import RunSettings
from tko.repository.repository_paths import RepositoryPaths


def make_run_settings(tmp_path: Path, local_cache: bool = False) -> RunSettings:
    return RunSettings(changedir=tmp_path, local_cache=local_cache)


def test_rec_search_for_repo_parents_returns_none_when_no_repository_exists(tmp_path: Path):
    start = tmp_path / "a" / "b"
    start.mkdir(parents=True)

    found = RepositoryPaths.rec_search_for_repo_parents(start)

    assert found is None


def test_rec_search_for_repo_parents_finds_nearest_parent_repository(tmp_path: Path):
    repo_root = tmp_path / "repo"
    nested = repo_root / "src" / "module"
    config_file = repo_root / RepositoryPaths.CONFIG_FOLDER / RepositoryPaths.CFG_FILE
    config_file.parent.mkdir(parents=True)
    config_file.write_text("version: '0.2'\n", encoding="utf-8")
    nested.mkdir(parents=True)

    found = RepositoryPaths.rec_search_for_repo_parents(nested)

    assert found == repo_root


def test_rec_search_for_repo_subdir_finds_nested_repositories(tmp_path: Path):
    repo_a = tmp_path / "a"
    repo_b = tmp_path / "deep" / "b"
    for repo in [repo_a, repo_b]:
        config = repo / RepositoryPaths.CONFIG_FOLDER / RepositoryPaths.CFG_FILE
        config.parent.mkdir(parents=True)
        config.write_text("version: '0.2'\n", encoding="utf-8")

    found = RepositoryPaths.rec_search_for_repo_subdir(tmp_path)

    assert sorted(found) == sorted([repo_a, repo_b])


def test_path_helpers_return_expected_locations(tmp_path: Path):
    paths = RepositoryPaths(tmp_path, make_run_settings(tmp_path, local_cache=True))

    assert paths.root_dir == tmp_path
    assert paths.track_folder == tmp_path / ".tko" / "track"
    assert paths.audit_folder == tmp_path / ".tko" / "audit"
    assert paths.log_folder == tmp_path / ".tko" / "log"
    assert paths.get_track_task_folder("repo@task") == tmp_path / ".tko" / "track" / "repo@task"
    assert paths.get_audit_task_folder("repo@task") == tmp_path / ".tko" / "audit" / "repo@task"
    assert paths.config_folder == tmp_path / ".tko"
    assert paths.config_file == tmp_path / ".tko" / "repository.yaml"
    assert paths.config_backup_file == tmp_path / ".tko" / "repository.yaml.backup"
    assert paths.old_history_file == tmp_path / ".tko" / "history.csv"
    assert paths.root_dir == tmp_path



def test_config_file_presence_can_be_checked_from_property(tmp_path: Path):
    paths = RepositoryPaths(tmp_path, make_run_settings(tmp_path, local_cache=True))
    assert paths.config_file.exists() is False

    config_file = paths.config_file
    config_file.parent.mkdir(parents=True)
    config_file.write_text("version: '0.2'\n", encoding="utf-8")

    assert paths.config_file.exists() is True
