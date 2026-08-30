from __future__ import annotations

from tko.run.execution_report import ExecutionReport


class ExecutionOrchestrator:
    """
    Pure application service that orchestrates test execution without I/O.
    Coordinates the flow of data from preparation to result without printing or persisting directly.
    """

    def __init__(self):
        pass

    def prepare_report(
        self,
        test_result: int,
        report: ExecutionReport,
    ) -> tuple[ExecutionReport, int]:
        """
        Prepare the execution report with the final test result.
        Returns the report and the final percentage to be returned.
        """
        return report, test_result

    def should_persist_execution(self, report: ExecutionReport) -> bool:
        """Determine if execution should be persisted to logs."""
        return report.summary.total > 0 and not report.summary.no_run

    def should_show_diff(self, report: ExecutionReport) -> bool:
        """Determine if diff should be shown to the user."""
        return report.has_failures() and not report.eval_mode
