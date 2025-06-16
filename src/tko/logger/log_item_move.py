from __future__ import annotations
from tko.logger.log_item_base import LogItemBase

import enum

class LogItemMove(LogItemBase):
    class Mode(enum.Enum):
        NONE = "NONE"
        DOWN = "DOWN"
        PICK = "PICK"
        BACK = "BACK"
        EDIT = "EDIT"

    mode_str = "mode"
    def __init__(self):
        super().__init__(LogItemBase.Type.MOVE)
        self.mode: LogItemMove.Mode = LogItemMove.Mode.NONE

    def set_mode(self, action: LogItemMove.Mode):
        self.mode = action
        return self

    def encode_line(self) -> str:
        return f'{super().encode_line()}, {self.mode_str}:{self.mode.value}'

    def identify_kv(self, kv: dict[str, str]) -> bool:
        if self.mode_str in kv:
            self.mode = LogItemMove.Mode(kv[self.mode_str])
        if self.mode == LogItemMove.Mode.NONE:
            return False
        return True
