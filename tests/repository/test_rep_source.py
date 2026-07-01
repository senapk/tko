from pathlib import Path
from typing import cast

import pytest

from tko.repository.git_cache import GitCache
from tko.repository.remote import (
    REMOTE_SANDBOX_INDEX,
    REMOTE_SANDBOX_TARGET,
    Remote,
)
from tko.repository.remote import SourceType


class FakeGitCache:
    def __init__(self, repo_dir: Path | None):
        self.repo_dir = repo_dir
        self.calls: list[str] = []

    def get_remote_dir(self, url: str) -> Path | None:
        self.calls.append(url)
        return self.repo_dir


def test_set_is_sandbox_updates_remote_data_fields() -> None:
    remote = Remote("")

    remote.set_sandbox()

    assert remote.name == "sandbox"
    assert remote.target == REMOTE_SANDBOX_TARGET
    assert remote.index == REMOTE_SANDBOX_INDEX
    assert remote.source_type == SourceType.LOCAL_FILE
    assert remote.is_editable is True


def test_remote_path_source_dir_for_absolute_local_path(tmp_path: Path) -> None:
    source_dir = tmp_path / "materials"
    remote = Remote("disc", git_cache=cast(GitCache, FakeGitCache(None)))
    remote.root_dir = tmp_path / "repo"
    remote.set_local_source(source_dir, is_editable=False)

    assert remote.path.source_dir == source_dir.resolve()


def test_remote_path_source_dir_for_relative_local_path(tmp_path: Path) -> None:
    remote = Remote("disc", git_cache=cast(GitCache, FakeGitCache(None)))
    remote.root_dir = tmp_path / "repo"
    remote.set_local_source(Path("quests"), is_editable=False)

    assert remote.path.source_dir == (tmp_path / "repo" / "quests").resolve()


def test_remote_path_source_dir_for_git_source_uses_git_cache(tmp_path: Path) -> None:
    cache = FakeGitCache(tmp_path / "cache" / "repo")
    remote = Remote("disc", git_cache=cast(GitCache, cache))
    remote.root_dir = tmp_path
    remote.set_git_source("https://example.com/repo.git", branch="main")

    source_dir = remote.path.source_dir

    assert source_dir == (tmp_path / "cache" / "repo")
    assert cache.calls == ["https://example.com/repo.git"]


def test_remote_path_work_dir_depends_on_editable_flag(tmp_path: Path) -> None:
    remote = Remote("disc", git_cache=cast(GitCache, FakeGitCache(None)))
    remote.root_dir = tmp_path / "repo"

    remote.set_local_source(Path("base"), is_editable=True)
    assert remote.path.work_dir == (tmp_path / "repo" / "base").resolve()

    remote.set_local_source(Path("base"), is_editable=False)
    assert remote.path.work_dir == (tmp_path / "repo" / "disc").resolve()


def test_load_from_dict_supports_current_and_legacy_fields() -> None:
    remote = Remote("").from_dict(
        {
            "alias": "legacy",
            "link": "/tmp/material/README.md",
            "branch": "dev",
            "type": "git",
            "filters": {"q1": "A"},
            "writeable": False,
            "index": "custom.md",
        }
    )

    assert remote.name == "legacy"
    assert remote.target == "/tmp/material"
    assert remote.branch == "dev"
    assert remote.source_type == SourceType.GIT_SOURCE
    assert remote.quest_filters == {"q1": "A"}
    assert remote.is_editable is False
    assert remote.index == "custom.md"


def test_save_to_dict_persists_expected_fields() -> None:
    remote = Remote("disc")
    remote.set_git_source("https://example.com/repo.git", branch="develop", index="INDEX.md")
    remote.quest_filters = {"quest": "x"}

    saved = remote.to_dict()

    assert saved == {
        "name": "disc",
        "target": "https://example.com/repo.git",
        "index": "INDEX.md",
        "type": "git",
        "writeable": False,
        "branch": "develop",
        "quests": {"quest": "x"},
    }


def test_path_requires_git_cache_and_root_dir() -> None:
    remote = Remote("disc")

    with pytest.raises(ValueError, match="Git cache and root dir must be set"):
        _ = remote.path
