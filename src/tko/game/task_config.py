from __future__ import annotations

from dataclasses import dataclass
import enum



class TaskEval(enum.Enum):
    NULL = "null"  # default mode, DO if TEST, READ if USER
    TEST = "test"  # rate uses % of test cases passed
    SELF = "self"  # rate uses user self-evaluation

class TaskLoss(enum.Enum):
    NULL = "null"  # default mode, FREE if READ, PART if DO
    FREE = "free"  # help allowed without penalty
    PART = "part"  # help allowed with partial penalty
    ZERO = "zero"  # if help is given, task is not completed (0% progress)


@dataclass
class TaskConfig:
    test: TaskEval = TaskEval.NULL
    loss: TaskLoss = TaskLoss.NULL

    def clone(self) -> TaskConfig:
        return TaskConfig(
            test=self.test,
            loss=self.loss,
        )
    
    @property
    def is_auto(self):
        return self.test == TaskEval.TEST