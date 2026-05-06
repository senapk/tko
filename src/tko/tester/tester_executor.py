from typing import Callable

from tko.config.settings import Settings
from tko.enums.execution_result import ExecutionResult
from tko.game.task import Task
from tko.logger.log_item_exec import LogItemExec
from tko.floating.floating_manager import FloatingManager
from tko.tester.tester_state import TesterState, SeqMode
from tko.tester.tester_top_bar import TesterTopBar
from tko.tester import tester_util
from tko.repository.repository import Repository
from tko.repository.repository_loader import RepositoryLoader
from tko.run.unit import Unit
from tko.run.unit_runner import UnitRunner
from tko.run.wdir import Wdir
from tko.util.freerun import Free
from tko.util.raw_terminal import RawTerminal
from tko.logger.tracker import Tracker


class TesterExecutor:

    def __init__(
        self,
        settings: Settings,
        rep: Repository | None,
        wdir: Wdir,
        task: Task,
        fman: FloatingManager,
        top_bar: TesterTopBar,
    ) -> None:
        self.settings = settings
        self.rep = rep
        self.wdir = wdir
        self.task = task
        self.fman = fman
        self.top_bar = top_bar
        self._dummy_unit = Unit()

    def store_version(self, result: str) -> tuple[bool, int]:
        if self.rep is None:
            return False, 0
        track_folder = self.rep.paths.get_track_task_folder(self.task.identity.get_full_key())
        tracker = Tracker()
        tracker.set_folder(track_folder)
        tracker.set_files(self.wdir.get_solver().args_list)
        tracker.set_result(result)
        return tracker.store()

    def process_one(self, state: TesterState) -> None:
        if state.mode != SeqMode.running:
            return

        solver = self.wdir.get_solver()

        if solver.has_compile_error():
            mode = LogItemExec.Mode.LOCK if state.locked_index else LogItemExec.Mode.FULL
            changes, total_lines = self.store_version("0")
            if self.rep:
                self.rep.logger.store(
                    LogItemExec()
                    .set_key(self.task.identity.get_full_key())
                    .set_mode(mode)
                    .set_fail(LogItemExec.Fail.COMP)
                    .set_size(changes, total_lines)
                )
            state.mode = SeqMode.finished
            while state.unit_list:
                index = len(state.results)
                state.unit_list = state.unit_list[1:]
                state.results.append((ExecutionResult.COMPILATION_ERROR, index))
            return

        if state.locked_index or not self.wdir.has_tests():
            state.mode = SeqMode.finished
            unit = state.get_focused_unit(self.wdir, self._dummy_unit)
            unit.result = UnitRunner.run_unit(solver, unit, self.settings.app.timeout)
            rate = 100 if unit.result == ExecutionResult.SUCCESS else 0
            changes, total_lines = self.store_version(str(rate))
            if self.rep:
                self.rep.logger.store(
                    LogItemExec()
                    .set_key(self.task.identity.get_full_key())
                    .set_mode(LogItemExec.Mode.LOCK)
                    .set_rate(rate)
                    .set_size(changes, total_lines)
                )
            return

        if self.wdir.has_tests():
            index = len(state.results)
            unit = state.unit_list[0]
            state.unit_list = state.unit_list[1:]
            unit.result = UnitRunner.run_unit(solver, unit, self.settings.app.timeout)
            state.results.append((unit.result, index))
            state.focused_index = index
            if unit.result == ExecutionResult.EXECUTION_ERROR:
                state.mode = SeqMode.finished
                while state.unit_list:
                    index = len(state.results)
                    state.unit_list = state.unit_list[1:]
                    state.results.append((ExecutionResult.EXECUTION_ERROR, index))

        if len(state.unit_list) == 0:
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
            percent: int = (100 * len(done_list)) // len(state.results)
            self.task.info.rate = percent
            mode = LogItemExec.Mode.LOCK if state.locked_index else LogItemExec.Mode.FULL
            changes, total_lines = self.store_version(str(percent))
            if self.rep:
                RepositoryLoader(self.rep).save_config()
                self.rep.logger.store(
                    LogItemExec()
                    .set_key(self.task.identity.get_full_key())
                    .set_mode(mode)
                    .set_rate(percent)
                    .set_size(changes, total_lines)
                )

    def run_test_mode(self, state: TesterState) -> None:
        state.mode = SeqMode.running
        if self.wdir.is_autoload():
            self.wdir.autoload()
        self.wdir.build()

        from tko.widget.fmt import Fmt
        Fmt.clear()

        solver_names = tester_util.get_solver_names(self.wdir)
        index = self.task.main_idx
        solver_selected = solver_names[index % len(solver_names)]
        self.wdir.get_solver().set_main(solver_selected).reset()

        if state.locked_index:
            for i in range(len(state.results)):
                _, idx = state.results[i]
                state.results[i] = (ExecutionResult.UNTESTED, idx)
        else:
            state.focused_index = 0
            state.results = []
            state.unit_list = list(self.wdir.get_unit_list())

    def run_exec_mode(self, state: TesterState) -> Callable[[], bool]:
        state.mode = SeqMode.running
        if self.wdir.is_autoload():
            self.wdir.autoload()
            self.wdir.get_solver().set_main(tester_util.get_solver_names(self.wdir)[self.task.main_idx])
        state.mode = SeqMode.finished
        changes, total_lines = self.store_version("---")
        if self.rep:
            self.rep.logger.store(
                LogItemExec()
                .set_key(self.task.identity.get_full_key())
                .set_mode(LogItemExec.Mode.FREE)
                .set_size(changes, total_lines)
            )
        header = self.top_bar.build_top_line_header(state, RawTerminal.get_terminal_size())
        return lambda: Free.free_run(
            self.wdir.get_solver(),
            standalone_mode=False,
            header=header,
        )
