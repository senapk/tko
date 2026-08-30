from tko.util.raw_terminal import RawTerminal
from tko.util.freerun import Free
from tko.run.run_context import RunContext
from tko.run.run_tracker import RunTracker
from tko.run.run_presenter import RunPresenter
from tko.run.run_loader import RunLoader
from tko.run.test_loop_service import TestLoopService
from tko.run.run_execution_summary import RunExecutionSummary
from tko.run.execution_report import ExecutionReport
from tko.run.execution_orchestrator import ExecutionOrchestrator
from tko.i18n import Msg
from tko.util.console import Console


_RUN_TESTING_LABEL = Msg.text(
    pt=" Testando o código com os casos de teste ",
    en=" Testing code with test cases ",
)

class RunExecutor:
    def __init__(self, ctx: RunContext):
        self.ctx = ctx
        self.tracker = RunTracker(ctx)
        self.presenter = RunPresenter(ctx)
        self.loader = RunLoader(ctx)
        self.test_loop = TestLoopService(ctx)
        self.orchestrator = ExecutionOrchestrator()

    def get_rate(self) -> int:
        summary = self.get_summary()
        return summary.percent

    def get_summary(self) -> RunExecutionSummary:
        return RunExecutionSummary.from_wdir(self.ctx.wdir, no_run=self.ctx.config.no_run)

    def get_report(self) -> ExecutionReport:
        summary = self.get_summary()
        solver = self.ctx.wdir.solver
        has_compile_error = bool(solver is not None and solver.has_compile_error())
        return ExecutionReport.from_execution(
            summary=summary,
            units=self.ctx.wdir.unit_list,
            has_compile_error=has_compile_error,
            compact=self.ctx.param.compact,
            eval_mode=self.ctx.config.eval_mode,
        )

    def run_tests(self) -> int:
        """Execute tests in raw terminal mode."""
        return self.run_tests_on_raw_term()

    def run_tests_on_raw_term(self) -> int:
        if not self.ctx.config.eval_mode:
            Console.print(_RUN_TESTING_LABEL.t().center(RawTerminal.get_terminal_size(), "═"))
        
        percent = self.test_loop.run_top_line(self.get_rate)
        self.presenter.print_diff()
        rate = self.get_rate()
        
        solver = self.ctx.wdir.solver
        if solver is None:
            return rate
        self.tracker.store_execution_log(rate, percent, solver.has_compile_error())
        return percent

    def free_run(self) -> None:
        solver = self.ctx.wdir.solver
        if solver is None:
            return
        self.tracker.store_free_run_log()
        Free.free_run(solver, standalone_mode=True)
