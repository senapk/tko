from pathlib import Path
from tko.run.unit import Unit
from tko.run.execution_report import ExecutionReport
from tko.run.run_execution_summary import RunExecutionSummary
from tko.run.execution_orchestrator import ExecutionOrchestrator
from tko.enums.execution_result import ExecutionResult


def test_orchestrator_determines_persistence_needed():
    units = [
        Unit(case="a", input_data="1", expected="1", source=Path("a.tio")),
    ]
    units[0].result = ExecutionResult.SUCCESS
    summary = RunExecutionSummary(total=1, passed=1, percent=100, no_run=False)
    report = ExecutionReport.from_execution(summary, units)

    orchestrator = ExecutionOrchestrator()
    
    assert orchestrator.should_persist_execution(report) is True


def test_orchestrator_skips_persistence_when_no_run():
    units = [
        Unit(case="a", input_data="1", expected="1", source=Path("a.tio")),
    ]
    summary = RunExecutionSummary(total=1, passed=0, percent=0, no_run=True)
    report = ExecutionReport.from_execution(summary, units)

    orchestrator = ExecutionOrchestrator()
    
    assert orchestrator.should_persist_execution(report) is False


def test_orchestrator_determines_diff_display():
    units = [
        Unit(case="a", input_data="1", expected="1", source=Path("a.tio")),
        Unit(case="b", input_data="2", expected="2", source=Path("b.tio")),
    ]
    units[0].result = ExecutionResult.SUCCESS
    units[1].result = ExecutionResult.WRONG_OUTPUT

    summary = RunExecutionSummary(total=2, passed=1, percent=50)
    report = ExecutionReport.from_execution(summary, units, eval_mode=False)

    orchestrator = ExecutionOrchestrator()
    
    assert orchestrator.should_show_diff(report) is True


def test_orchestrator_hides_diff_in_eval_mode():
    units = [
        Unit(case="a", input_data="1", expected="1", source=Path("a.tio")),
        Unit(case="b", input_data="2", expected="2", source=Path("b.tio")),
    ]
    units[0].result = ExecutionResult.SUCCESS
    units[1].result = ExecutionResult.WRONG_OUTPUT

    summary = RunExecutionSummary(total=2, passed=1, percent=50)
    report = ExecutionReport.from_execution(summary, units, eval_mode=True)

    orchestrator = ExecutionOrchestrator()
    
    assert orchestrator.should_show_diff(report) is False
