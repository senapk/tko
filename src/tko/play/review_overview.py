"""Typed per-task summary shared by the class table and its CSV export."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Literal

from tko.config.run_settings import RunSettings
from tko.play.review_loader import load_review_repository
from tko.repository.repository import Repository


ReviewRowStatus = Literal["ok", "sem atividade", "tarefa ausente", "erro"]


@dataclass(frozen=True, slots=True)
class ReviewTaskRow:
    index: int
    student: str
    repository: Path
    status: ReviewRowStatus
    grade: float | None = None
    executions: int = 0
    versions: int = 0
    minutes: float = 0.0
    last_event: datetime | None = None
    feedback: bool = False
    error: str = ""


class ReviewOverviewService:
    def __init__(self, repositories: list[Path], settings: RunSettings) -> None:
        self.repositories: list[Path] = repositories
        self.settings: RunSettings = settings
        self._cache: dict[str, dict[int, ReviewTaskRow]] = {}
        self._load_lock: Lock = Lock()

    def invalidate(self, index: int) -> None:
        with self._load_lock:
            for rows in self._cache.values():
                rows.pop(index, None)

    def load_repository(self, folder: Path, *, announce: bool = True) -> Repository:
        with self._load_lock:
            return load_review_repository(folder, self.settings, announce=announce)

    def row(self, task_key: str, index: int, *, refresh: bool = False) -> ReviewTaskRow:
        with self._load_lock:
            return self._row_locked(task_key, index, refresh=refresh)

    def _row_locked(self, task_key: str, index: int, *, refresh: bool) -> ReviewTaskRow:
        cached: dict[int, ReviewTaskRow] = self._cache.setdefault(task_key, {})
        if not refresh and index in cached:
            return cached[index]
        folder: Path = self.repositories[index]
        try:
            repo: Repository = load_review_repository(folder, self.settings, announce=False)
            task = repo.game.get_task(task_key)
            history = repo.logger.tasks.get_task_log(task_key)
            if history is None:
                row = ReviewTaskRow(
                    index, folder.name, folder,
                    "sem atividade" if task is not None else "tarefa ausente",
                    grade=task.grader.full_percent if task is not None else None,
                    feedback=task.info.feedback if task is not None else False,
                )
            else:
                entries = history.base_list
                row = ReviewTaskRow(
                    index, folder.name, folder,
                    "ok" if task is not None else "tarefa ausente",
                    grade=task.grader.full_percent if task is not None else None,
                    executions=len(history.exec_list), versions=len(history.diff_list),
                    minutes=entries[-1][0].accumulated.total_seconds() / 60 if entries else 0.0,
                    last_event=entries[-1][1].get_datetime() if entries else None,
                    feedback=task.info.feedback if task is not None else bool(history.self_list),
                )
        except Exception as error:
            # A broken student repository must not interrupt the class overview.
            row = ReviewTaskRow(index, folder.name, folder, "erro", error=str(error))
        cached[index] = row
        return row

    @staticmethod
    def export_csv(path: Path, task_key: str, rows: list[ReviewTaskRow]) -> None:
        headers: list[str] = [
            "student", "repository", "task", "status", "grade", "executions",
            "versions", "minutes", "last_event", "feedback", "error",
        ]
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow({
                    "student": row.student, "repository": str(row.repository), "task": task_key,
                    "status": row.status, "grade": "" if row.grade is None else row.grade,
                    "executions": row.executions, "versions": row.versions,
                    "minutes": round(row.minutes, 2),
                    "last_event": row.last_event.isoformat() if row.last_event is not None else "",
                    "feedback": "1" if row.feedback else "0", "error": row.error,
                })
