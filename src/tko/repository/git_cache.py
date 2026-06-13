from __future__ import annotations
from loguru import logger
import time
from pathlib import Path
from datetime import  timedelta
import subprocess
import hashlib
from filelock import FileLock
import shutil
import enum
from tko.i18n import Msg, t
from tko.util.has_internet import has_internet

_GIT_CACHE_CLEARING = Msg(
    pt="Limpando cache git em {cache_dir}...",
    en="Clearing git cache at {cache_dir}...",
)
_GIT_CACHE_CLONING = Msg(
    pt="Repositório não encontrado. Clonando {url} para o cache...",
    en="Repository not found. Cloning {url} into cache...",
)
_GIT_CACHE_CLONE_FAILED = Msg(
    pt="Falha ao clonar.",
    en="Failed to clone.",
)
_GIT_CACHE_UPDATING = Msg(
    pt="Atualizando cache para {url}...",
    en="Updating cache for {url}...",
)
_GIT_CACHE_UPDATE_FAILED_UPDATE = Msg(
    pt="Falha ao atualizar cache para {url}. Use 'tko reset cache' se estiver com problemas.",
    en="Failed to update cache for {url}. Use 'tko reset cache' if you are having issues.",
)

class UpdateMode(enum.Enum):
    ALWAYS = "always"
    NEVER = "never"
    IF_OLDER = "if_older"


class GitCache:
    def __init__(self, cache_dir: str | Path, max_age: timedelta = timedelta(hours=1), update_mode: UpdateMode = UpdateMode.IF_OLDER) -> None:
        logger.debug(f"Initializing GitCache with cache_dir={cache_dir}, update_mode={update_mode}")
        self.cache_dir: Path = Path(cache_dir)
        self.update_mode: UpdateMode = update_mode
        self.updated: dict[str, bool] = {}
        self.avoid: dict[str, bool] = {} # repos that failed to update, to avoid retrying them in the same session
        self.max_age: timedelta = max_age
        self.has_internet: bool = has_internet(1)

    def clear_cache(self):
        if self.cache_dir.exists():
            logger.info(t(_GIT_CACHE_CLEARING, cache_dir=self.cache_dir))
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
            self._git("fetch", "--prune", "origin", cwd=path)
            return True
        except subprocess.CalledProcessError as _:
            return False

    def _update(self, repo: Path) -> bool:
        try:
            self._git("fetch", "--prune", "origin", cwd=repo)
            self._git("reset", "--hard", "origin/HEAD", cwd=repo)
            self._git("clean", "-fd", cwd=repo)
            return True
        except subprocess.CalledProcessError as _:
            return False

    def _is_expired(self, repo: Path) -> bool:
        fetch_head: Path = repo / ".git" / "FETCH_HEAD"

        if not fetch_head.exists():
            return True

        age_seconds: float = time.time() - fetch_head.stat().st_mtime
        return age_seconds > self.max_age.total_seconds()

    def _acquire_lock(self, lock_path: Path):
        return FileLock(str(lock_path))

    def get_remote_dir(self, url: str) -> Path | None:
        target_path: Path = self._repo_dir(url)
        if not self.has_internet and target_path.exists():
            logger.debug(f"No internet connection. Using cached repository for {url} at {target_path}")
            return target_path

        if url in self.avoid:
            if target_path.exists():
                logger.debug(f"Skipping updade for {url} due to previous failure. Using old content.")
                return target_path
            else:
                logger.debug(f"Skipping updade for {url} due to previous failure. Directory missing.")
                return None
        
        if url in self.updated:
            return target_path

        lock_path: Path = self._lock_path(target_path)
        with self._acquire_lock(lock_path):
            if not target_path.exists():
                logger.warning(f"Repository not found in cache. Cloning {url}...")
                ok = self._clone(url, target_path)
                if ok:
                    self.updated[url] = True
                    return target_path
                else:
                    self.avoid[url] = True
                    logger.warning(f"Clone failed for {url}")
                    return None

            need_update = False
            if self.update_mode == UpdateMode.IF_OLDER and self._is_expired(target_path):
                logger.info(f"Updating expired repository {url}...")
                need_update = True
            if  self.update_mode == UpdateMode.ALWAYS:
                logger.info(f"Forcing update of repository {url}")
                need_update = True
            if need_update:
                ok = self._update(target_path)
                if ok:
                    self.updated[url] = True
                else:
                    logger.warning(f"Updating repository {url} failed.")
                    self.avoid[url] = True
        return target_path