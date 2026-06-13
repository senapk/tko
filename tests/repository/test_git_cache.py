from __future__ import annotations

import contextlib
import hashlib
import time
from datetime import timedelta
from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

from tko.repository.git_cache import (
    GitCache,
    GitResult,
    UpdateMode,
)


class GitCacheProbe(GitCache):
    def public_repo_dir(self, url: str) -> Path:
        return self._repo_dir(url)

    def public_lock_path(self, repo_path: Path) -> Path:
        return self._lock_path(repo_path)

    def public_is_expired(self, repo: Path) -> bool:
        return self._is_expired(repo)

    def public_last_fetch_file(self, repo: Path) -> Path:
        return self._last_fetch_file(repo)

    def public_mark_updated(self, repo: Path) -> None:
        self._mark_updated(repo)

    def public_is_valid_repo(self, repo: Path) -> bool:
        return self._is_valid_repo(repo)


def no_lock(path: Path):
    _ = path
    return contextlib.nullcontext()


def git_ok(*args: str, cwd: Path | None = None) -> GitResult:
    _ = (args, cwd)
    return GitResult(ok=True)


def git_fail(*args: str, cwd: Path | None = None) -> GitResult:
    _ = (args, cwd)
    return GitResult(
        ok=False,
        stderr="boom",
    )


def always_true(path: Path) -> bool:
    _ = path
    return True


def always_false(path: Path) -> bool:
    _ = path
    return False


def test_repo_and_lock_paths_are_derived_from_url(
    tmp_path: Path,
) -> None:
    cache = GitCacheProbe(tmp_path)

    url = "https://example.com/repo.git"

    expected = hashlib.blake2b(
        url.encode(),
        digest_size=16,
    ).hexdigest()

    repo_dir = cache.public_repo_dir(url)

    assert repo_dir == tmp_path / expected

    assert (
        cache.public_lock_path(repo_dir)
        == repo_dir.with_suffix(".lock")
    )


def test_clear_cache(
    tmp_path: Path,
) -> None:
    cache = GitCache(tmp_path)

    tmp_path.mkdir(exist_ok=True)

    stale = tmp_path / "old.txt"
    stale.write_text("stale")

    cache.clear_cache()

    assert cache.cache_dir.exists()
    assert not stale.exists()


def test_repo_without_last_fetch_is_expired(
    tmp_path: Path,
) -> None:
    cache = GitCacheProbe(
        tmp_path,
        max_age=timedelta(minutes=1),
    )

    repo = tmp_path / "repo"

    repo.mkdir()

    assert cache.public_is_expired(repo)


def test_last_fetch_controls_expiration(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    cache = GitCacheProbe(
        tmp_path,
        max_age=timedelta(seconds=60),
    )

    repo = tmp_path / "repo"
    repo.mkdir()

    cache.public_mark_updated(repo)

    stamp = cache.public_last_fetch_file(repo)

    monkeypatch.setattr(
        time,
        "time",
        lambda: stamp.stat().st_mtime + 30,
    )

    assert not cache.public_is_expired(repo)

    monkeypatch.setattr(
        time,
        "time",
        lambda: stamp.stat().st_mtime + 120,
    )

    assert cache.public_is_expired(repo)


def test_mark_updated_creates_last_fetch(
    tmp_path: Path,
) -> None:
    cache = GitCacheProbe(tmp_path)

    repo = tmp_path / "repo"
    repo.mkdir()

    cache.public_mark_updated(repo)

    assert (
        cache.public_last_fetch_file(repo)
        .exists()
    )


def test_valid_repo_detection(
    tmp_path: Path,
) -> None:
    cache = GitCacheProbe(tmp_path)

    repo = tmp_path / "repo"

    repo.mkdir()

    assert not cache.public_is_valid_repo(repo)

    (repo / ".git").mkdir()

    assert cache.public_is_valid_repo(repo)


def test_initial_clone_failure_returns_none(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    cache = GitCacheProbe(tmp_path)

    cache.git_fn = git_fail

    monkeypatch.setattr(
        cache,
        "_acquire_lock",
        no_lock,
    )

    monkeypatch.setattr(
        "tko.repository.git_cache.has_internet",
        lambda timeout=1: True,
    )

    result = cache.get_remote_dir(
        "https://example.com/repo.git"
    )

    assert result is None


def test_successful_clone_marks_updated(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    cache = GitCacheProbe(tmp_path)

    url = "https://example.com/repo.git"

    monkeypatch.setattr(
        cache,
        "_acquire_lock",
        no_lock,
    )

    monkeypatch.setattr(
        "tko.repository.git_cache.has_internet",
        lambda timeout=1: True,
    )

    def fake_clone(
        clone_url: str,
        path: Path,
    ) -> GitResult:
        _ = clone_url

        path.mkdir(parents=True)
        (path / ".git").mkdir()

        return GitResult(ok=True)

    monkeypatch.setattr(
        cache,
        "_clone",
        fake_clone,
    )

    repo = cache.get_remote_dir(url)

    assert repo is not None

    assert (
        cache.public_last_fetch_file(repo)
        .exists()
    )

    assert url in cache.updated


def test_expired_repository_is_updated(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    cache = GitCacheProbe(
        tmp_path,
        update_mode=UpdateMode.IF_OLDER,
    )

    url = "https://example.com/repo.git"

    repo = cache.public_repo_dir(url)

    repo.mkdir(parents=True)
    (repo / ".git").mkdir()

    called = False

    monkeypatch.setattr(
        cache,
        "_acquire_lock",
        no_lock,
    )

    monkeypatch.setattr(
        cache,
        "_is_expired",
        always_true,
    )

    monkeypatch.setattr(
        "tko.repository.git_cache.has_internet",
        lambda timeout=1: True,
    )

    def fake_update(path: Path) -> GitResult:
        nonlocal called

        called = True

        return GitResult(ok=True)

    monkeypatch.setattr(
        cache,
        "_update",
        fake_update,
    )

    cache.get_remote_dir(url)

    assert called


def test_non_expired_repository_is_marked_updated(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    cache = GitCacheProbe(
        tmp_path,
        update_mode=UpdateMode.IF_OLDER,
    )

    url = "https://example.com/repo.git"

    repo = cache.public_repo_dir(url)

    repo.mkdir(parents=True)
    (repo / ".git").mkdir()

    monkeypatch.setattr(
        cache,
        "_acquire_lock",
        no_lock,
    )

    monkeypatch.setattr(
        cache,
        "_is_expired",
        always_false,
    )

    monkeypatch.setattr(
        "tko.repository.git_cache.has_internet",
        lambda timeout=1: True,
    )

    cache.get_remote_dir(url)

    assert url in cache.updated


def test_failed_update_is_added_to_avoid(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    cache = GitCacheProbe(
        tmp_path,
        update_mode=UpdateMode.IF_OLDER,
    )

    url = "https://example.com/repo.git"

    repo = cache.public_repo_dir(url)

    repo.mkdir(parents=True)
    (repo / ".git").mkdir()

    monkeypatch.setattr(
        cache,
        "_acquire_lock",
        no_lock,
    )

    monkeypatch.setattr(
        cache,
        "_is_expired",
        always_true,
    )

    monkeypatch.setattr(
        "tko.repository.git_cache.has_internet",
        lambda timeout=1: True,
    )

    monkeypatch.setattr(
        cache,
        "_update",
        lambda path: GitResult( ok=False, stderr="boom", ), # type: ignore
    )

    cache.get_remote_dir(url)

    assert url in cache.avoid