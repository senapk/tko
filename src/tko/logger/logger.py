from __future__ import annotations
from tko.settings.listener_task import TaskListener
from tko.settings.listener_week import WeekListener
from tko.settings.repository import Repository
from tko.logger.log_file import LogFile
from tko.logger.log_item_base import LogItemBase

class Logger:
    instance: None | Logger = None

    @staticmethod
    def get_instance() -> Logger:
        if Logger.instance is None:
            Logger.instance = Logger()
        return Logger.instance

    def __init__(self, repository: Repository | None = None):
        self.rep: Repository | None = repository
        self.last_hash: str | None = None
        self.history: None | LogFile = None
        self.tasks = TaskListener()
        self.week = WeekListener()

    def set_log_files(self, log_file: str, track_folder: str) -> Logger:
        if self.history is not None:
            return self
        self.tasks.set_track_folder(track_folder)
        self.history = LogFile(log_file, [self.tasks.listener, self.week.listener])
        # resume = self.week.resume()
        # print("\n".join([f"{x.weed_day} {x.elapsed}" for x in resume.values()]))
        return self
    
    def get_history_file(self) -> LogFile:
        if self.history is None:
            raise Warning("fail: History File not set")
        return self.history

    def record_event(self, action: LogItemBase):
        if self.history is None:
            return
        self.get_history_file().append_new_action(action)
