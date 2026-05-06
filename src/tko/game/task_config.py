from __future__ import annotations

from dataclasses import dataclass
import enum

from tko.game.task_info import TaskSelfInfo


class TaskTest(enum.Enum):
    NULL = "null"  # default mode, EDIT if TEST, VIEW if USER
    TEST = "test"  # rate uses % of test cases passed
    SELF = "self"  # rate uses user self-evaluation


class TaskMain(enum.Enum):
    MAIN = "main"  # main task, required to complete the quest
    PERK = "perk"  # optional task that gives extra rewards and count as main for completion
    SIDE = "side"  # side task, allowing to achieve above 100% completion


class TaskLoss(enum.Enum):
    NULL = "null"  # default mode, FREE if VIEW, PART if EDIT
    FREE = "free"  # help allowed without penalty
    PART = "part"  # help allowed with partial penalty
    ZERO = "zero"  # if help is given, task is not completed (0% progress)


class TaskEdit(enum.Enum):
    VIEW = "view"  # view task details
    EDIT = "edit"  # edit task details


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
        return rate

    def get_quality_percent(self):
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
        return rate

    def get_ratio(self) -> float:
        return self.get_rate_percent() / 100.0


@dataclass
class TaskConfig:
    test: TaskTest = TaskTest.TEST
    path: TaskMain = TaskMain.MAIN
    loss: TaskLoss = TaskLoss.PART
    mode: TaskEdit = TaskEdit.EDIT

    def clone(self) -> TaskConfig:
        return TaskConfig(
            test=self.test,
            path=self.path,
            loss=self.loss,
            mode=self.mode,
        )

    def build_grader(self, info: TaskSelfInfo) -> TaskGrader:
        return TaskGrader(self.loss, info)
