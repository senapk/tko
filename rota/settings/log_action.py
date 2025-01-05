from __future__ import annotations
import enum
import hashlib


class LogAction:
    class Type(enum.Enum):
        NONE = 'NONE'
        OPEN = 'OPEN' # Open program
        QUIT = 'QUIT' # Quit program
        DOWN = 'DOWN' # Down problem
        FREE = 'FREE' # Free Compile and RUN
        FAIL = 'FAIL' # Compile error or Execution error
        TEST = 'TEST' # run test and Coverage %
        SELF = 'SELF' # {c:{coverage}, a:{autonomy}, s:{skill}}
        PICK = 'PICK' # Enter problem
        BACK = 'BACK' # Leave problem
        PROG = 'PROG' # deprecated

    def __init__(self, action_value: str, task: str = "", payload: str = ""):
        self.hash = ""
        self.timestamp = ""
        self.type_value: str = action_value
        self.task_key = task
        self.payload = payload

    def set_hash(self, hash: str):
        self.hash = hash
        return self

    def set_timestamp(self, timestamp: str):
        self.timestamp = timestamp
        return self

    def __str__(self):
        return "{" + f'time:{self.timestamp}, type:{self.type_value}, key:{self.task_key}, payload:{self.payload}' + "}"

    @staticmethod
    def generate_hash(action_data: LogAction, last_hash: str):
        length = 6
        input_str = str(action_data) + last_hash
        full_hash = hashlib.sha256(input_str.encode()).hexdigest()
        return full_hash[:length]  # Retorna os primeiros 'comprimento' caracteres do hash