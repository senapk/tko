from __future__ import annotations
from tko.logger.log_item_base import LogItemBase, LogItemBaseType

import enum

class LogItemMoveMode(enum.Enum):
    NONE = "NONE"
    DOWN = "DOWN"
    PICK = "PICK"
    BACK = "BACK"
    EDIT = "EDIT"

class LogItemMove(LogItemBase):

    mode_str = "mode"
    def __init__(self):
        super().__init__(LogItemBaseType.MOVE)
        self.mode: LogItemMoveMode = LogItemMoveMode.NONE

    def set_mode(self, action: LogItemMoveMode):
        self.mode = action
        return self

    def encode_line(self) -> str:
        return f'{super().encode_line()}, {self.mode_str}:{self.mode.value}'

    def identify_kv(self, kv: dict[str, str]) -> bool:
        if self.mode_str in kv:
            self.mode = LogItemMoveMode(kv[self.mode_str])
        if self.mode == LogItemMoveMode.NONE:
            return False
        return True
