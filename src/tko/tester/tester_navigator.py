from __future__ import annotations

from collections.abc import Callable

from tko.config.settings import Settings
from tko.game.task import Task
from tko.play.gui_keys import GuiKeys
from tko.repository.repository import Repository
from tko.run.wdir import Wdir
from tko.tester import tester_util
from tko.tester.tester_executor import TesterExecutor
from tko.tester.tester_state import SeqMode, TesterState


class TesterNavigator:
    """State transitions for the test screen, independent of a UI toolkit."""

    def __init__(
        self,
        settings: Settings,
        rep: Repository | None,
        wdir: Wdir,
        task: Task,
        executor: TesterExecutor,
        notify: Callable[[str], None] | None = None,
    ) -> None:
        self.settings = settings
        self.rep = rep
        self.wdir = wdir
        self.task = task
        self.executor = executor
        self.notify = notify or (lambda _message: None)

    def _locked(self, arrow: str) -> None:
        self.notify(f"{arrow}\nAtividade travada\nAperte {GuiKeys.pin} para destravar")

    def go_left(self, state: TesterState) -> None:
        if state.mode in (SeqMode.intro, SeqMode.finished):
            state.mode = SeqMode.select
        if state.locked_index:
            self._locked("←")
            return
        if not self.wdir.get_solver().has_compile_error():
            state.focused_index = max(0, state.focused_index - 1)
            state.diff_first_line = 1000

    def go_right(self, state: TesterState) -> None:
        if state.mode == SeqMode.intro:
            state.mode = SeqMode.select
            state.focused_index = 0
            return
        if state.mode == SeqMode.finished:
            state.mode = SeqMode.select
        if state.locked_index:
            self._locked("→")
            return
        if not self.wdir.get_solver().has_compile_error():
            state.focused_index = min(len(self.wdir.unit_list) - 1, state.focused_index + 1)
            state.diff_first_line = 1000

    def go_down(self, state: TesterState) -> None:
        if state.mode == SeqMode.intro:
            state.mode = SeqMode.select
        state.diff_first_line += 1

    def go_up(self, state: TesterState) -> None:
        if state.mode == SeqMode.intro:
            state.mode = SeqMode.select
        state.diff_first_line = max(0, state.diff_first_line - 1)

    def change_main(self, state: TesterState) -> None:
        solver_names = tester_util.get_solver_names(self.wdir)
        if len(solver_names) == 1:
            self.notify("Seu projeto só tem um arquivo de solução.")
            return
        self.task.main_idx = (self.task.main_idx + 1) % len(solver_names)

    def lock_unit(self, state: TesterState) -> None:
        state.locked_index = not state.locked_index
        if state.mode == SeqMode.intro:
            state.mode = SeqMode.select
        if state.locked_index:
            from tko.enums.execution_result import ExecutionResult

            state.results = [(ExecutionResult.UNTESTED, index) for _, index in state.results]

    def change_limit(self, state: TesterState) -> None:
        value = self.settings.app.timeout
        value = 1 if value == 0 else value * 2
        self.settings.app.timeout = 0 if value >= 5 else value
        self.settings.save_settings()
