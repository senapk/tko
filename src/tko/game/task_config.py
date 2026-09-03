from __future__ import annotations

from dataclasses import dataclass

from tko.game.task_enums import TaskEval, TaskType


@dataclass(frozen=True, slots=True)
class TaskConfig:
    type: TaskType = TaskType.NULL

    def clone(self) -> TaskConfig:
        return TaskConfig(
            type=self.type,
        )
    
    @property
    def is_eval_test(self):
        return self.type in (TaskType.DIFF, TaskType.CODE)
    
    @property
    def is_eval_self(self):
        return self.type == TaskType.SELF

    @property
    def is_wiki(self):
        return self.type == TaskType.WIKI

    @property
    def test(self) -> TaskEval:
        """Compatibilidade de leitura; novas configurações usam type."""
        if self.type == TaskType.SELF:
            return TaskEval.SELF
        if self.type in (TaskType.DIFF, TaskType.CODE):
            return TaskEval.TEST
        return TaskEval.SELF
