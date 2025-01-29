from __future__ import annotations
from tko.settings.log_action import LogAction
from tko.game.task import Task
import datetime

class LogInfo:
    def __init__(self):
        self.timestamp = ""
        self.type: str = LogAction.Type.NONE.value
        self.key = ""
        self.coverage: int = -1
        self.autonomy: int = -1
        self.skill: int = -1
        self.elapsed: datetime.timedelta = datetime.timedelta(0)
        self.attempts: int = 0

    def get_minutes(self) -> int:
        return int(self.elapsed.total_seconds() / 60)

    def set_timestamp(self, value: str):
        self.timestamp = value
        return self

    def set_type(self, value: str):
        self.type = value
        return self
    
    def set_key(self, value: str):
        self.key = value
        return self
    
    def set_attempts(self, value: int):
        self.attempts = value
        return self
    
    def set_coverage(self, value: int):
        self.coverage = value
        return self
    
    def set_autonomy(self, value: int):
        self.autonomy = value
        return self
    
    def set_skill(self, value: int):
        self.skill = value
        return self
    
    def set_elapsed(self, value: datetime.timedelta):
        self.elapsed = value
        return self
    
    def calc_and_set_elapsed(self, last: LogInfo, limit_minutes: int, format: str):
        last_time = datetime.datetime.strptime(last.timestamp, format)
        current_time = datetime.datetime.strptime(self.timestamp, format)
        diff = current_time - last_time
        if diff.total_seconds() < limit_minutes * 60:
            elapsed = last.elapsed + diff
        else:
            elapsed = last.elapsed
        self.elapsed = elapsed
        return self
        
    def to_dict(self) -> dict[str, str]:
        return {
            "type": self.type,
            "key": self.key,
            "coverage": str(self.coverage),
            "autonomy": str(self.autonomy),
            "skill": str(self.skill),
            "elapsed": str(int(self.elapsed.total_seconds() / 60)),
            "attempts": str(self.attempts)
        }

    def __str__(self) -> str:
        output = "{" + f'time:{self.timestamp}, type:{self.type}, key:{self.key}'
        if self.coverage != -1:
            output += f', c:{self.coverage}'
        if self.autonomy != -1:
            output += f', a:{self.autonomy}'
        if self.skill != -1:
            output += f', s:{self.skill}'
        if self.elapsed.total_seconds() > 0:
            minutes = int(self.elapsed.total_seconds() / 60)
            output += f', e:{minutes}'
        return output + "}"
    
    def decode(self, action: LogAction):
        self.timestamp = action.timestamp
        self.type = action.type_value
        self.key = action.task_key
        if action.type_value == LogAction.Type.TEST.value:
            self.load_from_test(action.payload)
        elif action.type_value == LogAction.Type.PROG.value:
            self.load_from_prog(action.payload)
        elif action.type_value == LogAction.Type.SELF.value:
            self.load_from_self(action.payload)

        return self

    def load_from_test(self, payload: str):
        try:
            self.coverage = int(payload)
        except:
            pass
    
    def load_from_prog(self, payload: str):
        self.coverage = int(payload)
        return
    
    def load_from_self(self, payload: str):
        if len(payload) == 1:
            self.autonomy, self.skill = Task.decode_autonomy_skill(int(payload))
            return
    
        if len(payload) == 2:
            self.autonomy = int(payload[0])
            self.skill = int(payload[1])
            return
        
        if len(payload) == 3 and payload[0] == "0":
            self.autonomy = int(payload[1])
            self.skill = int(payload[2])
            return
        
        if payload[0] == "{":
            payload = payload[1:-1]
            values = payload.split(",")
            kv = {}
            for svalue in values:
                k, v = svalue.split(":")
                kv[k.strip()] = v.strip()
            self.coverage = int(kv.get("c", -1))
            self.autonomy = int(kv.get("a", -1))
            self.skill = int(kv.get("s", -1))
            return
        
        raise Exception(f"Invalid SELF payload: {payload}")
            
    