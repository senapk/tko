from __future__ import annotations
from tko.config.run_settings import RunSettings
from tko.logger.task_listener import TaskListener
from tko.logger.daily_listener import DailyListener
from tko.logger.log_history import LogHistory
from tko.logger.log_item_base import LogItemBase
from pathlib import Path

from tko.repository.repository_paths import RepositoryPaths # type: ignore


class Logger:

    def __init__(self, rep_folder: Path, rs: RunSettings, paths: RepositoryPaths):
        self.tasks = TaskListener()
        self.daily = DailyListener()
        self.history = LogHistory(rep_folder, rs, paths, [self.tasks.handle_log_entry, self.daily.handle_entry_incoming])
    
    def store(self, action: LogItemBase):
        self.history.append_new_action(action)
