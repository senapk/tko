from __future__ import annotations
import enum
import hashlib
from abc import ABC, abstractmethod


class LogType(enum.Enum):
    NONE = 'NONE'
    OPEN = 'OPEN' # Open program
    QUIT = 'QUIT' # Quit program
    DOWN = 'DOWN' # Down problem
    FREE = 'FREE' # Free Compile and RUN
    FAIL = 'FAIL' # Compile error or Execution error
    TEST = 'TEST' # run test and Coverage %
    SELF = 'SELF' # {cov:{coverage}, app:{approach}, aut:{autonomy}} after added {clear:%d, fun:%d, easy:%d}
    PICK = 'PICK' # Enter problem
    BACK = 'BACK' # Leave problem
    PROG = 'PROG' # deprecated
    SIZE = 'SIZE' # Problem files changes "{line_count:%d}"

class LogTypeAction(enum.Enum):
    EXEC = 'EXEC'  # Execution Free or With tests
    SELF = 'SELF'  # Self evaluation
    MOVE = 'MOVE'  # Interaction with tasks without execution 
    GAME = 'GAME'  # Game changes or setup

class LogItemTemplate(ABC):
    def __init__(self, type: LogTypeAction):
        self.hash = ""
        self.timestamp = ""
        self.type: LogTypeAction = type

    def set_hash(self, hash: str):
        self.hash = hash
        return self
    
    def get_hash(self):
        return self.hash
    
    def set_timestamp(self, timestamp: str):
        self.timestamp = timestamp
        return self

    def get_timestamp(self) -> str:
        return self.timestamp
    
    def get_log_type(self) -> LogTypeAction:
        return self.type

    def __str__(self) -> str:
        return self.encode_line()
    
    @abstractmethod
    def get_key(self) -> str:
        pass
    
    @abstractmethod
    def decode_line(self, parts: list[str]) -> bool:
        """
        Decode a line from the log file into the log item.
        Returns True if successful, False otherwise.
        """
        pass

    @abstractmethod
    def encode_line(self) -> str:
        pass


class LogMoveAction(enum.Enum):
    NONE = "NONE"
    DOWN = "DOWN"
    ENTER = "ENTER"
    LEAVE = "LEAVE"
    EDIT = "EDIT"

class LogMoveItem(LogItemTemplate):
    def __init__(self):
        super().__init__(LogTypeAction.MOVE)
        self.task_key = ""
        self.action: LogMoveAction = LogMoveAction.NONE

    def set_task_key(self, task: str):
        self.task_key = task
        return self

    def set_action(self, action: LogMoveAction):
        self.action = action
        return self
    
    def encode_line(self) -> str:
        return f'{self.timestamp}, {self.type.value}, key:{self.task_key}, act:{self.action.value}'

    def decode_line(self, parts: list[str]) -> bool:
        self.timestamp = parts[0]
        self.type = LogTypeAction(parts[1])
        if self.type != LogTypeAction.MOVE:
            return False
        for part in parts[2:]:
            if part.startswith("key:"):
                self.task_key = part.split(":")[1]
            elif part.startswith("act:"):
                self.action = LogMoveAction(part.split(":")[1])
        if self.task_key == "":
            return False
        return True


class LogExecError(enum.Enum):
    NONE = "NONE"
    COMP = "COMP"
    EXEC = "EXEC"

class LogExecItem(LogItemTemplate):
    def __init__(self):
        self.key = ""
        self.cov: int = -1 # percentage of coverage, value from 0 to 100
        self.len: int = -1
        self.err: LogExecError = LogExecError.NONE

    def set_key(self, key: str):
        self.key = key
        return self

    def set_cov(self, cov: int):
        self.cov = cov
        return self
    
    def set_len(self, lines: int):
        self.len = lines
        return self

    def set_err(self, err: LogExecError):
        self.err = err
        return self

    def get_key(self) -> str:
        return self.key

    def decode_line(self, parts: list[str]) -> bool:
        self.timestamp = parts[0]
        self.type = LogTypeAction(parts[1])
        if self.type != LogTypeAction.EXEC:
            return False
        for part in parts[2:]:
            if part.startswith("key:"):
                self.key = part.split(":")[1]
            elif part.startswith("cov:"):
                self.cov = int(part.split(":")[1])
            elif part.startswith("len:"):
                self.len = int(part.split(":")[1])
            elif part.startswith("err:"):
                self.err = LogExecError(part.split(":")[1])
        if self.key == "":
            return False
        if self.cov == -1 and self.len == -1 and self.err == LogExecError.NONE:
            return False
        return True

    def encode_line(self) -> str:
        output = f'{self.timestamp}, {self.type.value}, key:{self.key}'
        if self.cov >= 0:
            output += f', cov:{self.cov}'
        if self.len >= 0:
            output += f', len:{self.len}'
        if self.err != LogExecError.NONE:
            output += f', err:{self.err.value}'
        return output

class LogSelfItem(LogItemTemplate):
    def __init__(self):
        self.cov: int = -1
        self.app: int = -1
        self.aut: int = -1
        self.clear: int = -1
        self.fun: int = -1
        self.easy: int = -1