from __future__ import annotations

from dataclasses import dataclass

from tko.game.task_enums import TaskEval, TaskLoss


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