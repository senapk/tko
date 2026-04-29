from pathlib import Path
from typing import cast

import pytest

from tko.repository.git_cache import GitCache
from tko.repository.rep_source import (
    STUDENT_SANDBOX_INDEX,
    STUDENT_SANDBOX_NAME,
    STUDENT_SANDBOX_TARGET,
    RepSource,
    SourceType,
)


class FakeGitCache:
    def __init__(self, repo_dir: Path | None):
        self.repo_dir = repo_dir
        self.calls: list[tuple[str, bool]] = []

    def get_repo_dir(self, url: str, verbose: bool) -> Path | None:
        self.calls.append((url, verbose))
        return self.repo_dir


def test_default_student_sandbox_sets_expected_defaults() -> None:
    source = RepSource("", git_cache=None).set_default_student_sandbox()

    assert source.name == STUDENT_SANDBOX_NAME
    assert source.target == STUDENT_SANDBOX_TARGET
    assert source.index == STUDENT_SANDBOX_INDEX
    assert source.source_type == SourceType.LOCAL_FILE
    assert source.get_writeable() is True
    assert source.is_sandbox_source() is True


def test_local_source_and_workspace_helpers() -> None:
    source = RepSource("disc", git_cache=None).set_local_source(Path("/tmp/quests"), writeable=False, index="README.md")
    source.set_source_globals(Path("/workspace/root"), Path("/workspace/cache"))

    assert source.is_local() is True
    assert source.is_local_source() is True
    assert source.is_read_only() is True
    assert source.get_source_folder(verbose=False) == Path("/tmp/quests")
    assert source.get_source_readme(verbose=False) == Path("/tmp/quests/README.md")
    assert source.get_workspace() == Path("/workspace/root/disc")
    assert source.get_cache_folder() == Path("/workspace/cache")
    assert source.get_task_workspace("task1") == Path("/workspace/root/disc/task1")


def test_sandbox_workspace_uses_target_inside_root_workspace() -> None:
    source = RepSource("", git_cache=None).set_default_student_sandbox()
    source.set_source_globals(Path("/repo"), Path("/cache"))

    assert source.get_workspace() == Path("/repo/base")
    assert source.get_source_folder(verbose=False) == Path("/repo/base")


def test_get_task_workspace_raises_for_writeable_source() -> None:
    source = RepSource("disc", git_cache=None).set_local_source(Path("/tmp/quests"), writeable=True)
    source.set_source_globals(Path("/repo"), Path("/cache"))

    with pytest.raises(ValueError, match="Source is not read-only"):
        source.get_task_workspace("task1")


def test_git_source_uses_git_cache_and_errors_without_it() -> None:
    source = RepSource("disc", git_cache=None).set_git_source("https://example.com/repo.git", branch="main")

    with pytest.raises(ValueError, match="Git cache is not set"):
        source.get_source_folder(verbose=False)

    cache = FakeGitCache(Path("/tmp/cache/repo"))
    source.set_git_cache(cast(GitCache, cache))

    assert source.get_source_folder(verbose=True) == Path("/tmp/cache/repo")
    assert cache.calls == [("https://example.com/repo.git", True)]


def test_git_source_raises_when_cache_cannot_resolve_repo() -> None:
    cache = FakeGitCache(None)
    source = RepSource("disc", git_cache=cast(GitCache, cache)).set_git_source("https://example.com/repo.git")

    with pytest.raises(ValueError, match="Failed to get repository directory"):
        source.get_source_folder(verbose=False)


def test_load_from_dict_supports_current_and_legacy_fields() -> None:
    source = RepSource("", git_cache=None).load_from_dict(
        {
            "alias": "legacy",
            "link": "/tmp/material/README.md",
            "branch": "dev",
            "type": "git",
            "filters": {"q1": "A"},
            "tasks": ["t1", "t2"],
            "writeable": False,
            "index": "custom.md",
        }
    )

    assert source.name == "legacy"
    assert source.target == "/tmp/material"
    assert source.branch == "dev"
    assert source.source_type == SourceType.GIT_SOURCE
    assert source.quests == {"q1": "A"}
    assert source.tasks == {"t1": "", "t2": ""}
    assert source.get_writeable() is False
    assert source.index == "custom.md"


def test_load_from_dict_forces_sandbox_to_be_writeable() -> None:
    source = RepSource("", git_cache=None).load_from_dict(
        {
            "name": "sandbox",
            "target": "base",
            "type": "local",
            "writeable": False,
        }
    )

    assert source.is_sandbox_source() is True
    assert source.get_writeable() is True
    assert source.branch == "master"
    assert source.index == "README.md"


def test_save_to_dict_persists_non_default_branch_and_filters() -> None:
    source = RepSource("disc", git_cache=None).set_git_source("https://example.com/repo.git", branch="develop")
    source.set_filters({"quest": "x"}, {"task": "y"})
    source.set_index("INDEX.md")
    source.set_writeable(False)

    saved = source.save_to_dict()

    assert saved == {
        "name": "disc",
        "target": "https://example.com/repo.git",
        "index": "INDEX.md",
        "type": "git",
        "writeable": False,
        "branch": "develop",
        "quests": {"quest": "x"},
        "tasks": {"task": "y"},
    }