from tko.cmds.cmd_run import Run
from tko.util.param import Param
from tko.settings.settings import Settings
from tko.enums.diff_count import DiffCount

class CmdEval:
    EVAL_TIMEOUT_DEFAULT = 5
    
    def __init__(self):
        self.target_list: list[str] = []
        self.norun: bool = False
        self.track: bool = False
        self.load_self: bool = False
        self.complex: bool = False
        self.timeout: int = CmdEval.EVAL_TIMEOUT_DEFAULT
    
    def set_norun(self, value: bool | None = None):
        if value is not None:
            self.norun = value
        return self
    
    def set_track(self, value: bool | None = None):
        if value is not None:
            self.track = value
        return self
    
    def set_self(self, value: bool | None = None):
        if value is not None:
            self.load_self = value
        return self
    
    def set_complex(self, value: bool | None = None):
        if value is not None:
            self.complex = value
        return self
    
    def set_timeout(self, timeout: int | None = None):
        if timeout is not None:
            self.timeout = timeout
        return self
    
    def set_target_list(self, target_list: list[str]):
        self.target_list = target_list
        return self

    def execute(self) -> int:
        if self.norun and not self.load_self:
            print("Nothing to do. If using --norun, you should choice at least --self.")
            return 1
        
        param = Param.Basic()
        param.set_diff_count(DiffCount.NONE)
        param.set_compact(True)

        settings = Settings()
        cmd_run = Run(settings, self.target_list, param)
        cmd_run.set_eval_mode().set_abort_on_exec_error()
        if self.norun:
            cmd_run.set_no_run()
        if self.track:
            cmd_run.show_track_info()
        if self.load_self:
            cmd_run.show_self_info()
        if self.complex:
            cmd_run.set_complex_percent()
        if self.timeout != 0:
            cmd_run.set_timeout(self.timeout)
        cmd_run.execute()

        return 0    