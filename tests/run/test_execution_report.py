from pathlib import Path
from tko.run.unit import Unit
from tko.run.execution_report import ExecutionReport
from tko.run.run_execution_summary import RunExecutionSummary
from tko.enums.execution_result import ExecutionResult


def test_execution_report_collects_failed_units():
    units = [
        Unit(case="a", input_data="1", expected="1", source=Path("a.tio")),
        Unit(case="b", input_data="2", expected="2", source=Path("b.tio")),
        Unit(case="c", input_data="3", expected="3", source=Path("c.tio")),
    ]
    units[0].result = ExecutionResult.SUCCESS
    units[1].result = ExecutionResult.WRONG_OUTPUT
    units[2].result = ExecutionResult.EXECUTION_ERROR

    summary = RunExecutionSummary(total=3, passed=1, percent=33)
    report = ExecutionReport.from_execution(summary, units, has_compile_error=False, compact=False, eval_mode=False)

    assert report.has_failures() is True
    assert len(report.get_failed_units()) == 2
    assert report.get_first_failed_unit() == units[1]


def test_execution_report_returns_none_when_no_failures():
    units = [
        Unit(case="a", input_data="1", expected="1", source=Path("a.tio")),
    ]
    units[0].result = ExecutionResult.SUCCESS

    summary = RunExecutionSummary(total=1, passed=1, percent=100)
    report = ExecutionReport.from_execution(summary, units, has_compile_error=False, compact=False, eval_mode=False)

    assert report.has_failures() is False
    assert report.get_first_failed_unit() is None
