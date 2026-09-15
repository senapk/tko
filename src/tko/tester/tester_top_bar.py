from __future__ import annotations

from pathlib import Path
from typing import Callable, Protocol

from tko.config.app_settings import AppSettings
from tko.enums.execution_result import ExecutionResult
from tko.game.task import Task
from tko.repository.repository import Repository
from tko.tester import tester_util
from tko.run.solver_builder import SolverBuilder
from tko.tester.tester_state import UnitSource
from tko.tester.tester_state import SeqMode, TesterState
from tko.util.aligner import Aligner
from tko.util.rt import RT
from tko.widget.button import Button
import time


def _edit_audit_info(edit_mode_fn: Callable[[], bool], audit_info_fn: Callable[[], bool], timed: bool) -> RT:
    states = ("█▄", "█▀", "▀█", "▄█")
    timer = Button.info_label(states[int(time.time()) % len(states)], color="y", sep="") if timed else RT("  ")
    return RT.join(
        [
            Button.toggle_bt("WATCH EDIT " + ("ON" if edit_mode_fn() else "OFF"), active=edit_mode_fn(), enabled=edit_mode_fn()),
            timer,
            Button.toggle_bt("AUDIT MODE " + ("ON" if audit_info_fn() else "OFF"), active=audit_info_fn(), enabled=audit_info_fn()),
        ],
        "",
    )


class HeaderSource(UnitSource, Protocol):
    def get_solver(self) -> SolverBuilder: ...
    def solvers_names(self) -> list[str]: ...
    def sources_names(self) -> list[tuple[str, str]]: ...


class TesterTopBar:
    """Presentation-neutral header formatter for the Textual test screen."""

    def __init__(
        self,
        repo: Repository | None,
        wdir: HeaderSource,
        task: Task,
        app: AppSettings,
        edit_fn: Callable[[], bool],
        audit_fn: Callable[[], bool],
    ) -> None:
        self.repo = repo
        self.wdir = wdir
        self.task = task
        self.app = app
        self.edit_fn = edit_fn
        self.audit_fn = audit_fn

    def build_top_line_header(self, state: TesterState, width: int, timed: bool) -> RT:
        folder = Path()
        if self.repo is not None:
            folder = self.repo.task_resolver.target_folder(self.task) or Path()
        activity = Button.info_label(folder.name)
        solver_names = sorted(self.wdir.solvers_names())
        solvers = RT.join(
            [Button.toggle_bt(name, active=index == self.task.main_idx) for index, name in enumerate(solver_names)],
            " ",
        )
        if state.mode == SeqMode.running:
            solvers = RT(f" ({len(state.results)}/{len(self.wdir.unit_list)}) ", "R")
        source_names = ", ".join(f"{name[0]}({name[1]})" for name in self.wdir.sources_names())
        sources = Button.info_label(source_names or "Nenhum teste cadastrado")
        return Aligner.distribute_with_filler(activity, _edit_audit_info(self.edit_fn, self.audit_fn, timed), RT.join([solvers, sources], " "), "─", width)

    def build_focused_case(self, state: TesterState, width: int) -> RT:
        """Describe the selected case or the current compilation result."""
        if not self.wdir.has_tests:
            return RT("Nenhum teste cadastrado.", "y").center(width, " ")
        if self.wdir.get_solver().has_compile_error():
            return RT("Erro de compilação", "r*").center(width, " ")
        if state.errors_only and not state.visible_indices(len(self.wdir.unit_list)):
            return RT("Nenhum teste com erro.", "y").center(width, " ")
        if state.errors_only and state.focused_index not in state.visible_indices(len(self.wdir.unit_list)):
            return RT("Caso fixado fora do filtro de erros.", "y").center(width, " ")
        if state.mode == SeqMode.intro:
            return RT("Pressione Enter para testar.", "y").center(width, " ")
        if state.is_all_right():
            return RT("Todos os casos passaram.", "g*").center(width, " ")
        return state.get_focused_unit(self.wdir).str(pad=False).center(width, " ")

    def build_unit_list(self, state: TesterState, width: int) -> RT:
        """Render a compact, horizontally windowed result token for each case."""
        if not self.wdir.has_tests:
            return RT()

        result_by_index = {index: result for result, index in state.results}
        indices = state.visible_indices(len(self.wdir.unit_list))
        count = len(indices)
        position = indices.index(state.focused_index) if state.focused_index in indices else 0
        cell_width = 5  # two-digit index, result symbol and surrounding spaces
        visible = max(1, width // cell_width)
        start = max(0, min(position - visible // 2, count - visible))
        end = min(count, start + visible)
        tokens: list[RT] = []
        for index in indices[start:end]:
            token = tester_util.get_token(result_by_index.get(index, ExecutionResult.UNTESTED))
            entry: RT = RT(f"{index:02}").set_style(token.runs[0][0]) + token
            if index == state.focused_index and state.mode != SeqMode.intro:
                entry = entry.add_style("X")
            tokens.append(entry)

        left = "… " if start else ""
        right = " …" if end < count else ""
        return (RT(left) + RT.join(tokens, "  ") + RT(right)).center(width, " ")
