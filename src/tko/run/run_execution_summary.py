from __future__ import annotations

from dataclasses import dataclass

from tko.run.run_progress import RunProgress
from tko.run.wdir import Wdir
from tko.run.solver_builder import SolverBuilder


@dataclass(frozen=True)
class RunExecutionSummary:
    total: int
    passed: int
    percent: int
    has_compile_error: bool = False
    no_run: bool = False

    @classmethod
    def from_wdir(cls, wdir: Wdir, no_run: bool = False) -> RunExecutionSummary:
        progress = RunProgress.from_units(wdir.unit_list, no_run=no_run)
        solver: SolverBuilder | None = wdir.solver
        has_compile_error = bool(solver is not None and solver.has_compile_error())
        return cls(
            total=progress.total,
            passed=progress.passed,
            percent=progress.percent,
            has_compile_error=has_compile_error,
            no_run=no_run,
        )
