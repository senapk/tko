from __future__ import annotations
from tko.settings.task_listener import TaskListener
from tko.settings.week_listener import WeekListener
from tko.logger.log_history import LogHistory
from tko.logger.log_item_base import LogItemBase

class Logger:

    def __init__(self, rep_folder: str):
        self.tasks = TaskListener()
        self.week = WeekListener()
        self.history = LogHistory(rep_folder, [self.tasks.handle_log_entry, self.week.handle_entry_incoming])
    
    def store(self, action: LogItemBase):
        self.history.append_new_action(action)
