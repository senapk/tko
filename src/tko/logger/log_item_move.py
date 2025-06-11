from tko.logger.log_item_base import LogItemBase
from tko.logger.log_enum_move import LogEnumMove
from tko.logger.log_enum_item import LogEnumItem


class LogItemMove(LogItemBase):
    def __init__(self):
        super().__init__(LogEnumItem.MOVE)
        self.action: LogEnumMove = LogEnumMove.NONE

    def set_action(self, action: LogEnumMove):
        self.action = action
        return self

    def encode_line(self) -> str:
        return f'{self.timestamp}, {self.type.value}, key:{self.task_key}, act:{self.action.value}'

    def decode_line(self, parts: list[str]) -> bool:
        self.timestamp = parts[0]
        self.type = LogEnumItem(parts[1])
        if self.type != LogEnumItem.MOVE:
            return False
        for part in parts[2:]:
            if part.startswith("key:"):
                self.task_key = part.split(":")[1]
            elif part.startswith("act:"):
                self.action = LogEnumMove(part.split(":")[1])
        if self.task_key == "":
            return False
        return True