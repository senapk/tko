from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Protocol

import enum
import hashlib
import shutil
import subprocess
import time

from filelock import FileLock
from loguru import logger

from tko.i18n import Msg
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


@dataclass(slots=True)
class GitResult:
    ok: bool
    stderr: str = ""


class GitRunner(Protocol):
    def __call__( self, *args: str, cwd: Path | None = None ) -> GitResult: ...


def _git(
    *args: str,
    cwd: Path | None = None,
) -> GitResult:
    try:
        subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=120,
        )

        return GitResult(ok=True)

    except subprocess.CalledProcessError as e:
        return GitResult(
            ok=False,
            stderr=e.stderr.decode(errors="replace"),
        )

    except subprocess.TimeoutExpired as e:
        return GitResult(
            ok=False,
            stderr=f"Git command timed out after {e.timeout}s",
        )


class GitCache:
    def __init__(
        self,
        cache_dir: str | Path,
        max_age: timedelta = timedelta(hours=1),
        update_mode: UpdateMode = UpdateMode.IF_OLDER,
    ) -> None:
        logger.debug(
            f"Initializing GitCache "
            f"with cache_dir={cache_dir}, "
            f"update_mode={update_mode}"
        )

        self.cache_dir = Path(cache_dir)
        self.update_mode = update_mode
        self.max_age = max_age

        self.updated: dict[str, bool] = {}
        self.avoid: dict[str, bool] = {}

        self.git_fn: GitRunner = _git

    def clear_cache(self) -> None:
        if self.cache_dir.exists():
            logger.info( str(_GIT_CACHE_CLEARING).format(cache_dir=self.cache_dir, ) )
            shutil.rmtree(self.cache_dir)

        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _repo_dir(self, url: str) -> Path:
        digest = hashlib.blake2b(
            url.encode(),
            digest_size=16,
        ).hexdigest()

        return self.cache_dir / digest

    def _lock_path(self, repo_path: Path) -> Path:
        return repo_path.with_suffix(".lock")

    def _last_fetch_file(self, repo: Path) -> Path:
        return repo / ".last_fetch"

    def _mark_updated(self, repo: Path) -> None:
        self._last_fetch_file(repo).touch()

    def _is_valid_repo(self, repo: Path) -> bool:
        return (repo / ".git").exists()

    def _clone(
        self,
        url: str,
        path: Path,
    ) -> GitResult:
        result = self.git_fn(
            "clone",
            "--depth",
            "1",
            "--filter=blob:none",
            "--no-single-branch",
            url,
            str(path),
        )

        if result.ok:
            result = self.git_fn(
                "fetch",
                "--prune",
                "origin",
                cwd=path,
            )

        return result

    def _update(
        self,
        repo: Path,
    ) -> GitResult:
        result = self.git_fn(
            "fetch",
            "--prune",
            "origin",
            cwd=repo,
        )

        if result.ok:
            result = self.git_fn(
                "reset",
                "--hard",
                "origin/HEAD",
                cwd=repo,
            )

        if result.ok:
            result = self.git_fn(
                "clean",
                "-fd",
                cwd=repo,
            )

        return result

    def _is_expired(
        self,
        repo: Path,
    ) -> bool:
        stamp = self._last_fetch_file(repo)

        if not stamp.exists():
            return True

        age_seconds = (
            time.time()
            - stamp.stat().st_mtime
        )

        return (
            age_seconds
            > self.max_age.total_seconds()
        )

    def _acquire_lock(
        self,
        lock_path: Path,
    ) -> FileLock:
        return FileLock(str(lock_path)) # type: ignore

    def get_remote_dir(
        self,
        url: str,
    ) -> Path | None:
        target_path = self._repo_dir(url)

        if not has_internet(1):
            if target_path.exists():
                logger.debug(
                    f"No internet connection. "
                    f"Using cached repository "
                    f"for {url} at {target_path}"
                )
                return target_path

            return None

        if url in self.avoid:
            if target_path.exists():
                logger.debug(
                    f"Skipping update for {url} "
                    f"due to previous failure. "
                    f"Using old content."
                )
                return target_path

            logger.debug(
                f"Skipping update for {url} "
                f"due to previous failure. "
                f"Directory missing."
            )

            return None

        if url in self.updated:
            return target_path

        lock_path = self._lock_path(target_path)

        with self._acquire_lock(lock_path):
            if url in self.updated:
                return target_path

            if (
                target_path.exists()
                and not self._is_valid_repo(target_path)
            ):
                logger.warning(
                    f"Removing corrupted repository "
                    f"cache at {target_path}"
                )

                shutil.rmtree(
                    target_path,
                    ignore_errors=True,
                )

            if not target_path.exists():
                logger.info(
                    str(_GIT_CACHE_CLONING).format(url=url,
                    )
                )

                result = self._clone(
                    url,
                    target_path,
                )

                if result.ok:
                    self._mark_updated(target_path)
                    self.updated[url] = True
                    return target_path

                logger.warning(
                    str(_GIT_CACHE_CLONE_FAILED)
                )

                logger.debug(result.stderr)

                self.avoid[url] = True

                return None

            need_update = False

            if self.update_mode == UpdateMode.ALWAYS:
                need_update = True

            elif (
                self.update_mode
                == UpdateMode.IF_OLDER
                and self._is_expired(target_path)
            ):
                need_update = True

            if need_update:
                logger.info(
                    str(_GIT_CACHE_UPDATING).format(url=url,
                    )
                )

                result = self._update(
                    target_path,
                )

                if result.ok:
                    self._mark_updated(
                        target_path,
                    )

                    self.updated[url] = True

                else:
                    logger.warning(
                        str(_GIT_CACHE_UPDATE_FAILED_UPDATE).format(url=url,
                        )
                    )

                    logger.debug(
                        result.stderr,
                    )

                    self.avoid[url] = True

            else:
                self.updated[url] = True

            return target_path