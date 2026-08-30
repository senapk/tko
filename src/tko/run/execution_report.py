from __future__ import annotations

from dataclasses import dataclass

from tko.run.unit import Unit
from tko.run.run_execution_summary import RunExecutionSummary


@dataclass(frozen=True)
class ExecutionReport:
    summary: RunExecutionSummary
    units: list[Unit]
    has_compile_error: bool
    compact: bool
    eval_mode: bool

    @classmethod
    def from_execution(
        cls,
        summary: RunExecutionSummary,
        units: list[Unit],
        has_compile_error: bool = False,
        compact: bool = False,
        eval_mode: bool = False,
    ) -> ExecutionReport:
        return cls(
            summary=summary,
            units=units,
            has_compile_error=has_compile_error,
            compact=compact,
            eval_mode=eval_mode,
        )

    def get_failed_units(self) -> list[Unit]:
        from tko.enums.execution_result import ExecutionResult
        return [unit for unit in self.units if unit.result != ExecutionResult.SUCCESS]

    def get_first_failed_unit(self) -> Unit | None:
        failed = self.get_failed_units()
        return failed[0] if failed else None

    def has_failures(self) -> bool:
        from tko.enums.execution_result import ExecutionResult
        return any(u.result in (ExecutionResult.EXECUTION_ERROR, ExecutionResult.WRONG_OUTPUT) for u in self.units)
