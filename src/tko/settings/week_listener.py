import yaml # type: ignore
from tko.logger.log_item_base import LogItemBase
from tko.logger.log_sort import LogSort
from tko.logger.delta import Delta
        
class WeekData:
    def __init__(self, week_day: str = "", elapsed: int = 0):
        self.week_day = week_day
        self.elapsed = elapsed

class WeekListener:
    def __init__(self):
        self.day_actions: dict[str, LogSort] = {}
        self.log_file: str | None = None
        self.format = '%Y-%m-%d %H:%M:%S'

    def handle_entry_incoming(self, item: LogItemBase, new_entry: bool = False):
        _ = new_entry
        day = item.timestamp.split(" ")[0]

        if day not in self.day_actions:
            self.day_actions[day] = LogSort()
        mode = Delta.Mode(Delta.Mode.Action.with_time_threshold, minutes_limit=60)
        self.day_actions[day].add_item(mode, item)

    def resume(self):
        days = sorted(self.day_actions.keys())
        if days:
            day = days[0]
            last = days[-1]
            while True:
                if day == last:
                    break
                if day not in self.day_actions:
                    self.day_actions[day] = LogSort()
                day = Delta.next_day(day)

        output: dict[str, WeekData] = {}
        for day in self.day_actions:
            week_day = Delta.week_day(day)
            base_list = self.day_actions[day].base_list
            if base_list:
                delta, _ = base_list[-1]
                elapsed = delta.accumulated.total_seconds() // 60
            else:
                elapsed = 0
            output[day] = WeekData(week_day=week_day, elapsed=int(elapsed))
        return output
    
    def save_yaml(self):
        if self.log_file is None:
            return
        with open(self.log_file, 'w') as file:
            yaml.dump(self.day_actions, file)
