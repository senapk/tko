from tko.util.rtext import RText
from tko.util.raw_terminal import RawTerminal
from tko.util.freerun import Free
from tko.enums.execution_result import ExecutionResult
from tko.tester import Tester
from tko.run.run_context import RunContext
from tko.run.run_tracker import RunTracker
from tko.run.run_presenter import RunPresenter
from tko.run.run_loader import RunLoader
from tko.run.test_loop_service import TestLoopService

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
        correct = [unit for unit in self.ctx.wdir.get_unit_list() if unit.result == ExecutionResult.SUCCESS]
        if len(self.ctx.wdir.get_unit_list()) == 0:
            return 0
        percent = (len(correct) * 100) // len(self.ctx.wdir.get_unit_list())
        return percent

    def run_tests(self) -> int:
        if self.ctx.config.curses_mode:
            self.run_test_on_curses()
            return 0
        else:
            return self.run_tests_on_raw_term()

    def run_test_on_curses(self):
        cdiff = Tester(self.ctx.settings, self.ctx.repo, self.ctx.wdir, self.ctx.get_task())
        if self.ctx.opener is not None:
            cdiff.set_opener(self.ctx.opener)
        else:
            cdiff.set_opener(self.loader.create_opener_for_wdir())
        cdiff.set_autorun(self.ctx.config.run_without_ask)
        cdiff.run()

    def run_tests_on_raw_term(self) -> int:
        if not self.ctx.config.eval_mode:
            print(RText.parse(" Testando o código com os casos de teste ").center(RawTerminal.get_terminal_size(), "═"))
        
        percent = self.test_loop.run_top_line(self.get_rate)
        self.presenter.print_diff()
        rate = self.get_rate()
        
        self.tracker.store_execution_log(rate, percent, self.ctx.wdir.get_solver().has_compile_error())
        return percent

    def free_run(self):
        self.tracker.store_free_run_log()
        Free.free_run(self.ctx.wdir.get_solver(), standalone_mode=True)
