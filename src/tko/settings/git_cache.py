from __future__ import annotations

import time
from pathlib import Path
from datetime import  timedelta
import subprocess
import hashlib
import fcntl
import shutil


class GitCache:

    def __init__(self, cache_dir: str | Path, max_age: timedelta = timedelta(hours=1)) -> None:
        self.cache_dir: Path = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.max_age: timedelta = max_age

    def _repo_dir(self, url: str) -> Path:
        digest: str = hashlib.sha1(url.encode()).hexdigest()
        return self.cache_dir / digest

    def _lock_path(self, repo_path: Path) -> Path:
        return repo_path.with_suffix(".lock")

    def _git(self, *args: str, cwd: Path | None = None) -> None:
        subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=120,
        )

    def _clone(self, url: str, path: Path) -> None:
        self._git(
            "clone",
            "--depth", "1",
            "--filter=blob:none",
            "--no-single-branch",
            url,
            str(path),
        )

    def _update(self, repo: Path) -> None:
        self._git("fetch", "--prune", "origin", cwd=repo)
        self._git("reset", "--hard", "origin/HEAD", cwd=repo)
        self._git("clean", "-fd", cwd=repo)

    def _is_expired(self, repo: Path) -> bool:
        fetch_head: Path = repo / ".git" / "FETCH_HEAD"

        if not fetch_head.exists():
            return True

        age_seconds: float = time.time() - fetch_head.stat().st_mtime
        return age_seconds > self.max_age.total_seconds()

    def _acquire_lock(self, lock_path: Path):
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        f = open(lock_path, "w")
        fcntl.flock(f, fcntl.LOCK_EX)
        return f

    def get(self, url: str, force_update: bool) -> Path:
        repo: Path = self._repo_dir(url)
        lock_path: Path = self._lock_path(repo)

        with self._acquire_lock(lock_path):

            if not repo.exists():
                print(f"Cloning {url} into cache...")
                self._clone(url, repo)
                return repo

            if self._is_expired(repo) or force_update:
                try:
                    print(f"Updating cache for {url}...")
                    self._update(repo)
                except subprocess.CalledProcessError:
                    print(f"Failed to update cache for {url}. Removing and re-cloning...")
                    shutil.rmtree(repo, ignore_errors=True)
                    self._clone(url, repo)

        return repo