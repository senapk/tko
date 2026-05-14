from __future__ import annotations

from dataclasses import dataclass
import enum



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


@dataclass
class TaskConfig:
    path: TaskMain = TaskMain.MAIN
    test: TaskTest = TaskTest.NULL
    loss: TaskLoss = TaskLoss.NULL

    def clone(self) -> TaskConfig:
        return TaskConfig(
            test=self.test,
            path=self.path,
            loss=self.loss,
        )

    @property
    def is_optional(self):
        return self.path == TaskMain.SIDE
    
    @property
    def is_auto(self):
        return self.test == TaskTest.TEST