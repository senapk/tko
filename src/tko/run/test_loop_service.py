from typing import Callable

from tko.enums.execution_result import ExecutionResult
from tko.logger.log_sort import LogSort
from tko.logger.task_resume import TaskResume
from tko.run.run_context import RunContext
from tko.run.unit_runner import UnitRunner
from tko.util.rtext import RText
from tko.util.symbols import Symbols


class TestLoopService:
    def __init__(self, ctx: RunContext):
        self.ctx = ctx

    def run_top_line(self, get_rate: Callable[[], int]) -> int:
        print(RText(Symbols.opening) + self.ctx.wdir.resume_splitted(), end="")
        print(" [", end="")
        self._run_units()
        print("] ", end="")
        self._print_track_info()
        return self._print_percent(get_rate)

    def _run_units(self):
        first = True
        execution_error = False
        for unit in self.ctx.wdir.get_unit_list():
            if first:
                first = False
            else:
                print(" ", end="")
            solver = self.ctx.wdir.get_solver()
            if self.ctx.config.no_run or (execution_error and self.ctx.config.abord_on_exec_error):
                unit.result = ExecutionResult.UNTESTED
            else:
                unit.result = UnitRunner.run_unit(solver, unit, timeout=self.ctx.config.timeout)
                if unit.result == ExecutionResult.EXECUTION_ERROR:
                    execution_error = True
            print(ExecutionResult.get_symbol(unit.result), end="")

    def _print_track_info(self):
        if self.ctx.config.show_track_info:
            if self.ctx.repo is not None:
                logger = self.ctx.repo.logger
                log_sort: LogSort | None = logger.tasks.task_dict.get(self.ctx.get_task().basic.full_key, None)
                if log_sort is not None:
                    log_resume = TaskResume(self.ctx.get_task().basic.full_key, "").from_log_sort(log_sort)
                    print(
                        RText(
                            f"time:{log_resume.resume.minutes:.0f}, diff:{log_resume.resume.versions}, runs:{log_resume.resume.executions},",
                            "g",
                        )
                        + " ",
                        end="",
                        flush=True,
                    )

    def _print_percent(self, get_rate: Callable[[], int]) -> int:
        percent: float = 0 if self.ctx.config.no_run else get_rate()
        print(f"{percent:.0f}%")
        return round(percent)