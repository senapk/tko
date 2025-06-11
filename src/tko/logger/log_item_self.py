from tko.logger.log_item_base import LogItemBase
from tko.logger.log_enum_item import LogEnumItem


class LogItemSelf(LogItemBase):
    def __init__(self):
        super().__init__(LogEnumItem.SELF)
        self.cov: int = -1
        self.app: int = -1
        self.aut: int = -1
        self.neat: int = -1
        self.cool: int = -1
        self.easy: int = -1

    def set_cov(self, cov: int):
        self.cov = cov
        return self

    def set_app(self, app: int):
        self.app = app
        return self

    def set_aut(self, aut: int):
        self.aut = aut
        return self

    def set_neat(self, neat: int):
        self.neat = neat
        return self

    def set_cool(self, cool: int):
        self.cool = cool
        return self

    def set_easy(self, easy: int):
        self.easy = easy
        return self

    def decode_line(self, parts: list[str]) -> bool:
        self.timestamp = parts[0]
        self.type = LogEnumItem(parts[1])
        if self.type != LogEnumItem.SELF:
            return False
        for part in parts[2:]:
            if part.startswith("key:"):
                self.key = part.split(":")[1]
            elif part.startswith("cov:"):
                self.cov = int(part.split(":")[1])
            elif part.startswith("app:"):
                self.app = int(part.split(":")[1])
            elif part.startswith("aut:"):
                self.aut = int(part.split(":")[1])
            elif part.startswith("neat:"):
                self.neat = int(part.split(":")[1])
            elif part.startswith("cool:"):
                self.cool = int(part.split(":")[1])
            elif part.startswith("easy:"):
                self.easy = int(part.split(":")[1])
        if self.key == "":
            return False
        return True

    def encode_line(self) -> str:
        output = f'{self.timestamp}, {self.type.value}, key:{self.key}'
        if self.cov >= 0:
            output += f', cov:{self.cov}'
        if self.app >= 0:
            output += f', app:{self.app}'
        if self.aut >= 0:
            output += f', aut:{self.aut}'
        if self.neat >= 0:
            output += f', neat:{self.neat}'
        if self.cool >= 0:
            output += f', cool:{self.cool}'
        if self.easy >= 0:
            output += f', easy:{self.easy}'
        return output