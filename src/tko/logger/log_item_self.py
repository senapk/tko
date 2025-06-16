from tko.logger.log_item_base import LogItemBase
from tko.game.task_info import TaskInfo
from tko.logger.kv import KV

class LogItemSelf(LogItemBase):
    def __init__(self):
        super().__init__(LogItemBase.Type.SELF)
        self.info: TaskInfo = TaskInfo()

    def set_info(self, info: TaskInfo):
        self.info = info
        return self
    
    def get_info(self) -> TaskInfo:
        return self.info

    def identify_kv(self, kv: dict[str, str]) -> bool:
        self.info.load_from_kv(kv)
        if self.type != LogItemBase.Type.SELF:
            return False
        return True

    def encode_line(self) -> str:
        output = super().encode_line()
        kv = self.info.get_filled_kv()
        if len(kv) > 0:
            output += ", " + KV.encode_kv(kv, ", ")
        return output
