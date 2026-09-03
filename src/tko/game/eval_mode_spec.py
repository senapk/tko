from __future__ import annotations

from dataclasses import dataclass

from tko.game.task_enums import EvalMode


@dataclass(frozen=True, slots=True)
class EvalModeSpec:
    """Contrato operacional de um modo de avaliação."""

    materializes_draft: bool
    materializes_tests: bool
    supports_self_evaluation: bool
    supports_automated_tests: bool
    awards_xp: bool


_EVAL_MODE_SPECS: dict[EvalMode, EvalModeSpec] = {
    EvalMode.NONE: EvalModeSpec(False, False, False, False, False),
    EvalMode.SELF: EvalModeSpec(True, False, True, False, True),
    EvalMode.DIFF: EvalModeSpec(True, True, True, True, True),
}


def get_eval_mode_spec(eval_mode: EvalMode) -> EvalModeSpec:
    try:
        return _EVAL_MODE_SPECS[eval_mode]
    except KeyError as exc:
        raise ValueError(f"Unsupported evaluation mode: {eval_mode.value}") from exc
