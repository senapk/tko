from tko.game.task_enums import TaskLoss
from tko.game.task_info import TaskSelfInfo

class TaskGrader:
    def __init__(self, task_loss: TaskLoss, task_info: TaskSelfInfo):
        self.info = task_info
        self.loss = task_loss
        self.grades: dict[str, dict[str, int]] = {
            TaskLoss.FREE.value: {
                "guided": 100,
                "code": 100,
                "debug": 100,
                "problem": 100,
            },
            TaskLoss.PART.value: {
                "guided": 80,
                "code": 40,
                "debug": 80,
                "problem": 90,
            },
            TaskLoss.ZERO.value: {
                "guided": 0,
                "code": 0,
                "debug": 0,
                "problem": 0,
            },
        }

    def get_rate_percent(self):
        rate = float(self.info.rate)
        if rate < 0.1:
            return 0.0
        return rate

    def get_quality_percent(self):
        if self.loss == TaskLoss.FREE:
            return 100
        if not self.info.feedback:
            return 0.0
        rate = 100.0
        if self.info.guided:
            rate *= self.grades[self.loss.value]["guided"] / 100.0
        if self.info.ia_code:
            rate *= self.grades[self.loss.value]["code"] / 100.0
        if self.info.ia_debug:
            rate *= self.grades[self.loss.value]["debug"] / 100.0
        if self.info.ia_problem:
            rate *= self.grades[self.loss.value]["problem"] / 100.0
        if rate < 0.1:
            return 0.0
        return rate
    
    @property
    def full_percent(self):
        return (self.get_rate_percent() * self.get_quality_percent()) / 100.0

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