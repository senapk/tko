import yaml # type: ignore
from tko.logger.log_item_base import LogItemBase
from tko.logger.log_sort import LogSort
from tko.logger.delta import Delta
        
class WeekData:
    def __init__(self, week_day: str = "", elapsed_seconds: int = 0):
        self.week_day = week_day
        self.elapsed_seconds = elapsed_seconds

class WeekListener:
    def __init__(self):
        self.day_actions: dict[str, LogSort] = {}
        self.log_file: str | None = None

    def handle_entry_incoming(self, item: LogItemBase, new_entry: bool = False):
        _ = new_entry
        day = item.datetime.strftime('%Y-%m-%d')

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
        for day, log_sort in self.day_actions.items():
            week_day = Delta.week_day(day)
            base_list = log_sort.base_list
            if base_list:
                delta, _ = base_list[-1]
                elapsed = int(delta.accumulated.total_seconds())
            else:
                elapsed = 0
            output[day] = WeekData(week_day=week_day, elapsed_seconds=elapsed)
        return output
    
    def save_yaml(self):
        if self.log_file is None:
            return
        with open(self.log_file, 'w') as file:
            yaml.dump(self.day_actions, file)
