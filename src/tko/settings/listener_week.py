import yaml # type: ignore
from tko.settings.log_action import LogAction
from tko.settings.task_basic import TaskBasic
from tko.settings.log_info import LogInfo
import datetime
        
class WeekData:
    def __init__(self, weed_day: str = "", elapsed: int = 0):
        self.weed_day = weed_day
        self.elapsed = elapsed

class WeekListener:
    def __init__(self):
        self.day_actions: dict[str, list[LogInfo]] = {}
        self.log_file: str | None = None
        self.format = '%Y-%m-%d %H:%M:%S'
        self.max_minutes = 60

    def listener(self, action: LogAction, new_entry: bool = False):
        decoder = LogInfo().decode(action)
        day = decoder.timestamp.split(" ")[0]

        if day not in self.day_actions:
            self.day_actions[day] = [decoder]
        else:
            last_action = self.day_actions[day][-1]
            decoder.calc_and_set_elapsed(last_action, self.max_minutes, self.format)
            self.day_actions[day].append(decoder)

    def set_task_file(self, value: str):
        self.log_file = value
        return self

    @staticmethod
    def next_day(day: str) -> str:
        date = datetime.datetime.strptime(day, '%Y-%m-%d')
        return (date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    @staticmethod
    def week_day(day: str) -> str:
        date = datetime.datetime.strptime(day, '%Y-%m-%d')
        return date.strftime('%A')

    def resume(self):
        days = sorted(self.day_actions.keys())
        day = days[0]
        last = days[-1]
        while True:
            if day == last:
                break
            if day not in self.day_actions:
                self.day_actions[day] = []
            day = self.next_day(day)

        output: dict[str, WeekData] = {}
        for key in sorted(self.day_actions.keys()):
            entries = self.day_actions[key]
            elapsed = 0 if len(entries) == 0 else entries[-1].get_minutes()
            output[key] = WeekData(weed_day=self.week_day(key), elapsed=elapsed)
        return output
    
    def save_yaml(self):
        if self.log_file is None:
            return
        with open(self.log_file, 'w') as file:
            yaml.dump(self.day_actions, file)
