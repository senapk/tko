from tko.logger.log_item_base import LogItemBase
from tko.game.task_info import TaskSelfInfo
from tko.game.task import Task
from tko.logger.kv import KV

class LogItemSelf(LogItemBase):
    def __init__(self):
        super().__init__(LogItemBase.Type.SELF)
        self.info: TaskSelfInfo = TaskSelfInfo()

    def set_task(self, task: Task):
        self.key = task.basic.full_key
        self.info = task.info.clone()
        return self

    def set_info(self, info: TaskSelfInfo):
        self.info = info
        return self
    
    def get_info(self) -> TaskSelfInfo:
        return self.info

    def identify_kv(self, kv: dict[str, str]) -> bool:
        self.info.load_from_kv(kv)
        if self.type != LogItemBase.Type.SELF:
            return False
        return True

    def encode_line(self) -> str:
        output = super().encode_line()
        kv = self.info.get_kv()
        if len(kv) > 0:
            output += ", " + KV.encode_kv(kv, ", ")
        return output
