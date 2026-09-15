from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from filelock import BaseFileLock, FileLock, Timeout


class AuditAlreadyRunning(RuntimeError):
    """Raised when another process owns the workspace audit collector."""


class AuditCoordinator:
    """Own the single audit collector allowed for a repository workspace."""

    def __init__(self, root_dir: Path) -> None:
        self._folder: Path = root_dir / ".tko"
        self._lock_path: Path = self._folder / "audit-runtime.lock"
        self._status_path: Path = self._folder / "audit-runtime.json"
        self._lock: BaseFileLock = FileLock(str(self._lock_path))
        self._owned: bool = False

    def acquire(self) -> None:
        if self._owned:
            return
        self._folder.mkdir(parents=True, exist_ok=True)
        try:
            self._lock.acquire(timeout=0)
        except Timeout as error:
            raise AuditAlreadyRunning(self.description()) from error
        self._owned = True
        metadata: dict[str, object] = {
            "pid": os.getpid(),
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        self._status_path.write_text(json.dumps(metadata, ensure_ascii=False) + "\n", encoding="utf-8")

    def release(self) -> None:
        if not self._owned:
            return
        self._owned = False
        try:
            self._status_path.unlink(missing_ok=True)
        finally:
            self._lock.release()

    def description(self) -> str:
        if not self._status_path.is_file():
            return "Auditoria já está ativa neste workspace."
        try:
            metadata = json.loads(self._status_path.read_text(encoding="utf-8"))
            pid = metadata.get("pid")
            return f"Auditoria já está ativa neste workspace (processo {pid})."
        except (OSError, TypeError, ValueError):
            return "Auditoria já está ativa neste workspace."

    def is_active(self) -> bool:
        try:
            self._lock.acquire(timeout=0)
        except Timeout:
            return True
        self._lock.release()
        return False
