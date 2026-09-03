from __future__ import annotations

from dataclasses import dataclass

from tko.game.task_enums import EvalMode
from tko.game.eval_mode_spec import get_eval_mode_spec


@dataclass(frozen=True, slots=True)
class TaskConfig:
    eval: EvalMode = EvalMode.NONE

    def clone(self) -> TaskConfig:
        return TaskConfig(
            eval=self.eval,
        )
    
    @property
    def eval_spec(self):
        return get_eval_mode_spec(self.eval)
    
    @property
    def is_automated(self):
        return self.eval_spec.supports_automated_tests

    @property
    def awards_xp(self):
        return self.eval_spec.awards_xp

    @property
    def is_non_evaluated(self):
        return self.eval == EvalMode.NONE

    @property
    def supports_self_evaluation(self):
        return self.eval_spec.supports_self_evaluation
