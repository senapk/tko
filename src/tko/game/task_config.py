from __future__ import annotations

from dataclasses import dataclass

from tko.game.task_enums import TaskEval


@dataclass(frozen=True, slots=True)
class TaskConfig:
    test: TaskEval = TaskEval.NULL

    def clone(self) -> TaskConfig:
        return TaskConfig(
            test=self.test,
        )
    
    @property
    def is_eval_test(self):
        return self.test == TaskEval.TEST
    
    @property
    def is_eval_self(self):
        return self.test == TaskEval.SELF