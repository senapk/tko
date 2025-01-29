import yaml # type: ignore
from tko.util.decoder import Decoder
from tko.settings.log_action import LogAction
from tko.settings.task_basic import TaskBasic
from tko.settings.log_info import LogInfo
import datetime
        
class TaskListener:
    def __init__(self):
        self.key_actions: dict[str, list[LogInfo]] = {}
        self.log_file: str | None = None
        self.format = '%Y-%m-%d %H:%M:%S'
        self.max_minutes = 60

    def listener(self, action: LogAction, new_entry: bool = False):
        decoder = LogInfo().decode(action)
        if decoder.key == "":
            return
        if decoder.key not in self.key_actions:
            self.key_actions[decoder.key] = [decoder]
        else:
            last_action = self.key_actions[decoder.key][-1]
            last_time = datetime.datetime.strptime(last_action.timestamp, self.format)
            current_time = datetime.datetime.strptime(decoder.timestamp, self.format)
            diff = current_time - last_time
            if diff.total_seconds() < self.max_minutes * 60:
                elapsed = last_action.elapsed + diff
            else:
                elapsed = last_action.elapsed
            decoder.elapsed = elapsed
            self.key_actions[decoder.key].append(decoder)
        # self.save_yaml()

    def set_task_file(self, value: str):
        self.log_file = value
        return self
    
    def __str__(self) -> str: # yaml formatted output of key_actions
        output: dict[str, list[str]] = {}
        for key in sorted(self.key_actions.keys()):
            output[key] = []
            for action in self.key_actions[key]:
                output[key].append(str(action))
        return yaml.dump(output)

    def resume(self) -> dict[str, LogInfo]:
        output: dict[str, LogInfo] = {}
        for key in sorted(self.key_actions.keys()):
            entries = self.key_actions[key]
            info = LogInfo().set_key(key)
            info.set_elapsed(entries[-1].elapsed)
            info.set_attempts(len([x for x in entries if x.type == "TEST" or x.type == "FAIL"]))
            for action in entries:
                if action.coverage != -1:
                    info.set_coverage(action.coverage)
                if action.autonomy != -1:
                    info.set_autonomy(action.autonomy)
                if action.skill != -1:
                    info.set_skill(action.skill)
            output[key] = info
        return output
    
    def save_yaml(self):
        if self.log_file is None:
            return
        with open(self.log_file, 'w') as file:
            yaml.dump(self.key_actions, file)
