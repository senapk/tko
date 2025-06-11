from tko.logger.log_enum_error import LogEnumError
from tko.logger.log_item_base import LogItemBase
from tko.logger.log_enum_item import LogEnumItem


class LogItemExec(LogItemBase):
    def __init__(self):
        super().__init__(LogEnumItem.EXEC)
        self.cov: int = -1 # percentage of coverage, value from 0 to 100
        self.len: int = -1
        self.err: LogEnumError = LogEnumError.NONE

    def set_cov(self, cov: int):
        self.cov = cov
        return self

    def set_len(self, lines: int):
        self.len = lines
        return self

    def set_err(self, err: LogEnumError):
        self.err = err
        return self
    
    def get_cov(self) -> int:
        return self.cov
    
    def get_len(self) -> int:
        return self.len
    
    def get_err(self) -> LogEnumError:
        return self.err

    def decode_line(self, parts: list[str]) -> bool:
        self.timestamp = parts[0]
        self.type = LogEnumItem(parts[1])
        if self.type != LogEnumItem.EXEC:
            return False
        for part in parts[2:]:
            if part.startswith("key:"):
                self.key = part.split(":")[1]
            elif part.startswith("cov:"):
                self.cov = int(part.split(":")[1])
            elif part.startswith("len:"):
                self.len = int(part.split(":")[1])
            elif part.startswith("err:"):
                self.err = LogEnumError(part.split(":")[1])
        if self.key == "":
            return False
        if self.cov == -1 and self.len == -1 and self.err == LogEnumError.NONE:
            return False
        return True

    def encode_line(self) -> str:
        output = f'{self.timestamp}, {self.type.value}, key:{self.key}'
        if self.cov >= 0:
            output += f', cov:{self.cov}'
        if self.len >= 0:
            output += f', len:{self.len}'
        if self.err != LogEnumError.NONE:
            output += f', err:{self.err.value}'
        return output