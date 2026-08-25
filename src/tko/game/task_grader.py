from tko.game.task_info import TaskSelfInfo

class TaskGrader:
    def __init__(self, task_info: TaskSelfInfo):
        self.info = task_info

    def get_rate_percent(self):
        rate = float(self.info.rate)
        if rate < 0.1:
            return 0.0
        return rate

    def get_quality_percent(self):
        return self.get_rate_percent
    
    @property
    def full_percent(self):
        return self.get_rate_percent()

    @property
    def ratio(self) -> float:
        return self.full_percent / 100.0

    @property
    def is_complete(self):
        return self.full_percent >= 70

    @property
    def not_started(self):
        return self.full_percent == 0

    @property
    def in_progress(self):
        return 0 < self.full_percent < 100