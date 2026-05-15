from tko.util.rtext import RText
from tko.util.raw_terminal import RawTerminal
from tko.util.symbols import Symbols
from tko.util.freerun import Free
from tko.enums.execution_result import ExecutionResult
from tko.run.unit_runner import UnitRunner
from tko.tester import Tester
from tko.logger.log_sort import LogSort
from tko.logger.task_resume import TaskResume
from tko.run.run_context import RunContext
from tko.run.run_tracker import RunTracker
from tko.run.run_presenter import RunPresenter
from tko.run.run_loader import RunLoader

class RunExecutor:
    def __init__(self, ctx: RunContext):
        self.ctx = ctx
        self.tracker = RunTracker(ctx)
        self.presenter = RunPresenter(ctx)
        self.loader = RunLoader(ctx)

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
        
        percent = self._run_all_tests_top_line()
        self.presenter.print_diff()
        rate = self.get_rate()
        
        self.tracker.store_execution_log(rate, percent, self.ctx.wdir.get_solver().has_compile_error())
        return percent

    def free_run(self):
        self.tracker.store_free_run_log()
        Free.free_run(self.ctx.wdir.get_solver(), standalone_mode=True)

    def _run_all_tests_top_line(self) -> int:
        print(RText(Symbols.opening) + self.ctx.wdir.resume_splitted(), end="")
        print(" [", end="")
        first = True
        execution_error = False
        for unit in self.ctx.wdir.get_unit_list():
            if first:
                first = False
            else:
                print(" ", end="")
            solver = self.ctx.wdir.get_solver()
            if self.ctx.config.no_run or (execution_error and self.ctx.config.abord_on_exec_error):
                unit.result = ExecutionResult.UNTESTED
            else:
                unit.result = UnitRunner.run_unit(solver, unit, timeout=self.ctx.config.timeout)
                if unit.result == ExecutionResult.EXECUTION_ERROR:
                    execution_error = True
            print(ExecutionResult.get_symbol(unit.result), end="")
        print("] ", end="")
        
        if self.ctx.config.show_track_info:
            if self.ctx.repo is not None:
                logger = self.ctx.repo.logger
                log_sort: LogSort | None = logger.tasks.task_dict.get(self.ctx.get_task().basic.full_key, None)
                if log_sort is not None:
                    log_resume = TaskResume(self.ctx.get_task().basic.full_key, "").from_log_sort(log_sort)
                    print(RText(f"time:{log_resume.resume.minutes:.0f}, diff:{log_resume.resume.versions}, runs:{log_resume.resume.executions},", "g") + " ", end="", flush=True)

        percent: float = 0 if self.ctx.config.no_run else self.get_rate()
        print(f"{percent:.0f}%")
        return round(percent)
