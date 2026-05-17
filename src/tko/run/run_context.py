from pathlib import Path
from tko.util.param import Param
from tko.config.settings import Settings
from tko.run.run_config import RunConfig
from tko.run.wdir import Wdir
from tko.repository.repository import Repository
from tko.game.task import Task
from tko.i18n import MsgKey, t
from tko.play.opener import Opener

class RunContext:
    def __init__(self, config: RunConfig, settings: Settings, target_list: list[Path], param: Param.Basic | None, language: str | None, repo: Repository | None = None):
        self.config = config
        self.pwd = Path(".").resolve()
        self.settings = settings
        self.target_list: list[Path] = [Path(target) for target in target_list]
        self.param = param if param is not None else Param.Basic()

        self.wdir: Wdir = Wdir(self.settings)
        self.wdir_builded: bool = False

        self.lang: str = language if language is not None else ""

        # Discovered Environment
        self.repo: None | Repository = repo
        self.task: None | Task = None
        self.track_folder: None | Path = None
        self.opener: None | Opener = None

    # --- Setters (fluent API) ---

    def set_show_track_info(self):
        self.config.show_track_info = True
        return self

    def set_no_run(self):
        self.config.no_run = True
        return self

    def set_show_self_info(self):
        self.config.show_self_info = True
        return self

    def set_complex_percent(self):
        self.config.complex_percent = True
        return self

    def set_abort_on_exec_error(self):
        self.config.abord_on_exec_error = True
        return self

    def set_timeout(self, timeout: int):
        self.config.timeout = timeout
        return self

    def set_curses(self, value: bool = True):
        self.config.curses_mode = value
        return self

    def set_lang(self, lang: str):
        self.lang = lang
        return self

    def set_opener(self, opener: Opener):
        self.opener = opener
        return self

    def set_run_without_ask(self, value: bool):
        self.config.run_without_ask = value
        return self

    def set_task(self, rep: Repository, task: Task):
        self.repo = rep
        self.task = task
        return self

    def get_task(self) -> Task:
        if self.task is None:
            raise Warning(t(MsgKey.RUN_TASK_NOT_DEFINED))
        return self.task
