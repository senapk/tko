from tko.collect.task_user_data import TaskUserData
from tko.logger.log_item_base import LogItemBase
from tko.logger.log_sort import LogSort
from tko.logger.delta import DeltaMode, DeltaAction
from tko.logger.delta_list import DeltaList
from tko.game.game import Game
import datetime as dt
import sys # type: ignore

class TaskListener:
    def __init__(self):
        self.minutes_limit: int = 30
        self.delta_list: DeltaList = DeltaList()
        self.task_dict: dict[str, LogSort] = {}
        self.task_history: list[LogSort] = []
        self.last_key: str = ""

    def handle_log_entry(self, item: LogItemBase, new_entry: bool = False):
        _ = new_entry
        without_inc_time = DeltaMode(DeltaAction.without_inc_time)
        self.delta_list.add_item(without_inc_time, item)
        self._add_to_task_dict(item)
        self._add_to_task_history(item)

    def _add_to_task_history(self, item: LogItemBase):
        key = item.key
        mode = DeltaMode(DeltaAction.with_time_threshold)

        last = self.task_history[-1] if self.task_history else None
        if last and last.key == key and last.is_continuous_action(mode, item):
            last.add_item(mode, item)
        else:
            log_sort = LogSort()
            log_sort.add_item(mode, item)
            self.task_history.append(log_sort)

    def mount_task_history(self, game: Game) -> list[TaskUserData]:
        history_log_sort: list[LogSort] = self.task_history
        history_data: list[TaskUserData] = []
        for log_sort in history_log_sort:
            key = log_sort.key
            if key is None:
                continue
            taskuserdata = TaskUserData().setup(log_sort, game.get_task(key))
            if taskuserdata.resume.duration > dt.timedelta(seconds=60):
                history_data.append(taskuserdata)
        return history_data
    

    def _add_to_task_dict(self, item: LogItemBase):
        cumulative = True
        delta, _ = self.delta_list.base_list[-1]
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
