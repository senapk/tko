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
        self.approach: int = -1
        self.autonomy: int = -1
        self.howclear: int = -1
        self.howfun: int = -1
        self.howeasy: int = -1
        self.elapsed: datetime.timedelta = datetime.timedelta(0)
        self.attempts: int = 0
        self.lines: int = -1

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
        self.approach = value
        return self
    
    def set_skill(self, value: int):
        self.autonomy = value
        return self
    
    def set_elapsed(self, value: datetime.timedelta):
        self.elapsed = value
        return self

    def set_lines(self, value: int):
        self.lines = value
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
            "approach": str(self.approach),
            "autonomy": str(self.autonomy),
            "howclear": str(self.howclear),
            "howfun": str(self.howfun),
            "howeasy": str(self.howeasy),
            "elapsed": str(int(self.elapsed.total_seconds() / 60)),
            "attempts": str(self.attempts),
            "lines": str(self.lines)
        }

    def __str__(self) -> str:
        output = f'time:{self.timestamp}, type:{self.type}, key:{self.key}'
        if self.coverage != -1:
            output += f', c:{self.coverage}'
        if self.approach != -1:
            output += f', a:{self.approach}'
        if self.autonomy != -1:
            output += f', s:{self.autonomy}'
        if self.howclear != -1:
            output += f', clear:{self.howclear}'
        if self.howfun != -1:
            output += f', fun:{self.howfun}'
        if self.howeasy != -1:
            output += f', easy:{self.howeasy}'
        if self.elapsed.total_seconds() > 0:
            minutes = int(self.elapsed.total_seconds() / 60)
            output += f', e:{minutes}'
        if self.attempts > 0:
            output += f', att:{self.attempts}'
        if self.lines != -1:
            output += f', lines:{self.lines}'
        return output
    
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
        elif action.type_value == LogAction.Type.SIZE.value:
            self.load_from_size(action.payload)
        return self

    def load_from_test(self, payload: str):
        try:
            self.coverage = int(payload)
        except:
            pass
    
    def load_from_prog(self, payload: str):
        self.coverage = int(payload)
        return
    
    def load_from_size(self, payload: str):
        self.lines = int(payload)
        return
    
    def load_from_self(self, payload: str):
        if len(payload) == 1:
            self.approach, self.autonomy = Task.decode_approach_autonomy(int(payload))
            return
    
        if len(payload) == 2:
            self.approach = int(payload[0])
            self.autonomy = int(payload[1])
            return
        
        if len(payload) == 3 and payload[0] == "0":
            self.approach = int(payload[1])
            self.autonomy = int(payload[2])
            return
        
        if payload[0] == "{":
            payload = payload[1:-1]
            values = payload.split(",")
            kv: dict[str, str] = {}
            for svalue in values:
                k, v = svalue.split(":")
                kv[k.strip()] = v.strip()
            self.coverage = int(kv.get("c", -1))
            self.approach = int(kv.get("a", -1))
            self.autonomy = int(kv.get("s", -1))
            self.howclear = int(kv.get("clear", -1))
            self.howfun = int(kv.get("fun", -1))
            self.howeasy = int(kv.get("easy", -1))
            return
        
        raise Exception(f"Invalid SELF payload: {payload}")
            
    