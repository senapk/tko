from tko.game.task_info import TaskInfo
from tko.logger.log_sort import LogSort

class LogResume:
    def __init__(self):
        self.time: int = 0
        self.time_str: str = "time"
        self.diff: int = 0
        self.diff_str: str = "diff"
        self.runs: int = 0
        self.runs_str: str = "runs"
        self.size: int = 0
        self.size_str: str = "size"
        self.auto: int = 0
        self.auto_str: str = "auto"
        self.info: TaskInfo = TaskInfo()

    def from_log_sort(self, log_sort: LogSort):
        if log_sort.base_list:
            delta, _ = log_sort.base_list[-1]
            self.time = round(delta.accumulated.total_seconds() / 60)
        self.diff = len(log_sort.diff_list)
        self.runs = len(log_sort.exec_list)
        if log_sort.diff_list:
            delta, last_diff = log_sort.diff_list[-1]
            self.size = last_diff.get_size()
        if log_sort.self_list:
            delta, last_self = log_sort.self_list[-1]
            self.auto = len(log_sort.self_list)
            self.info = last_self.get_info()
        return self
    
    def to_dict(self) -> dict[str, str]:
        output: dict[str, str] = {
            self.time_str: str(self.time),
            self.diff_str: str(self.diff),
            self.runs_str: str(self.runs),
            self.size_str: str(self.size),
            self.auto_str: str(self.auto),
        }
        output.update(self.info.get_kv())
        return output
