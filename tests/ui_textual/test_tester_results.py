from __future__ import annotations

import asyncio
from pathlib import Path

from pytest import MonkeyPatch

from tko.config.settings import Settings
from tko.enums.execution_result import ExecutionResult as Result
from tko.game.task import Task
from tko.run.unit import Unit
from tko.run.unit_runner import UnitRunner
from tko.run.solver_builder import SolverBuilder
from tko.run.wdir import Wdir
from tko.tester.tester_state import SeqMode
from tko.ui_textual.tester_app import TkoTesterApp
from tko.ui_textual.palette import DARK, LIGHT


def make_app(tmp_path: Path) -> TkoTesterApp:
    settings = Settings(tmp_path)
    wdir = Wdir(settings)
    wdir.setup_solver([tmp_path / "main.py"])
    wdir.unit_list = [Unit(case=f"case-{index}", input_data=str(index)) for index in range(4)]
    for index, unit in enumerate(wdir.unit_list):
        unit.index = index
    return TkoTesterApp(settings, None, wdir, Task(), None)


def make_app_without_tests(tmp_path: Path) -> TkoTesterApp:
    settings = Settings(tmp_path)
    wdir = Wdir(settings)
    wdir.setup_solver([tmp_path / "main.py"])
    return TkoTesterApp(settings, None, wdir, Task(), None)


def mixed_results(app: TkoTesterApp) -> None:
    app.state.results = [(Result.SUCCESS, 0), (Result.WRONG_OUTPUT, 1),
                         (Result.SUCCESS, 2), (Result.EXECUTION_ERROR, 3)]
    app.state.mode = SeqMode.finished


def test_tester_shift_c_toggles_and_persists_theme(tmp_path: Path) -> None:
    async def exercise() -> None:
        app = make_app(tmp_path)
        async with app.run_test() as pilot:
            assert app.theme == DARK.name
            await pilot.press("C")
            assert app.theme == LIGHT.name
            assert Settings(tmp_path).load_settings().app.theme == LIGHT.name
            await pilot.press("C")
            assert app.theme == DARK.name
            assert Settings(tmp_path).load_settings().app.theme == DARK.name

    asyncio.run(exercise())


def test_tester_header_keeps_metadata_at_the_right_edge(tmp_path: Path) -> None:
    app = make_app_without_tests(tmp_path)

    header = app.top_bar.build_top_line_header(app.state, 80).plain()

    assert len(header) == 80
    assert header.rstrip().endswith("✗(0)")
    assert header.index("main.py") < header.index("✗(0)")
    assert header.startswith(" ")


