from __future__ import annotations
from abc import ABC, abstractmethod
import datetime as dt
from tko.logger.delta import Delta
import enum
from tko.logger.kv import KV

class LogItemBase(ABC):
    class Type(enum.Enum):
        EXEC = 'EXEC'  # Execution Free or With tests
        SELF = 'SELF'  # Self evaluation
        MOVE = 'MOVE'  # Interaction with tasks without execution 
        GAME = 'GAME'  # Game changes or setup

    key_str = "k"
    version_str = "v"
    def __init__(self, log_type: LogItemBase.Type):
        self.key = ""
        self.vers: int = 1
        self.datetime: dt.datetime = dt.datetime.fromordinal(1)
        self.timestamp: str = ""
        self.type: LogItemBase.Type = log_type

    def set_key(self, key: str):
        self.key = key
        return self
    
    def set_version(self, version: int):
        self.vers = version
        return self
    
    def get_version(self) -> int:
        return self.vers

    def get_key(self) -> str:
        return self.key

    def set_timestamp(self, str_timestamp: str, datetime: dt.datetime | None = None):
        self.timestamp = str_timestamp
        if datetime is not None:
            self.datetime = datetime
        else:
            self.datetime = Delta.decode_format(str_timestamp)
        return self

    def set_datetime(self, datetime: dt.datetime):
        self.datetime = datetime
        self.timestamp = Delta.encode_format(datetime)
        return self

    def get_timestamp(self) -> str:
        return self.timestamp

    def get_datetime(self) -> dt.datetime:
        return self.datetime

    def get_log_type(self) -> LogItemBase.Type:
        return self.type

    def __str__(self) -> str:
        return self.encode_line()

    @abstractmethod
    def identify_kv(self, kv: dict[str, str]) -> bool:
        """
        Identify key-value pairs in the dictionary and set the corresponding attributes.
        Returns True if successful, False otherwise.
        """
        pass

    def decode_line(self, parts: list[str]) -> bool:
        kv = KV.decode_args(parts[2:])
        self.set_timestamp(parts[0])
        self.type = LogItemBase.Type(parts[1])
        self.vers = int(kv.get(self.version_str, 1))
        self.key = kv.get(self.key_str, "")
        return self.identify_kv(kv)

    def encode_line(self) -> str:
        """
        Encode the log item into a line for the log file.
        Returns the encoded line as a string.
        """
        return f'{self.timestamp}, {self.type.value}, {self.version_str}:{self.vers}, {self.key_str}:{self.key}'