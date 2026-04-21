from __future__ import annotations

import sys
import time
from pathlib import Path
from datetime import  timedelta
import subprocess
import hashlib
from filelock import FileLock
import shutil
import enum

class GitCache:
    class UpdateMode(enum.Enum):
        ALWAYS = "always"
        NEVER = "never"
        IF_OLDER = "if_older"

    def __init__(self, cache_dir: str | Path, max_age: timedelta = timedelta(hours=1), update_mode: GitCache.UpdateMode = UpdateMode.IF_OLDER) -> None:
        self.cache_dir: Path = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.update_mode: GitCache.UpdateMode = update_mode
        self.updated: dict[str, bool] = {}
        self.max_age: timedelta = max_age

    def clear_cache(self):
        if self.cache_dir.exists():
            print(f"Clearing git cache at {self.cache_dir}...", file=sys.stderr)
            shutil.rmtree(self.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

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

    def _clone(self, url: str, path: Path) -> bool:
        try:
            self._git(
                "clone",
                "--depth", "1",
                "--filter=blob:none",
                "--no-single-branch",
                url,
                str(path),
            )
            return True
        except subprocess.CalledProcessError as _:
            return False

    def _update(self, repo: Path) -> None:
        self._git("fetch", "--prune", "origin", cwd=repo)
        self._git("reset", "--hard", "origin/HEAD", cwd=repo)
        self._git("clean", "-fd", cwd=repo)
        self.updated[str(repo)] = True

    def _is_expired(self, repo: Path) -> bool:
        fetch_head: Path = repo / ".git" / "FETCH_HEAD"

        if not fetch_head.exists():
            return True

        age_seconds: float = time.time() - fetch_head.stat().st_mtime
        return age_seconds > self.max_age.total_seconds()

    def _acquire_lock(self, lock_path: Path):
        return FileLock(str(lock_path))

    def get_repo_dir(self, url: str, verbose: bool) -> Path | None:
        repo: Path = self._repo_dir(url)
        lock_path: Path = self._lock_path(repo)
        with self._acquire_lock(lock_path):
            if not repo.exists():
                if verbose:
                    print(f"Cloning {url} into cache...", file=sys.stderr)
                ok = self._clone(url, repo)
                if not ok:
                    if verbose:
                        print(f"Failed to clone {url}. Removing cache directory...", file=sys.stderr)
                    shutil.rmtree(repo, ignore_errors=True)
                    return None

            if self._is_expired(repo) or (self.update_mode == GitCache.UpdateMode.ALWAYS) and not self.updated.get(str(repo), False):
                try:
                    if verbose:
                        print(f"Updating cache for {url}...", file=sys.stderr)
                    self._update(repo)
                except subprocess.CalledProcessError:
                    if self.update_mode == self.UpdateMode.IF_OLDER:
                        pass
                    if verbose:
                        print(f"Failed to update cache for {url}. Removing and re-cloning...", file=sys.stderr)
                    shutil.rmtree(repo, ignore_errors=True)
                    self._clone(url, repo)
        return repo