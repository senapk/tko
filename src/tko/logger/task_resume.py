from tko.game.task_info import TaskInfo
from tko.logger.log_sort import LogSort
from tko.game.task_grader import TaskGrader
from typing import Any


class Resume:
    minutes_str: str = "minutes"
    versions_str: str = "versions"
    executions_str: str = "executions"
    lines_str: str = "lines"
    percent_str: str = "percent"

    def __init__(self, minutes: int = 0, versions: int = 0, executions: int = 0, lines: int = 0, percent: float = 0.0):
        self.minutes: int = minutes # elapsed time in minutes
        self.versions: int = versions # number of versions
        self.executions: int = executions # number of runs
        self.lines: int = lines # lines
        self.percent: float = percent # percent of completion

    def to_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = {}
        if self.minutes > 0:
            output[Resume.minutes_str] = str(self.minutes)
        if self.versions > 0:
            output[Resume.versions_str] = str(self.versions)
        if self.executions > 0:
            output[Resume.executions_str] = str(self.executions)
        if self.lines > 0:
            output[Resume.lines_str] = str(self.lines)
        if self.percent > 0.0:
            output[Resume.percent_str] = f"{self.percent:.2f}"
        return output
    
    def from_dict(self, info: dict[str, str]) -> None:
        # print(f"Loading Resume from dict: {info}")
        self.minutes    = int(info.get(Resume.minutes_str, 0))
        self.versions   = int(info.get(Resume.versions_str, 0))
        self.executions = int(info.get(Resume.executions_str, 0))
        self.lines      = int(info.get(Resume.lines_str, 0))
        percent_str     = info.get(Resume.percent_str, "0.0")
        if percent_str:
            self.percent = float(percent_str)


class TaskResume:
    def __init__(self, key: str):
        self.key: str = key
        self.resume: Resume = Resume()
        self.info: TaskInfo = TaskInfo()

    def from_log_sort(self, log_sort: LogSort):
        if log_sort.base_list:
            delta, _ = log_sort.base_list[-1]
            self.resume.minutes = round(delta.accumulated.total_seconds() / 60)
        self.resume.versions = len(log_sort.diff_list)
        self.resume.executions = len(log_sort.exec_list)
        if log_sort.diff_list:
            delta, last_diff = log_sort.diff_list[-1]
            self.resume.lines = last_diff.get_size()
        if log_sort.self_list:
            delta, last_self = log_sort.self_list[-1]
            self.info = last_self.get_info()
            self.resume.percent = TaskGrader(self.info).get_percent()
        return self
    
    def to_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = {}
        output.update(self.resume.to_dict())
        output.update(self.info.get_filled_kv())
        return output

    def from_dict(self, info: dict[str, str]) -> None:
        self.resume.from_dict(info)
        self.info.load_from_kv(info)
