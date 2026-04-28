from pathlib import Path
from typing import Optional

from tko.util.param import Param
from tko.config.settings import Settings
from tko.run.wdir import Wdir
from tko.repository.repository import Repository
from tko.game.task import Task
from tko.play.opener import Opener

class RunContext:
    def __init__(self, settings: Settings, target_list: list[Path], param: Optional[Param.Basic]):
        self.settings = settings
        self.target_list: list[Path] = [Path(target) for target in target_list]
        self.param = param if param is not None else Param.Basic()
        
        self.wdir: Wdir = Wdir(self.settings)
        self.wdir_builded: bool = False
        
        # State
        self.curses_mode: bool = False
        self.lang: str = ""
        self.run_without_ask: bool = True
        self.show_track_info: bool = False
        self.show_self_info: bool = False
        self.eval_mode: bool = False
        self.complex_percent: bool = False
        self.abord_on_exec_error: bool = False
        self.no_run: bool = False
        self.timeout: int = 0
        
        # Discovered Environment
        self.rep: Optional[Repository] = None
        self.task: Optional[Task] = None
        self.track_folder: Optional[Path] = None
        self.opener: Optional[Opener] = None

    def set_show_track_info(self):
        self.show_track_info = True
        return self
    
    def set_no_run(self):
        self.no_run = True
        return self
    
    def set_show_self_info(self):
        self.show_self_info = True
        return self

    def set_complex_percent(self):
        self.complex_percent = True
        return self

    def set_abort_on_exec_error(self):
        self.abord_on_exec_error = True
        return self
    
    def set_timeout(self, timeout: int):
        self.timeout = timeout
        return self

    def set_curses(self, value: bool = True):
        self.curses_mode = value
        return self
   
    def set_lang(self, lang: str):
        self.lang = lang
        return self
    
    def set_opener(self, opener: Opener):
        self.opener = opener
        return self

    def set_run_without_ask(self, value: bool):
        self.run_without_ask = value
        return self

    def set_task(self, rep: Repository, task: Task):
        self.rep = rep
        self.task = task
        return self
    
    def get_task(self) -> Task:
        if self.task is None:
            raise Warning("Task não definida")
        return self.task
