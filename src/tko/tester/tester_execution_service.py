from collections.abc import Callable

from tko.config.settings import Settings
from tko.enums.execution_result import ExecutionResult
from tko.game.task import Task
from tko.logger.log_item_exec import LogItemExec
from tko.repository.repository import Repository
from tko.repository.repository_loader import RepositoryLoader
from tko.run.unit import Unit
from tko.run.unit_runner import UnitRunner
from tko.run.wdir import Wdir
from tko.tester.tester_state import SeqMode, TesterState


class TesterExecutionService:
    def __init__(
        self,
        settings: Settings,
        rep: Repository | None,
        wdir: Wdir,
        task: Task,
        store_version: Callable[[str], tuple[bool, int]],
    ) -> None:
        self.settings = settings
        self.rep = rep
        self.wdir = wdir
        self.task = task
        self.store_version = store_version
        self._dummy_unit = Unit()

    def process_one(self, state: TesterState) -> None:
        if state.mode != SeqMode.running:
            return

        solver = self.wdir.solver
        if solver is None:
            return

        if solver.has_compile_error():
            self._handle_compile_error(state)
            return

        if state.locked_index or not self.wdir.has_tests:
            self._run_locked_or_without_tests(state)
            return

        self._run_next_test(state)
        if len(state.unit_list) == 0:
            self._finish_and_store(state)

    def _handle_compile_error(self, state: TesterState) -> None:
        mode = LogItemExec.Mode.LOCK if state.locked_index else LogItemExec.Mode.FULL
        changes, total_lines = self.store_version("0")
        if self.rep:
            self.rep.logger.store(
                LogItemExec()
                .set_key(self.task.basic.full_key)
                .set_mode(mode)
                .set_fail(LogItemExec.Fail.COMP)
                .set_size(changes, total_lines)
            )
        state.mode = SeqMode.finished
        while state.unit_list:
            index = len(state.results)
            state.unit_list = state.unit_list[1:]
            state.results.append((ExecutionResult.COMPILATION_ERROR, index))

    def _run_locked_or_without_tests(self, state: TesterState) -> None:
        state.mode = SeqMode.finished
        unit = state.get_focused_unit(self.wdir, self._dummy_unit)
        solver = self.wdir.solver
        if solver is None:
            return
        unit.result = UnitRunner.run_unit(solver, unit, self.settings.app.timeout)
        rate = 100 if unit.result == ExecutionResult.SUCCESS else 0
        changes, total_lines = self.store_version(str(rate))
        if self.rep:
            self.rep.logger.store(
                LogItemExec()
                .set_key(self.task.basic.full_key)
                .set_mode(LogItemExec.Mode.LOCK)
                .set_rate(rate)
                .set_size(changes, total_lines)
            )

    def _run_next_test(self, state: TesterState) -> None:
        index = len(state.results)
        unit = state.unit_list[0]
        state.unit_list = state.unit_list[1:]
        solver = self.wdir.solver
        if solver is None:
            return
        unit.result = UnitRunner.run_unit(solver, unit, self.settings.app.timeout)
        state.results.append((unit.result, index))
        state.focused_index = index

        if unit.result == ExecutionResult.EXECUTION_ERROR:
            state.mode = SeqMode.finished
            while state.unit_list:
                index = len(state.results)
                state.unit_list = state.unit_list[1:]
                state.results.append((ExecutionResult.EXECUTION_ERROR, index))

    def _finish_and_store(self, state: TesterState) -> None:
        state.mode = SeqMode.finished
        state.focused_index = 0

        done_list: list[tuple[ExecutionResult, int]] = []
        fail_list: list[tuple[ExecutionResult, int]] = []
        for data in state.results:
            unit_result, _ = data
            if unit_result != ExecutionResult.SUCCESS:
                fail_list.append(data)
            else:
                done_list.append(data)

        state.results = fail_list + done_list
        percent = (100 * len(done_list)) // len(state.results)
        self.task.info.rate = percent

        mode = LogItemExec.Mode.LOCK if state.locked_index else LogItemExec.Mode.FULL
        changes, total_lines = self.store_version(str(percent))
        if self.rep:
            RepositoryLoader(self.rep).save_config()
            self.rep.logger.store(
                LogItemExec()
                .set_key(self.task.basic.full_key)
                .set_mode(mode)
                .set_rate(percent)
                .set_size(changes, total_lines)
            )
