from datetime import datetime
from pathlib import Path
from typing import Protocol

from tko.game.task import Task
from tko.logger.log_item_base import LogItemBase
from tko.logger.log_item_move import LogItemMove, LogItemMoveMode
from tko.repository.task_path_lookup import TaskPathLookup


class LogSink(Protocol):
    def store(self, action: LogItemBase) -> None: ...


class EditLogger:
    def __init__(self, task_lookup: TaskPathLookup, logger: LogSink) -> None:
        self.task_lookup: TaskPathLookup = task_lookup
        self.logger: LogSink = logger

    def on_flush_events(self, changed_files: dict[Path, datetime]) -> None:
        for path, timestamp in changed_files.items():
            task: Task | None = self.task_lookup.get_task_from_task_folder(path)
            if task is None:
                continue
            item: LogItemMove = LogItemMove()
            item.set_datetime(timestamp)
            item.mode = LogItemMoveMode.EDIT
            item.key = task.basic.full_key
            self.logger.store(item)
