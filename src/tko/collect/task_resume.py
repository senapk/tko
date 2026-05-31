from typing import Any
import datetime as dt
from dataclasses import dataclass
from tko.logger.log_sort import LogSort
from tko.logger.delta import Delta

@dataclass
class TaskResume:
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


    def get_kv(self) -> dict[str, Any]:
        output: dict[str, Any] = {}
        output[TaskResume.Key.INIT] = Delta.encode_format(self.init_time) if self.init_time else ""
        output[TaskResume.Key.DURATION] = Delta.format_hhmmss(self.duration.total_seconds())
        if self.events > 0:
            output[TaskResume.Key.EVENTS] = str(self.events)
        # if self.minutes > 0:
        #     output[TaskResume.Key.MINUTES] = str(self.minutes)
        output[TaskResume.Key.VERSIONS] = f"{self.versions:>2}"
        output[TaskResume.Key.EXECUTIONS] = f"{self.executions:>2}"
        # if self.lines > 0:
        #     output[TaskResume.Key.LINES] = str(self.lines)

        return output

    def from_kv(self, info: dict[str, str]) -> None:
        init_str = info.get(TaskResume.Key.INIT, "")
        if init_str:
            self.init_time = Delta.decode_format(init_str)
        duration_str = info.get(TaskResume.Key.DURATION, "")
        if duration_str:
            self.duration = Delta.parse_hhmmss(duration_str)
        self.events = int(info.get(TaskResume.Key.EVENTS, 0))
        self.versions   = int(info.get(TaskResume.Key.VERSIONS, 0))
        self.executions = int(info.get(TaskResume.Key.EXECUTIONS, 0))
