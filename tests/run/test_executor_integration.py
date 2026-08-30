from pathlib import Path
from tko.run.unit import Unit
from tko.run.run_context import RunContext
from tko.run.run_config import RunConfig
from tko.config.settings import Settings
from tko.run.run_executor import RunExecutor
from tko.enums.execution_result import ExecutionResult


class _FakeWdir:
    def __init__(self, units: list[Unit]):
        self._units = units
        self.solver = None

    @property
    def unit_list(self):
        return self._units

    def resume_splitted(self):
        return "test/resume"

    def get_solver(self):
        return self.solver


def test_executor_generates_summary_from_units():
    config = RunConfig()
    config.no_run = False
    settings = Settings(Path("/tmp"))
    ctx = RunContext(
        config=config,
        settings=settings,
        target_list=[],
        param=None,
        language=None,
        repo=None,
    )

    units = [
        Unit(case="a", input_data="1", expected="1", source=Path("a.tio")),
        Unit(case="b", input_data="2", expected="2", source=Path("b.tio")),
        Unit(case="c", input_data="3", expected="3", source=Path("c.tio")),
    ]
    units[0].result = ExecutionResult.SUCCESS
    units[1].result = ExecutionResult.SUCCESS
    units[2].result = ExecutionResult.WRONG_OUTPUT

    ctx.wdir = _FakeWdir(units)  # type: ignore

    executor = RunExecutor(ctx)
    summary = executor.get_summary()

    assert summary.total == 3
    assert summary.passed == 2
    assert summary.percent == 66
    assert summary.no_run is False


def test_executor_report_has_failures():
    config = RunConfig()
    config.no_run = False
    settings = Settings(Path("/tmp"))
    ctx = RunContext(
        config=config,
        settings=settings,
        target_list=[],
        param=None,
        language=None,
        repo=None,
    )

    units = [
        Unit(case="a", input_data="1", expected="1", source=Path("a.tio")),
        Unit(case="b", input_data="2", expected="2", source=Path("b.tio")),
    ]
    units[0].result = ExecutionResult.SUCCESS
    units[1].result = ExecutionResult.EXECUTION_ERROR

    ctx.wdir = _FakeWdir(units)  # type: ignore

    executor = RunExecutor(ctx)
    report = executor.get_report()

    assert report.has_failures() is True
    assert len(report.get_failed_units()) == 1
    assert report.summary.percent == 50
