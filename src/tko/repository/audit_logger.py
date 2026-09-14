from datetime import datetime
from pathlib import Path
from typing import Protocol

from tko.game.task import Task
from tko.repository.task_path_lookup import TaskPathLookup


class AuditSink(Protocol):
    def store(self, task_key: str, file_ts_list: list[tuple[Path, datetime | None]]) -> tuple[bool, int]: ...


class AuditLogger:
    def __init__(self, task_lookup: TaskPathLookup, audit_tracker: AuditSink) -> None:
        self.task_lookup: TaskPathLookup = task_lookup
        self.audit_tracker: AuditSink = audit_tracker

    def on_flush_events(self, changed_files: dict[Path, datetime]) -> None:
        task_files_map: dict[str, list[tuple[Path, datetime | None]]] = {}
        for path, timestamp in changed_files.items():
            task: Task | None = self.task_lookup.get_task_from_task_folder(path)
            if task is None:
                continue
            task_files_map.setdefault(task.basic.full_key, []).append((path, timestamp))
        for task_key, file_ts_list in task_files_map.items():
            self.audit_tracker.store(task_key, file_ts_list)
