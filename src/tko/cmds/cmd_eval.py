from tko.cmds.cmd_run import Run
from tko.util.param import Param
from tko.settings.settings import Settings
from tko.enums.diff_count import DiffCount
from tko.util.text import Text
from tko.util.symbols import symbols

class CmdEval:
    EVAL_TIMEOUT_DEFAULT = 30
    
    def __init__(self):
        self.target_list: list[str] = []
        self.no_run: bool = False
        self.track: bool = False
        self.load_self: bool = False
        self.complex: bool = False
        self.timeout: int = CmdEval.EVAL_TIMEOUT_DEFAULT
        self.result_file: str | None = None
        self.diff = DiffCount.FIRST

        symbols.execution_result["untested"] = Text.Token("U", "")
        symbols.execution_result["success"] = Text.Token("S", "g")
        symbols.execution_result["wrong_output"] = Text.Token("W", "r")
        symbols.execution_result["compilation_error"] = Text.Token("C", "m")
        symbols.execution_result["execution_error"] = Text.Token("E", "y")

    def set_diff(self, diff: DiffCount):
        self.diff = diff
        return self

    def set_no_run(self, value: bool | None = None):
        if value is not None:
            self.no_run = value
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
        else:
            self.timeout = CmdEval.EVAL_TIMEOUT_DEFAULT
        return self

    def set_result_file(self, result_file: str | None = None):
        self.result_file = result_file
        return self
    
    def set_target_list(self, target_list: list[str]):
        self.target_list = target_list
        return self

    def execute(self) -> None:
        if self.no_run and not self.load_self:
            print("Nothing to do. If using --norun, you should choice at least --self.")
            return
        
        param = Param.Basic()
        param.set_diff_count(self.diff)
        param.set_compact(True)

        settings = Settings()
        cmd_run = Run(settings, self.target_list, param)
        cmd_run.set_eval_mode().set_abort_on_exec_error()
        if self.no_run:
            cmd_run.set_no_run()
        if self.track:
            cmd_run.show_track_info()
        if self.load_self:
            cmd_run.show_self_info()
        if self.complex:
            cmd_run.set_complex_percent()
        if self.timeout != 0:
            cmd_run.set_timeout(self.timeout)
        percent = cmd_run.execute()

        if self.result_file:
            with open(self.result_file, 'w') as f:
                f.write(f"{percent}%\n")