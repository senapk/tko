from __future__ import annotations
from tko.logger.log_item_base import LogItemBase

import enum

class LogItemExec(LogItemBase):
    class Fail(enum.Enum):
        NONE = "NONE"
        COMP = "COMP"
        EXEC = "EXEC"

    class Mode(enum.Enum):
        NONE = "NONE" # no execution
        FULL = "FULL" # run all test cases
        LOCK = "LOCK" # run just one test case  
        FREE = "FREE" # run without test cases

    mode_str = "mode"
    rate_str = "rate"
    size_str = "size"
    fail_str = "fail"
    def __init__(self):
        super().__init__(LogItemBase.Type.EXEC)
        self.mode: LogItemExec.Mode = LogItemExec.Mode.NONE # NONE, FULL, LOCK, FREE
        self.rate: int = -1 # percentage of coverage, value from 0 to 100
        self.size: int = -1 # lines
        self.fail: LogItemExec.Fail = LogItemExec.Fail.NONE

    def set_mode(self, mode: LogItemExec.Mode):
        self.mode = mode
        return self

    def set_rate(self, cov: int):
        self.rate = cov
        return self

    def set_size(self, changes: bool, lines: int):
        if changes:
            self.size = lines
        return self

    def set_fail(self, err: LogItemExec.Fail):
        self.fail = err
        return self

    def get_rate(self) -> int:
        return self.rate

    def get_size(self) -> int:
        return self.size

    def get_fail(self) -> LogItemExec.Fail:
        return self.fail

    def identify_kv(self, kv: dict[str, str]) -> bool:
        if self.rate_str in kv:
            self.rate = int(kv[self.rate_str])
        if self.size_str in kv:
            self.size = int(kv[self.size_str])
        if self.mode_str in kv:
            self.mode = LogItemExec.Mode(kv[self.mode_str])
        if self.fail_str in kv:
            self.fail = LogItemExec.Fail(kv[self.fail_str])
        
        if self.key == "":
            return False
        return True

    def encode_line(self) -> str:
        output = super().encode_line()
        if self.mode != LogItemExec.Mode.NONE:
            output += f', {self.mode_str}:{self.mode.value}'
        if self.rate >= 0:
            output += f', {self.rate_str}:{self.rate}'
        if self.size >= 0:
            output += f', {self.size_str}:{self.size}'
        if self.fail != LogItemExec.Fail.NONE:
            output += f', {self.fail_str}:{self.fail.value}'
        return output
    
