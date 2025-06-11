from tko.logger.log_enum_item import LogEnumItem


from abc import ABC, abstractmethod


class LogItemBase(ABC):
    def __init__(self, type: LogEnumItem):
        self.key = ""
        self.timestamp = ""
        self.type: LogEnumItem = type

    def set_key(self, key: str):
        self.key = key
        return self
    
    def get_key(self) -> str:
        return self.key

    def set_timestamp(self, timestamp: str):
        self.timestamp = timestamp
        return self

    def get_timestamp(self) -> str:
        return self.timestamp

    def get_log_type(self) -> LogEnumItem:
        return self.type

    def __str__(self) -> str:
        return self.encode_line()


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