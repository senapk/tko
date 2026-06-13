from tko.util.rt import RT
from tko.util.raw_terminal import RawTerminal
from tko.util.freerun import Free
from tko.enums.execution_result import ExecutionResult
from tko.run.run_context import RunContext
from tko.run.run_tracker import RunTracker
from tko.run.run_presenter import RunPresenter
from tko.run.run_loader import RunLoader
from tko.run.test_loop_service import TestLoopService
from tko.i18n import Msg
from tko.util.console import Console


_RUN_TESTING_LABEL = Msg(
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

    def get_rate(self) -> int:
        if self.ctx.config.no_run:
            return 0
        correct = [unit for unit in self.ctx.wdir.unit_list if unit.result == ExecutionResult.SUCCESS]
        if len(self.ctx.wdir.unit_list) == 0:
            return 0
        percent = (len(correct) * 100) // len(self.ctx.wdir.unit_list)
        return percent

    def run_tests(self) -> int:
        """Execute tests in raw terminal mode."""
        return self.run_tests_on_raw_term()

    def run_tests_on_raw_term(self) -> int:
        if not self.ctx.config.eval_mode:
            Console.print(RT.parse(f"{_RUN_TESTING_LABEL}").center(RawTerminal.get_terminal_size(), "═"))
        
        percent = self.test_loop.run_top_line(self.get_rate)
        self.presenter.print_diff()
        rate = self.get_rate()
        
        solver = self.ctx.wdir.solver
        if solver is None:
            return rate
        self.tracker.store_execution_log(rate, percent, solver.has_compile_error())
        return percent

    def free_run(self):
        solver = self.ctx.wdir.solver
        if solver is None:
            return
        self.tracker.store_free_run_log()
        Free.free_run(solver, standalone_mode=True)
