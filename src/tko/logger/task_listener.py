from tko.logger.log_item_base import LogItemBase
from tko.logger.log_sort import LogSort
from tko.logger.delta import Delta, DeltaMode, DeltaAction
import sys # type: ignore

class TaskListener:
    def __init__(self):
        self.minutes_limit: int = 60
        self.time_item: list[tuple[Delta, LogItemBase]] = []
        self.task_dict: dict[str, LogSort] = {}
        self.last_key: str = ""

    def handle_log_entry(self, item: LogItemBase, new_entry: bool = False):
        _ = new_entry
        without_inc_time = DeltaMode(DeltaAction.without_inc_time)
        LogItemBase.add_to_list(without_inc_time, self.time_item, item)
        self.add_to_task(item)

    def add_to_task(self, item: LogItemBase):
        cumulative = True
        delta, _ = self.time_item[-1]
        if delta.elapsed.total_seconds() / 60 > self.minutes_limit:
            cumulative = False
        
        new_key = item.get_key()
        old_key = self.last_key
        if new_key != "" and old_key != "" and new_key != old_key:
            cumulative = False
                  
        if new_key != "":
            self.last_key = new_key

        if new_key not in self.task_dict:
            self.task_dict[new_key] = LogSort()
        
        if cumulative:
            mode = DeltaMode(DeltaAction.incrementing_time)
        else:
            mode = DeltaMode(DeltaAction.without_inc_time)
        self.task_dict[new_key].add_item(mode, item)
