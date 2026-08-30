from pathlib import Path
from tko.run.unit import Unit
from tko.run.solver_builder import SolverBuilder
from tko.run.run_context import RunContext
from tko.run.run_config import RunConfig
from tko.config.settings import Settings

import pytest

from tko.enums.execution_result import ExecutionResult
from tko.run.test_loop_service import TestLoopService as _TestLoopService
from tko.run.unit import Unit


class _FakeSolver:
    pass



class _FakeWdir:
    def __init__(self, units: list[Unit]):
        self._units = units
        self._solver = _FakeSolver()
    @property
    def unit_list(self):
        return self._units
    def resume_splitted(self):
        return "fake/resume"
    def get_unit_list(self):
        return self._units
    def get_solver(self):
        return self._solver


def _make_ctx(units: list[Unit], no_run: bool, abort_on_exec_error: bool) -> RunContext:
    config = RunConfig()
    config.no_run = no_run
    config.abord_on_exec_error = abort_on_exec_error
    config.timeout = 7
    config.show_track_info = False
    settings = Settings(Path("/tmp"))
    ctx = RunContext(
        config=config,
        settings=settings,
        target_list=[],
        param=None,
        language=None,
        repo=None,
    )
    ctx.wdir = _FakeWdir(units)  # type: ignore
    return ctx


def test_run_top_line_marks_all_untested_when_no_run(monkeypatch: pytest.MonkeyPatch):
    calls: list[tuple[object, object, int]] = []

    def _fake_run_unit(solver: SolverBuilder, unit: Unit, timeout: int) -> ExecutionResult:
        calls.append((solver, unit, timeout))
        return ExecutionResult.SUCCESS

    monkeypatch.setattr("tko.run.test_loop_service.UnitRunner.run_unit", _fake_run_unit)

    units = [Unit(case="a", input_data="1", expected="1", source=Path("a.tio"))]
    service = _TestLoopService(_make_ctx(units, no_run=True, abort_on_exec_error=False))

    percent = service.run_top_line(lambda: 77)

    assert percent == 0
    assert units[0].result == ExecutionResult.UNTESTED
    assert calls == []


def test_run_top_line_stops_after_execution_error_when_abort_enabled(monkeypatch: pytest.MonkeyPatch):
    calls: list[tuple[object, object, int]] = []
    results = [ExecutionResult.EXECUTION_ERROR, ExecutionResult.SUCCESS]

    def _fake_run_unit(solver: SolverBuilder, unit: Unit, timeout: int) -> ExecutionResult:
        calls.append((solver, unit, timeout))
        return results[len(calls) - 1]

    monkeypatch.setattr("tko.run.test_loop_service.UnitRunner.run_unit", _fake_run_unit)

    units = [
        Unit(case="a", input_data="1", expected="1", source=Path("a.tio")),
        Unit(case="b", input_data="2", expected="2", source=Path("b.tio")),
    ]
    service = _TestLoopService(_make_ctx(units, no_run=False, abort_on_exec_error=True))

    percent = service.run_top_line(lambda: 42)

    assert percent == 42
    assert units[0].result == ExecutionResult.EXECUTION_ERROR
    assert units[1].result == ExecutionResult.UNTESTED
    assert len(calls) == 1
    assert calls[0][2] == 7


def test_run_progress_calculates_success_percentage_from_units():
    from tko.run.run_progress import RunProgress

    units = [
        Unit(case="a", input_data="1", expected="1", source=Path("a.tio")),
        Unit(case="b", input_data="2", expected="2", source=Path("b.tio")),
        Unit(case="c", input_data="3", expected="3", source=Path("c.tio")),
    ]
    units[0].result = ExecutionResult.SUCCESS
    units[1].result = ExecutionResult.SUCCESS
    units[2].result = ExecutionResult.WRONG_OUTPUT

    progress = RunProgress.from_units(units)

    assert progress.total == 3
    assert progress.passed == 2
    assert progress.percent == 66


def test_run_progress_returns_zero_when_no_run_is_enabled():
    from tko.run.run_progress import RunProgress

    units = [
        Unit(case="a", input_data="1", expected="1", source=Path("a.tio")),
    ]
    units[0].result = ExecutionResult.SUCCESS

    progress = RunProgress.from_units(units, no_run=True)

    assert progress.percent == 0
    assert progress.passed == 0


def test_run_execution_settings_are_extracted_from_config():
    from tko.run.run_execution_settings import RunExecutionSettings

    config = RunConfig()
    config.no_run = True
    config.timeout = 12
    config.curses_mode = True

    settings = RunExecutionSettings.from_config(config)

    assert settings.no_run is True
    assert settings.timeout == 12
    assert settings.curses_mode is True