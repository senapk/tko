from tko.logger.log_item_base import LogItemBase
from tko.logger.log_sort import LogSort
from tko.logger.delta import Delta

class TaskListener:
    def __init__(self):
        self.minutes_limit: int = 60
        self.item_time: list[tuple[Delta, LogItemBase]] = []
        self.task_dict: dict[str, LogSort] = {}
        self.last_key: str = ""

    def listener(self, item: LogItemBase, new_entry: bool = False):
        without_inc_time = Delta.Mode(Delta.Mode.Action.without_inc_time)
        LogSort.add_to_list(without_inc_time, self.item_time, item)
        cumulative = True
        delta, _ = self.item_time[-1]
        if delta.elapsed.total_seconds() / 60 > self.minutes_limit:
            cumulative = False
        
        new_key = item.get_name()
        old_key = self.last_key
        if new_key != "" and old_key != "" and new_key != old_key:
            cumulative = False
                  
        if new_key != "":
            self.last_key = new_key

        if new_key not in self.task_dict:
            self.task_dict[new_key] = LogSort()
        if cumulative:
            self.task_dict[new_key].add_item(
                Delta.Mode(Delta.Mode.Action.incrementing_time), item
            )
        else:
            self.task_dict[new_key].add_item(
                Delta.Mode(Delta.Mode.Action.without_inc_time), item
            )
