from __future__ import annotations

from pathlib import Path
from typing import Protocol

from tko.enums.execution_result import ExecutionResult
from tko.game.task import Task
from tko.repository.repository import Repository
from tko.tester import tester_util
from tko.tester.tester_state import UnitSource
from tko.tester.tester_state import SeqMode, TesterState
from tko.util.rt import RT
from tko.widget.button import Button
class HeaderSource(UnitSource, Protocol):
    def solvers_names(self) -> list[str]: ...
    def sources_names(self) -> list[tuple[str, str]]: ...


class TesterTopBar:
    """Presentation-neutral header formatter for the Textual test screen."""

    def __init__(
        self,
        repo: Repository | None,
        wdir: HeaderSource,
        task: Task,
    ) -> None:
        self.repo = repo
        self.wdir = wdir
        self.task = task

    def build_top_line_header(self, state: TesterState, width: int) -> RT:
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
        right: RT = RT.join([solvers, sources], " ")
        width = max(0, width)
        # Reserve most of the line for cases; shorten metadata first.
        side_width: int = max(0, (width - min(width, max(12, width // 2)) - 2) // 2)
        left: RT = activity.truncate(side_width)
        right = right.truncate(side_width)
        if side_width == 0:
            return self.build_unit_list(state, width)
        center_width: int = width - 2 * side_width - 2
        return left.ljust(side_width) + " " + self.build_unit_list(state, center_width) + " " + right.rjust(side_width)

    def build_unit_list(self, state: TesterState, width: int) -> RT:
        """Render a compact, horizontally windowed result token for each case."""
        if not self.wdir.has_tests:
            return RT()

        result_by_index = {index: result for result, index in state.results}
        indices = state.visible_indices(len(self.wdir.unit_list))
        count = len(indices)
        position = indices.index(state.focused_index) if state.focused_index in indices else 0
        if count == 0 or width <= 0:
            return RT().center(max(0, width), " ")

        def render(start: int, end: int) -> RT:
            tokens: list[RT] = []
            for index in indices[start:end]:
                token: RT = tester_util.get_token(result_by_index.get(index, ExecutionResult.UNTESTED))
                entry: RT = RT(f"{index:02}").set_style(token.runs[0][0]) + token
                if index == state.focused_index and state.mode != SeqMode.intro:
                    entry = entry.add_style("X")
                tokens.append(entry)
            return RT("… " if start else "") + RT.join(tokens, "  ") + RT(" …" if end < count else "")

        start: int = position
        end: int = position + 1
        while start > 0 or end < count:
            next_start: int = max(0, start - 1)
            next_end: int = min(count, end + 1)
            if len(render(next_start, next_end)) <= width:
                start, end = next_start, next_end
            elif start > 0 and len(render(next_start, end)) <= width:
                start = next_start
            elif end < count and len(render(start, next_end)) <= width:
                end = next_end
            else:
                break
        return render(start, end).truncate(width).center(width, " ")
