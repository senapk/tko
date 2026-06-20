from pathlib import Path

from tko.game.task import Task
from tko.play.opener import Opener
from tko.repository.repository import Repository
from tko.repository.repository_watcher import RepositoryWatcher
from tko.util.param import Param
from tko.config.settings import Settings
from tko.util.rt import RT
from tko.run.run_config import RunConfig
from tko.run.run_context import RunContext
from tko.run.run_loader import RunLoader
from tko.run.run_presenter import RunPresenter
from tko.run.run_executor import RunExecutor
from tko.tester import Tester
from tko.i18n import Msg
from tko.util.console import Console


_RUN_NO_TEST_CASES = Msg.text(
    pt="Nenhum caso de teste encontrado.",
    en="No test cases found.",
)
_RUN_NO_SOURCE_OR_TESTS = Msg.text(
    pt="Nenhum arquivo de código ou de teste encontrado.",
    en="No source files or tests found.",
)

class Run:
    def __init__(self, settings: Settings, target_list: list[Path], param: None | Param.Basic, language: str | None = None, repo: Repository | None = None, watcher: RepositoryWatcher | None = None):
        config = RunConfig()
        self.context = RunContext(config, settings, target_list, param, language, repo)
        self.watcher = watcher

    # Fluent Setters delegated to context
    def show_track_info(self):
        self.context.set_show_track_info()
        return self
    
    def set_no_run(self):
        self.context.set_no_run()
        return self
    
    def show_self_info(self):
        self.context.set_show_self_info()
        return self

    def set_complex_percent(self):
        self.context.set_complex_percent()
        return self

    def set_abort_on_exec_error(self):
        self.context.set_abort_on_exec_error()
        return self
    
    def set_timeout(self, timeout: int):
        self.context.set_timeout(timeout)
        return self

    def set_curses(self, value: bool = True):
        self.context.set_curses(value)
        return self
   
    def set_lang(self, lang: str):
        self.context.set_lang(lang)
        return self
    
    def set_opener(self, opener: Opener):
        self.context.set_opener(opener)
        return self

    def set_run_without_ask(self, value: bool):
        self.context.set_run_without_ask(value)
        return self

    def set_task(self, rep: Repository, task: Task):
        self.context.set_task(rep, task)
        return self

    def load(self):
        loader = RunLoader(self.context)
        loader.build_wdir()
        loader.setup_task()
        
        return self

    def execute(self):
        loader = RunLoader(self.context)

        if not self.context.wdir_builded:
            loader.build_wdir()
            loader.setup_task()

        if self._missing_target():
            return 0

        if not self.context.wdir.solver and self.context.wdir.has_tests and not self.context.config.eval_mode:
            RunPresenter(self.context).list_mode()
            return 0
        
        # Decidir entre curses (TUI) e raw terminal
        if self.context.config.curses_mode:
            # TUI mode: criar Tester
            return self._run_in_curses_mode(loader)
        else:
            # Raw terminal mode: usar RunExecutor
            return self._run_in_raw_terminal_mode()

    def _run_in_curses_mode(self, loader: RunLoader) -> int:
        """Execute in curses TUI mode."""
        tester = Tester(settings = self.context.settings, repo = self.context.repo, wdir = self.context.wdir, task = self.context.get_task(), watcher = self.watcher)
        
        # Set opener
        if self.context.opener is not None:
            tester.set_opener(self.context.opener)
        else:
            tester.set_opener(loader.create_opener_for_wdir())
        
        # Set autorun if configured
        tester.set_autorun(self.context.config.run_without_ask)
        tester.run()
        return 0

    def _run_in_raw_terminal_mode(self) -> int:
        """Execute in raw terminal mode."""
        executor = RunExecutor(self.context)
        
        # Free run mode (no tests)
        if self.context.wdir.solver and not self.context.wdir.has_tests and not self.context.config.no_run:
            if not self.context.config.eval_mode:
                executor.free_run()
            else:
                Console.print(RT(f"fail: {_RUN_NO_TEST_CASES}"))
            return 0
        
        # Normal test mode
        return executor.run_tests()

    def _missing_target(self) -> bool:
        if not self.context.wdir.solver and not self.context.wdir.has_tests:
            if not self.context.config.curses_mode:
                Console.print(RT(f"fail: {_RUN_NO_SOURCE_OR_TESTS}"))
            return True
        return False
