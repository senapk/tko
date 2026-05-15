from collections.abc import Callable

from tko.config.settings import Settings
from tko.enums.execution_result import ExecutionResult
from tko.game.task import Task
from tko.logger.log_item_exec import LogItemExec
from tko.repository.repository import Repository
from tko.run.wdir import Wdir
from tko.tester import tester_util
from tko.tester.tester_state import SeqMode, TesterState
from tko.tester.tester_top_bar import TesterTopBar
from tko.util.freerun import Free
from tko.util.raw_terminal import RawTerminal


class TesterRunModeService:
    def __init__(
        self,
        settings: Settings,
        rep: Repository | None,
        wdir: Wdir,
        task: Task,
        top_bar: TesterTopBar,
        store_version: Callable[[str], tuple[bool, int]],
    ) -> None:
        self.settings = settings
        self.rep = rep
        self.wdir = wdir
        self.task = task
        self.top_bar = top_bar
        self.store_version = store_version

    def run_test_mode(self, state: TesterState) -> None:
        state.mode = SeqMode.running
        if self.wdir.is_autoload():
            self.wdir.autoload()
        self.wdir.build()

        from tko.widget.fmt import Fmt
        Fmt.clear()

        solver_names = tester_util.get_solver_names(self.wdir)
        index = self.task.main_idx % len(solver_names)
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
                .set_key(self.task.basic.full_key)
                .set_mode(LogItemExec.Mode.FREE)
                .set_size(changes, total_lines)
            )

        header = self.top_bar.build_top_line_header(state, RawTerminal.get_terminal_size())
        return lambda: Free.free_run(
            self.wdir.get_solver(),
            standalone_mode=False,
            header=header,
        )
