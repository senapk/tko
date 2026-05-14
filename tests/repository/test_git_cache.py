from __future__ import annotations

import contextlib
import hashlib
from datetime import timedelta
from pathlib import Path
import subprocess

from _pytest.monkeypatch import MonkeyPatch

from tko.repository.git_cache import GitCache, UpdateMode


class GitCacheProbe(GitCache):
    def public_repo_dir(self, url: str) -> Path:
        return self._repo_dir(url)

    def public_lock_path(self, repo_path: Path) -> Path:
        return self._lock_path(repo_path)

    def public_is_expired(self, repo: Path) -> bool:
        return self._is_expired(repo)

    def public_clone(self, url: str, path: Path) -> bool:
        return self._clone(url, path)


def no_lock(lock_path: Path) -> contextlib.AbstractContextManager[None]:
    _ = lock_path
    return contextlib.nullcontext()


def always_true(repo_path: Path) -> bool:
    _ = repo_path
    return True


def always_false(repo_path: Path) -> bool:
    _ = repo_path
    return False


def clone_fails(url: str, path: Path) -> bool:
    _ = (url, path)
    return False


def test_repo_and_lock_paths_are_derived_from_url(tmp_path: Path) -> None:
    cache = GitCacheProbe(tmp_path / "cache")
    url = "https://example.com/repo.git"

    repo_dir = cache.public_repo_dir(url)
    lock_path = cache.public_lock_path(repo_dir)

    assert repo_dir == (tmp_path / "cache" / hashlib.sha1(url.encode()).hexdigest())
    assert lock_path == repo_dir.with_suffix(".lock")


def test_clear_cache_removes_contents_and_recreates_folder(tmp_path: Path) -> None:
    cache = GitCache(tmp_path / "cache")
    stale_file = cache.cache_dir / "old.txt"
    stale_file.write_text("stale", encoding="utf-8")

    cache.clear_cache()

    assert cache.cache_dir.exists() is True
    assert stale_file.exists() is False


def test_is_expired_without_fetch_head_returns_true(tmp_path: Path) -> None:
    cache = GitCacheProbe(tmp_path / "cache")
    repo = cache.cache_dir / "repo"
    repo.mkdir(parents=True)

    assert cache.public_is_expired(repo) is True


def test_is_expired_uses_fetch_head_age(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    cache = GitCacheProbe(tmp_path / "cache", max_age=timedelta(seconds=60))
    repo = cache.cache_dir / "repo"
    fetch_head = repo / ".git" / "FETCH_HEAD"
    fetch_head.parent.mkdir(parents=True)
    fetch_head.write_text("ok", encoding="utf-8")

    monkeypatch.setattr("tko.repository.git_cache.time.time", lambda: fetch_head.stat().st_mtime + 30)
    assert cache.public_is_expired(repo) is False

    monkeypatch.setattr("tko.repository.git_cache.time.time", lambda: fetch_head.stat().st_mtime + 120)
    assert cache.public_is_expired(repo) is True


def test_clone_returns_false_when_git_command_fails(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    cache = GitCacheProbe(tmp_path / "cache")

    def fake_git(*args: str, cwd: Path | None = None) -> None:
        _ = (args, cwd)
        raise subprocess.CalledProcessError(returncode=1, cmd=["git"])

    monkeypatch.setattr(cache, "_git", fake_git)

    assert cache.public_clone("https://example.com/repo.git", cache.cache_dir / "repo") is False


def test_get_repo_dir_returns_none_when_initial_clone_fails(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    cache = GitCacheProbe(tmp_path / "cache")

    monkeypatch.setattr(cache, "_acquire_lock", no_lock)
    monkeypatch.setattr(cache, "_clone", clone_fails)

    result = cache.get_remote_dir("https://example.com/repo.git", verbose=False)

    assert result is None


def test_get_repo_dir_updates_when_repository_is_expired(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    cache = GitCacheProbe(tmp_path / "cache", update_mode=UpdateMode.IF_OLDER)
    repo = cache.public_repo_dir("https://example.com/repo.git")
    repo.mkdir(parents=True)
    called = {"update": False}

    monkeypatch.setattr(cache, "_acquire_lock", no_lock)
    monkeypatch.setattr(cache, "_is_expired", always_true)

    def fake_update(repo_path: Path) -> None:
        _ = repo_path
        called["update"] = True

    monkeypatch.setattr(cache, "_update", fake_update)

    result = cache.get_remote_dir("https://example.com/repo.git", verbose=False)

    assert result == repo
    assert called["update"] is True


def test_get_repo_dir_always_mode_updates_once_per_repo(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    cache = GitCacheProbe(tmp_path / "cache", update_mode=UpdateMode.ALWAYS)
    url = "https://example.com/repo.git"
    repo = cache.public_repo_dir(url)
    repo.mkdir(parents=True)
    calls = {"count": 0}

    monkeypatch.setattr(cache, "_acquire_lock", no_lock)
    monkeypatch.setattr(cache, "_is_expired", always_false)

    def fake_update(repo_path: Path) -> None:
        cache.updated[str(repo_path)] = True
        calls["count"] += 1

    monkeypatch.setattr(cache, "_update", fake_update)

    first = cache.get_remote_dir(url, verbose=False)
    second = cache.get_remote_dir(url, verbose=False)

    assert first == repo
    assert second == repo
    assert calls["count"] == 1


def test_get_repo_dir_reclones_when_update_fails(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    cache = GitCacheProbe(tmp_path / "cache", update_mode=UpdateMode.IF_OLDER)
    url = "https://example.com/repo.git"
    repo = cache.public_repo_dir(url)
    repo.mkdir(parents=True)
    calls = {"clone": 0}

    monkeypatch.setattr(cache, "_acquire_lock", no_lock)
    monkeypatch.setattr(cache, "_is_expired", always_true)

    def fake_update(repo_path: Path) -> None:
        raise subprocess.CalledProcessError(returncode=1, cmd=["git", "fetch"])

    def fake_clone(clone_url: str, clone_path: Path) -> bool:
        _ = clone_url
        clone_path.mkdir(parents=True, exist_ok=True)
        calls["clone"] += 1
        return True

    monkeypatch.setattr(cache, "_update", fake_update)
    monkeypatch.setattr(cache, "_clone", fake_clone)

    result = cache.get_remote_dir(url, verbose=False)

    assert result == repo
    assert calls["clone"] == 1