def test_tester_header_keeps_test_cases_between_edges(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    app.wdir.source_list = [tmp_path / "tests.tio"]
    app.wdir.pack_list = [app.wdir.unit_list]

    header = app.top_bar.build_top_line_header(app.state, 80).plain()

    assert len(header) == 80
    assert "main.py" in header
    assert "tests.tio(4)" in header
    assert "00" in header
    assert header.index("00") < header.index("main.py") < header.index("tests.tio(4)")


def test_enter_runs_and_renders_tasks_without_tests(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    app = make_app_without_tests(tmp_path)

    def run_unit(solver: SolverBuilder, unit: Unit, timeout: float | None) -> Result:
        unit.set_received("program output\n")
        return Result.WRONG_OUTPUT

    monkeypatch.setattr(UnitRunner, "run_unit", run_unit)

    async def exercise() -> None:
        async with app.run_test(size=(80, 24)) as pilot:
            assert "Pressione Enter" in app._output_lines(80)[0].plain()
            await pilot.press("enter")
            await pilot.pause()

            assert app.state.mode == SeqMode.finished
            rendered = "\n".join(line.plain() for line in app._output_lines(80))
            assert "Nenhum teste cadastrado" not in rendered
            assert "program output" in rendered

    asyncio.run(exercise())


def test_finish_preserves_order_and_selects_first_error(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    mixed_results(app)
    original = list(app.state.results)
    app.executor.execution_service._finish_and_store(app.state)
    assert app.state.results == original
    assert app.state.focused_index == 1
    assert app.state.get_focused_unit(app.wdir).case == "case-1"
    assert app.current_task.info.rate == 50
    app.navigator.go_right(app.state)
    assert app.state.get_focused_unit(app.wdir).case == "case-2"


def test_filter_navigation_and_original_numbers(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    mixed_results(app)
    app.navigator.toggle_errors(app.state)
    assert app.state.focused_index == 1
    assert app.state.visible_indices(4) == [1, 3]
    tokens = app.top_bar.build_unit_list(app.state, 80).plain()
    assert "01" in tokens and "03" in tokens
    assert "00" not in tokens and "02" not in tokens
    app.navigator.go_left(app.state)
    assert app.state.focused_index == 1
    app.navigator.go_right(app.state)
    app.navigator.go_right(app.state)
    assert app.state.focused_index == 3
    app.navigator.toggle_errors(app.state)
    assert app.state.focused_index == 3


def test_empty_filter_and_all_passed(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    app.state.results = [(Result.SUCCESS, index) for index in range(4)]
    app.executor.execution_service._finish_and_store(app.state)
    assert app.state.focused_index == 0
    assert app.state.is_all_right()
    app.navigator.toggle_errors(app.state)
    assert app.state.visible_indices(4) == []
    assert app.top_bar.build_unit_list(app.state, 80).plain().strip() == ""
    assert "Nenhum teste com erro" in app._output_lines(80)[0].plain()
    app.navigator.go_right(app.state)
    assert app.state.focused_index == 0
    assert app.state.errors_only


def test_locked_result_updates_without_changing_target(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    app = make_app(tmp_path)
    mixed_results(app)
    app.state.focused_index = 2
    app.navigator.lock_unit(app.state)
    app.navigator.toggle_errors(app.state)
    assert app.state.focused_index == 2

    def run_unit(solver: SolverBuilder, unit: Unit, timeout: float) -> Result:
        assert unit is app.wdir.unit_list[2]
        return Result.WRONG_OUTPUT

    monkeypatch.setattr(UnitRunner, "run_unit", run_unit)
    app.state.mode = SeqMode.running
    app.executor.process_one(app.state)
    assert app.state.results == [(Result.WRONG_OUTPUT, 2)]
    assert app.state.visible_indices(4) == [2]


def test_filter_remains_active_on_rerun(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    app = make_app(tmp_path)
    mixed_results(app)
    app.navigator.toggle_errors(app.state)

    def build_units(wdir: Wdir) -> Wdir:
        return wdir

    monkeypatch.setattr(Wdir, "build_unit_list", build_units)
    app.executor.run_test_mode(app.state)
    assert app.state.errors_only
    assert app.state.results == []
    assert app.state.unit_list == app.wdir.unit_list
    assert app.state.visible_indices(4) == []


def test_compilation_errors_are_visible_but_untested_are_not(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    app.state.errors_only = True
    app.state.results = [(Result.COMPILATION_ERROR, 0), (Result.UNTESTED, 1)]
    assert app.state.visible_indices(4) == [0]


def test_uppercase_filter_and_lowercase_lock(tmp_path: Path) -> None:
    async def exercise() -> None:
        app = make_app(tmp_path)
        mixed_results(app)
        async with app.run_test() as pilot:
            await pilot.press("F")
            assert app.state.errors_only
            assert not app.state.locked_index
            assert app.state.focused_index == 1
            await pilot.press("f")
            assert app.state.locked_index
            await pilot.press("F")
            assert not app.state.errors_only
            assert app.state.locked_index
            assert app.state.focused_index == 1

    asyncio.run(exercise())


def test_partial_results_allow_navigation_to_unexecuted_case(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    app.state.mode = SeqMode.running
    app.state.results = [(Result.SUCCESS, 0)]
    app.navigator.go_right(app.state)
    assert app.state.get_focused_unit(app.wdir).case == "case-1"


def test_filtered_run_stays_on_error_when_next_case_passes(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    app = make_app(tmp_path)
    app.state.errors_only = True
    app.state.mode = SeqMode.running
    results = iter([Result.SUCCESS, Result.WRONG_OUTPUT, Result.SUCCESS, Result.SUCCESS])

    def run_unit(solver: SolverBuilder, unit: Unit, timeout: float) -> Result:
        return next(results)

    monkeypatch.setattr(UnitRunner, "run_unit", run_unit)
    for _ in range(4):
        app.executor.process_one(app.state)
    assert app.state.mode == SeqMode.finished
    assert app.state.focused_index == 1
    assert [index for _, index in app.state.results] == [0, 1, 2, 3]
    assert app.state.visible_indices(4) == [1]


def test_execution_error_does_not_filter_in_cases_that_never_ran(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    app = make_app(tmp_path)
    app.state.errors_only = True
    app.state.mode = SeqMode.running

    def run_unit(solver: SolverBuilder, unit: Unit, timeout: float) -> Result:
        return Result.EXECUTION_ERROR

    monkeypatch.setattr(UnitRunner, "run_unit", run_unit)
    app.executor.process_one(app.state)
    assert app.state.mode == SeqMode.finished
    assert app.state.visible_indices(4) == [0]
    assert app.state.results[1:] == [(Result.UNTESTED, index) for index in range(1, 4)]


def test_compact_layout_resizes_with_scrollable_output(tmp_path: Path) -> None:
    from textual.containers import VerticalScroll
    from textual.widgets import Static

    async def exercise() -> None:
        app = make_app(tmp_path)
        mixed_results(app)
        app.state.focused_index = 1
        app.wdir.unit_list[1].set_received("line\n" * 100)
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            header = app.query_one("#tester-header", Static)
            output = app.query_one("#tester-output", VerticalScroll)
            assert header.size.height == 1
            assert not app.query("#tester-status")
            assert output.region.y == header.region.bottom
            assert output.styles.border.top[0] in ("", "none")
            assert output.styles.padding.left == 0
            assert "WATCH" not in app._header().plain()
            assert "AUDIT" not in app._header().plain()
            assert "case-1" not in app._header().plain()
            for width in (40, 120):
                await pilot.resize_terminal(width, 24)
                await pilot.pause()
                assert len(app._header()) <= width
                assert "01" in app._header().plain()
                assert header.size.height == 1
            await pilot.press("F")
            assert app.active_bindings["F"].binding.description == "Apenas erros: ON"

    asyncio.run(exercise())
