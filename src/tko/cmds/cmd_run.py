from pathlib import Path

from tko.game.task import Task
from tko.play.opener import Opener
from tko.repository.repository import Repository
from tko.util.param import Param
from tko.config.settings import Settings
from tko.util.rtext import RText
from tko.run.run_context import RunContext
from tko.run.run_loader import RunLoader
from tko.run.run_presenter import RunPresenter
from tko.run.run_executor import RunExecutor

class Run:
    def __init__(self, settings: Settings, target_list: list[Path], param: None | Param.Basic, language: str | None = None, repo: Repository | None = None):
        self.context = RunContext(settings, target_list, param, language, repo)

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

        if not self.context.wdir.has_solver() and self.context.wdir.has_tests() and not self.context.eval_mode:
            RunPresenter(self.context).list_mode()
            return 0
            
        executor = RunExecutor(self.context)
        
        if self.context.wdir.has_solver() and not self.context.wdir.has_tests() and not self.context.curses_mode and not self.context.no_run:
            if not self.context.eval_mode:
                executor.free_run()
            else:
                print(RText("fail: ") + "Nenhum caso de teste encontrado.")
            return 0
            
        return executor.run_tests()

    def _missing_target(self) -> bool:
        if not self.context.wdir.has_solver() and not self.context.wdir.has_tests():
            if not self.context.curses_mode:
                print(RText("fail: ") + "Nenhum arquivo de código ou de teste encontrado.")
            return True
        return False
