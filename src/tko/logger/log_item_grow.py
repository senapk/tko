from tko.logger.log_item_base import LogItemBase
from tko.logger.log_item_move import LogItemMove
from tko.logger.log_item_exec import LogItemExec
from tko.logger.log_item_self import LogItemSelf
import datetime


class LogItemGrow:
    def __init__(self):
        self.attempts: int = 0
        self.versions: int = 0
        self.laststamp: str = ""
        self.elapsed: datetime.timedelta = datetime.timedelta(0)
        self.move_list: list[LogItemMove] = []
        self.exec_list: list[LogItemExec] = []
        self.self_list: list[LogItemSelf] = []
        self.timeformat: str = '%Y-%m-%d %H:%M:%S'
        self.minutes_limit: int = 60

    def add_elapsed(self, timestamp: str):
        last_time = datetime.datetime.strptime(self.laststamp, self.timeformat)
        current_time = datetime.datetime.strptime(timestamp, self.timeformat)
        diff = current_time - last_time
        if diff.total_seconds() < self.minutes_limit * 60:
            self.elapsed = self.elapsed + diff
        return self

    def add_item(self, item: LogItemBase):
        self.add_elapsed(item.timestamp)
        if isinstance(item, LogItemMove):
            self.move_list.append(item)
        elif isinstance(item, LogItemExec):
            self.attempts += 1
            if item.get_len() > 0:
                self.versions += 1
            self.exec_list.append(item)
        elif isinstance(item, LogItemSelf):
            self.self_list.append(item)
        else:
            raise ValueError("Unsupported log item type")
