from __future__ import annotations

from dataclasses import dataclass

from tko.enums.execution_result import ExecutionResult
from tko.run.unit import Unit


@dataclass(frozen=True)
class RunProgress:
    total: int
    passed: int
    percent: int

    @classmethod
    def from_units(cls, units: list[Unit], no_run: bool = False) -> RunProgress:
        total = len(units)
        if no_run or total == 0:
            return cls(total=total, passed=0, percent=0)

        passed = sum(1 for unit in units if unit.result == ExecutionResult.SUCCESS)
        percent = (passed * 100) // total
        return cls(total=total, passed=passed, percent=percent)
