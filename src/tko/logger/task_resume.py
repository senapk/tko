from tko.game.task_info import TaskInfo
from tko.logger.log_sort import LogSort

class TaskResume:
    def __init__(self):
        self.minutes: int = 0 # elapsed time in minutes
        self.minutes_str: str = "minutes"
        self.versions: int = 0 # number of versions
        self.versions_str: str = "versions"
        self.executions: int = 0 # number of runs
        self.executions_str: str = "executions"
        self.lines: int = 0 # lines
        self.lines_str: str = "lines"
        self.info: TaskInfo = TaskInfo()

    def from_log_sort(self, log_sort: LogSort):
        if log_sort.base_list:
            delta, _ = log_sort.base_list[-1]
            self.minutes = round(delta.accumulated.total_seconds() / 60)
        self.versions = len(log_sort.diff_list)
        self.executions = len(log_sort.exec_list)
        if log_sort.diff_list:
            delta, last_diff = log_sort.diff_list[-1]
            self.lines = last_diff.get_size()
        if log_sort.self_list:
            delta, last_self = log_sort.self_list[-1]
            self.self_eval_count = len(log_sort.self_list)
            self.info = last_self.get_info()
        return self
    
    def to_dict(self) -> dict[str, str]:
        output: dict[str, str] = {
            self.minutes_str: str(self.minutes),
            self.versions_str: str(self.versions),
            self.executions_str: str(self.executions),
            self.lines_str: str(self.lines),
        }
        output.update(self.info.get_kv())
        return output

    def from_dict(self, info: dict[str, str]) -> None:
        self.minutes = int(info.get(self.minutes_str, 0))
        self.versions = int(info.get(self.versions_str, 0))
        self.executions = int(info.get(self.executions_str, 0))
        self.lines = int(info.get(self.lines_str, 0))
        self.info.load_from_kv(info)
