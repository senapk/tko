import enum
from typing import Protocol

from tko.enums.execution_result import ExecutionResult
from tko.run.unit import Unit


class UnitSource(Protocol):
    @property
    def unit_list(self) -> list[Unit]: ...

    @property
    def has_tests(self) -> bool: ...


class SeqMode(enum.Enum):
    intro    = 0
    select   = 1
    running  = 2
    finished = 3


class TesterState:
    """Estado mutável puro do Tester — sem dependências de play/*.py."""

    def __init__(self, unit_list: list[Unit]) -> None:
        self.results: list[tuple[ExecutionResult, int]] = []
        self.unit_list: list[Unit] = list(unit_list)
        self.exit: bool = False
        self.diff_first_line: int = 1000
        self.length: int = 1
        self.space: int = 0
        self.mode: SeqMode = SeqMode.intro
        self.locked_index: bool = False
        self.errors_only: bool = False
        self.focused_index: int = 0
        self.resumes: list[str] = []
        self.dummy_unit: Unit = Unit()

    # ------------------------------------------------------------------
    # Queries que dependem apenas do estado interno + wdir/unit
    # ------------------------------------------------------------------

    def is_all_right(self) -> bool:
        if self.locked_index or len(self.results) == 0:
            return False
        if self.mode != SeqMode.finished:
            return False
        for result, _ in self.results:
            if result != ExecutionResult.SUCCESS:
                return False
        return True

    def visible_indices(self, count: int) -> list[int]:
        if not self.errors_only:
            return list(range(count))
        return sorted(index for result, index in self.results
                      if result not in (ExecutionResult.SUCCESS, ExecutionResult.UNTESTED)
                      and 0 <= index < count)

    def reconcile_focus(self, count: int) -> None:
        if self.locked_index:
            return
        indices = self.visible_indices(count)
        if indices and self.focused_index not in indices:
            self.focused_index = indices[0]

    def get_focused_unit(self, wdir: UnitSource) -> Unit:
        if not wdir.has_tests:
            return self.dummy_unit
        return wdir.unit_list[self.focused_index]
