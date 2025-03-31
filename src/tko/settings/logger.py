from __future__ import annotations
from tko.settings.history_file import HistoryFile
from tko.settings.log_action import LogAction
from tko.settings.listener_daily import DailyListener
from tko.settings.listener_task import TaskListener
from tko.settings.listener_week import WeekListener
import os

class Logger:
    instance: None | Logger = None

    @staticmethod
    def get_instance() -> Logger:
        if Logger.instance is None:
            Logger.instance = Logger()
        return Logger.instance

    def __init__(self):
        self.last_hash: str | None = None
        self.history: None | HistoryFile = None
        self.daily = DailyListener()
        self.tasks = TaskListener()
        self.week = WeekListener()

    def set_log_files(self, log_file: str) -> Logger:
        if self.history is not None:
            return self
        self.history = HistoryFile(log_file, [self.daily.listener, self.tasks.listener, self.week.listener])
        # resume = self.week.resume()
        # print("\n".join([f"{x.weed_day} {x.elapsed}" for x in resume.values()]))
        return self
    
    def get_history_file(self) -> HistoryFile:
        if self.history is None:
            raise Warning("fail: History File not set")
        return self.history

    def check_log_file_integrity(self) -> list[str]:
        entries = self.get_history_file().get_entries()
        if len(entries) == 0:
            return []
        hash = entries[0].hash
        output: list[str] = []

        for i in range(1, len(entries)):
            calculated_hash = LogAction.generate_hash(entries[i], hash)
            if calculated_hash != entries[i].hash:
                output.append(f"Hash mismatch line {i + 1}: {str(entries[i])}")
            hash = calculated_hash
        return output

    def record_pick(self, task_key: str):
        self.__record_event(LogAction.Type.PICK, task_key)

    def record_back(self, task_key: str):
        self.__record_event(LogAction.Type.BACK, task_key)

    def record_down(self, task_key: str):
        self.__record_event(LogAction.Type.DOWN, task_key)

    def record_compilation_execution_error(self, task_key: str):
        self.__record_event(LogAction.Type.FAIL, task_key)
    
    def record_test_result(self, task_key: str, result: int):
        self.__record_event(LogAction.Type.TEST, task_key, str(result))

    def record_freerun(self, task_key: str):
        self.__record_event(LogAction.Type.FREE, task_key)

    def record_self_grade(self, task_key: str, coverage: int, autonomy: int, skill: int):
        self.__record_event(LogAction.Type.SELF, task_key, "{" + f"c:{coverage},a:{autonomy},s:{skill}" + "}")

    def record_open(self):
        self.__record_event(LogAction.Type.OPEN)
    
    def record_quit(self):
        self.__record_event(LogAction.Type.QUIT)

    def __record_event(self, action: LogAction.Type, task_key: str = "", payload: str = ""):
        if self.history is None:
            return
        self.get_history_file().append_new_action(action, task_key, payload)
