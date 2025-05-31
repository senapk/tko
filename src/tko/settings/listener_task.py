import yaml
import os
from tko.settings.log_action import LogAction
from tko.settings.log_info import LogInfo
import datetime
        
class TaskListener:
    TASK_CSV = "task_log.csv"
    def __init__(self):
        self.key_actions: dict[str, list[LogInfo]] = {}
        self.log_file: str | None = None
        self.format = '%Y-%m-%d %H:%M:%S'
        self.max_minutes = 60
        self.track_folder: str | None = None

    def set_track_folder(self, folder: str):
        self.track_folder = folder
        return self

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
                if diff.total_seconds() > 0:
                    elapsed = last_action.elapsed + diff
                else:
                    elapsed = last_action.elapsed
            else:
                elapsed = last_action.elapsed
            decoder.elapsed = elapsed
            if decoder.type == LogAction.Type.SIZE.value:
                decoder.attempts = last_action.attempts + 1
            else:
                decoder.attempts = last_action.attempts
                decoder.lines = last_action.lines
            
            self.key_actions[decoder.key].append(decoder)

        if self.track_folder is None:
            return
        if not new_entry:
            return
        task_track_folder = os.path.join(self.track_folder, decoder.key)
        os.makedirs(task_track_folder, exist_ok=True)
        log_file = os.path.join(task_track_folder, self.TASK_CSV)
        if os.path.exists(log_file):
            with open(log_file, 'a') as file:
                file.write(str(decoder) + '\n')
        else:
            with open(log_file, 'w') as file:
                for entry in self.key_actions[decoder.key]:
                    file.write(str(entry) + '\n')

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
                if action.approach != -1:
                    info.set_autonomy(action.approach)
                if action.autonomy != -1:
                    info.set_skill(action.autonomy)
            output[key] = info
        return output
    
    def save_yaml(self):
        if self.log_file is None:
            return
        with open(self.log_file, 'w') as file:
            yaml.dump(self.key_actions, file)
