from typing import Any
import datetime as dt
from dataclasses import dataclass
from tko.logger.log_sort import LogSort
from tko.logger.delta import Delta

@dataclass
class TaskCollectedResume:
    class Key:
        INIT: str = "init"
        DURATION: str = "duration"
        EVENTS: str = "events" # number os sequential ocurrences
        VERSIONS: str = "diffs" # number of versions
        EXECUTIONS: str = "executions"

    init_time: dt.datetime | None = None
    duration: dt.timedelta = dt.timedelta()
    events: int = 0
    versions: int = 0 # number of versions
    executions: int = 0 # number of runs

    def from_log_sort(self, log_sort: LogSort):
        self.events = log_sort.sequential_ocurrences
        base_list = log_sort.base_list
        if base_list:
            _, first = base_list[0]
            self.init_time = first.get_datetime()
            delta, _ = base_list[-1]
            self.duration = delta.accumulated
        self.versions = len(log_sort.diff_list)
        self.executions = len(log_sort.exec_list)


    def get_kv(self, full: bool = False, minutes: bool = True) -> dict[str, Any]:
        output: dict[str, Any] = {}
        output[TaskCollectedResume.Key.INIT] = Delta.encode_format(self.init_time) if self.init_time else ""
        output[TaskCollectedResume.Key.DURATION] = (self.duration.total_seconds() / 60) if minutes else Delta.format_hhmmss(self.duration.total_seconds())
        if full or self.events > 0:
            output[TaskCollectedResume.Key.EVENTS] = str(self.events)
        output[TaskCollectedResume.Key.VERSIONS] = f"{self.versions:>2}"
        output[TaskCollectedResume.Key.EXECUTIONS] = f"{self.executions:>2}"

        return output

    def from_kv(self, info: dict[str, str]) -> None:
        init_str = info.get(TaskCollectedResume.Key.INIT, "")
        if init_str:
            self.init_time = Delta.decode_format(init_str)
        duration_str = info.get(TaskCollectedResume.Key.DURATION, "")
        if duration_str:
            self.duration = Delta.parse_hhmmss(duration_str)
        self.events = int(info.get(TaskCollectedResume.Key.EVENTS, 0))
        self.versions   = int(info.get(TaskCollectedResume.Key.VERSIONS, 0))
        self.executions = int(info.get(TaskCollectedResume.Key.EXECUTIONS, 0))
