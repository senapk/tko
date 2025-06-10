from __future__ import annotations
from tko.logger.log_action import LogAction
from tko.game.task import Task
import datetime

class LogInfo:
    def __init__(self):
        self.timestamp = ""
        self.type: str = LogAction.Type.NONE.value
        self.key = ""
        self.cov: int = -1
        self.app: int = -1
        self.aut: int = -1
        self.att: int = 0
        self.elapsed: datetime.timedelta = datetime.timedelta(0)
        self.len: int = -1
        self.clear: int = -1
        self.fun: int = -1
        self.easy: int = -1

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
        self.att = value
        return self
    
    def set_coverage(self, value: int):
        self.cov = value
        return self
    
    def set_approach(self, value: int):
        self.app = value
        return self
    
    def set_autonomy(self, value: int):
        self.aut = value
        return self
    
    def set_elapsed(self, value: datetime.timedelta):
        self.elapsed = value
        return self

    def set_lines(self, value: int):
        self.len = value
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
            "cov": str(self.cov),
            "app": str(self.app),
            "aut": str(self.aut),
            "clear": str(self.clear),
            "fun": str(self.fun),
            "easy": str(self.easy),
            "elapsed": str(int(self.elapsed.total_seconds() / 60)),
            "att": str(self.att),
            "len": str(self.len)
        }

    def __str__(self) -> str:
        output = f'time:{self.timestamp}, type:{self.type}, key:{self.key}'
        if self.cov != -1:
            output += f', cov:{self.cov}'
        if self.app != -1:
            output += f', app:{self.app}'
        if self.aut != -1:
            output += f', aut:{self.aut}'
        if self.clear != -1:
            output += f', clear:{self.clear}'
        if self.fun != -1:
            output += f', fun:{self.fun}'
        if self.easy != -1:
            output += f', easy:{self.easy}'
        if self.elapsed.total_seconds() > 0:
            minutes = int(self.elapsed.total_seconds() / 60)
            output += f', elapsed:{minutes}'
        if self.att > 0:
            output += f', att:{self.att}'
        if self.len != -1:
            output += f', len:{self.len}'
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
        elif action.type_value == LogAction.Type.FAIL.value:
            self.load_from_fail(action.payload)
        return self

    def load_from_fail(self, payload: str):
        if payload[0] == "{":
            payload = payload[1:-1]

    def load_from_test(self, payload: str):
        try:
            self.cov = int(payload)
        except:
            pass
    
    def load_from_prog(self, payload: str):
        self.cov = int(payload)
        return
    
    def load_from_size(self, payload: str):
        self.len = int(payload)
        return
    
    def load_from_self(self, payload: str):
        if len(payload) == 1:
            self.app, self.aut = Task.decode_approach_autonomy(int(payload))
            return
    
        if len(payload) == 2:
            self.app = int(payload[0])
            self.aut = int(payload[1])
            return
        
        if len(payload) == 3 and payload[0] == "0":
            self.app = int(payload[1])
            self.aut = int(payload[2])
            return
        
        if payload[0] == "{":
            payload = payload[1:-1]
            values = payload.split(",")
            kv: dict[str, str] = {}
            for svalue in values:
                k, v = svalue.split(":")
                kv[k.strip()] = v.strip()
            if "c" in kv:
                self.cov = int(kv["c"])
            if "a" in kv:
                self.app = int(kv["a"])
            if "s" in kv:
                self.aut = int(kv["s"])
            if "clear" in kv:
                self.clear = int(kv["clear"])
            if "fun" in kv:
                self.fun = int(kv["fun"])
            if "easy" in kv:
                self.easy = int(kv["easy"])
            if "cov" in kv:
                self.cov = int(kv["cov"])
            if "app" in kv:
                self.app = int(kv["app"])
            if "aut" in kv:
                self.aut = int(kv["aut"])
            return
        
        raise Exception(f"Invalid SELF payload: {payload}")
            
    