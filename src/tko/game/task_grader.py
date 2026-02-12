from .task_info import TaskInfo

class TaskGrader:
    def __init__(self, task_info: TaskInfo):
        self.info = task_info

    def get_percent(self):
        # hardcoded gambi for compatibility
        if not self.info.feedback:
            return 0.0
        rate = float(self.info.rate)
        if self.info.ia_code:
            rate *= 0.3
        if self.info.ia_debug:
            rate *= 0.8
        if self.info.ia_problem:
            rate *= 0.9
        return rate

    def get_ratio(self) -> float:
        return self.get_percent() / 100.0
