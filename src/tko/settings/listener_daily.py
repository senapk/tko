import yaml # type: ignore
from tko.settings.task_basic import TaskBasic
from tko.settings.log_action import LogAction
from tko.settings.log_info import LogInfo

class DailyListener:
    def __init__(self):
        self.history: dict[str, dict[str, TaskBasic]] = {} # dict[day, dict[key, [key, cov, how]]]
        self.actual: dict[str, TaskBasic] = {}
        self.daily_file: str | None
        
    def listener(self, action: LogAction, new_entry: bool = False):
        decoder = LogInfo().decode(action)
        types = [LogAction.Type.TEST.value, LogAction.Type.PROG.value, LogAction.Type.SELF.value]
        if decoder.type in types:
            self.log_task(decoder.timestamp, decoder.key, decoder.coverage, decoder.autonomy, decoder.skill)

    def set_daily_file(self, daily_file: str):
        self.daily_file = daily_file
        return self

    def log_task(self, timestamp: str, key: str, coverage: int = -1, autonomy: int = -1, skill: int = -1):
        if key not in self.actual:
            self.actual[key] = TaskBasic(key)
        self.actual[key].set_coverage(coverage).set_autonomy(autonomy).set_skill(skill)

        day = timestamp.split(" ")[0]
        if day not in self.history:
            self.history[day] = {}
        if key not in self.history[day]:
            self.history[day][key] = self.actual[key]
        else:
            self.history[day][key].set_coverage(coverage).set_autonomy(autonomy).set_skill(skill)
        # self.save_yaml()

    def __str__(self) -> str:
        output: dict[str, dict[str, str]] = {}
        for day in sorted(self.history.keys()):
            output[day] = {}
            for key in self.history[day]:
                output[day][key] = str(self.history[day][key])
        return yaml.dump(output)
    
    def save_yaml(self):
        if self.daily_file is None:
            return
        with open(self.daily_file, 'w') as file:
            file.write(str(self))
