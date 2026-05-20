import re

from tko.game.task_config import TaskLoss, TaskEval
from tko.game.task_resource import ResourceType

class TaskMatcher:
    PATTERN = r'^- \[ \](.*?)\[(.*?)\]\(([^()]*)\)(.*)$'
    ALLOWED = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-+"

    def __init__(self):
        self.raw_pre: str = ""
        self.raw_pos: str = ""
        self.title: str = ""
        self.link: str = ""

        self.key: str | None = None

        self.resource_type = ResourceType.NULL
        self.loss = TaskLoss.NULL
        self.xp = 1
        self.tier = 1
        self.test = TaskEval.NULL

    def match_pattern(self, line: str) -> bool:
        match = re.match(self.PATTERN, line)

        if match is None:
            return False

        self.raw_pre = match.group(1)
        self.title = match.group(2)
        self.link = match.group(3)
        self.raw_pos = match.group(4)
        self.__parse_key()
        self.__decode_task_types()
        return True
    
    def filter_tags(self, text: str) -> str:
        return text.replace("`", " ").replace("<!--", " ").replace("-->", " ")

    def __parse_key(self):
        text = self.filter_tags(self.raw_pre + " " + self.raw_pos + " " + self.title)
        words = [w for w in text.split()]
        for item in words:
            if item.startswith("@"):
                self.key = TaskMatcher.__filter_task_key(item)
                break
            if item.startswith("key="):
                self.key = TaskMatcher.__filter_task_key(item[4:])
                break

    @staticmethod
    def parse_int(value: str) -> int | None:
        try:
            return int(value)
        except ValueError:
            return None

    @staticmethod
    def is_field(v: str) -> bool:
        return (
            v.startswith("@") or v.startswith(":") or 
            v.startswith("key=") or v.startswith("xp=") or v.startswith("tier=") or 
            v.startswith("loss=") or v.startswith("type=") or v.startswith("=eval")
        )

    def __parse_key_values(self, words: list[str]):
        for item in words:
            if item.startswith("tier="):
                tier_value = self.parse_int(item[5:])
                if tier_value is not None:
                    self.tier = tier_value
                break
            if item.startswith("xp="):
                xp_value = self.parse_int(item[3:])
                if xp_value is not None:
                    self.xp = xp_value
                break
            elif item == "eval=test":
                self.test = TaskEval.TEST
            elif item == "eval=self":
                self.test = TaskEval.SELF
            elif item == "loss=free":
                self.loss = TaskLoss.FREE
            elif item == "loss=part":
                self.loss = TaskLoss.PART
            elif item == "loss=zero":
                self.loss = TaskLoss.ZERO
            elif item == "type=task":
                self.resource_type = ResourceType.TASK
            elif item == "type=read":
                self.resource_type = ResourceType.READ

    def __parse_legacy_symbols(self, items: list[str]):
        for tag in items:
            # if c is digit, set xp
            if tag.isdigit():
                self.xp = int(tag)
            elif tag == TaskEval.TEST.value:
                self.test = TaskEval.TEST
            elif tag == TaskEval.SELF.value:
                self.test = TaskEval.SELF
            elif tag == ResourceType.TASK.value:
                self.resource_type = ResourceType.TASK
            elif tag == ResourceType.READ.value:
                self.resource_type = ResourceType.READ
            elif tag == TaskLoss.FREE.value:
                self.loss = TaskLoss.FREE
            elif tag == TaskLoss.PART.value:
                self.loss = TaskLoss.PART
            elif tag == TaskLoss.ZERO.value:
                self.loss = TaskLoss.ZERO

    def __set_default_values(self):
        if self.resource_type == ResourceType.NULL:
            self.resource_type = ResourceType.TASK

        if self.resource_type == ResourceType.READ:
            if self.loss == TaskLoss.NULL:
                self.loss = TaskLoss.FREE
            if self.test == TaskEval.NULL:
                self.test = TaskEval.SELF
        else:
            if self.loss == TaskLoss.NULL:
                self.loss = TaskLoss.PART
            if self.test == TaskEval.NULL:
                self.test = TaskEval.TEST


    def __decode_task_types(self):
        text = self.filter_tags(self.raw_pre + " " + self.title)
        words = [w for w in text.split()]
        self.__parse_key_values(words)

        text = text.replace(":", " :")
        items = [w[1:].strip() for w in text.split() if w[0] == ':']
        self.__parse_legacy_symbols(items)

        self.__set_default_values()

    @staticmethod
    def __filter_task_key(key: str) -> str | None:
        # Remove leading @ and filter remaining characters
        if not key.startswith("@"):
            return None
        key = key[1:]
        new_key = ""
        for c in key:
            if c in TaskMatcher.ALLOWED:
                new_key += c
            else:
                break
        return new_key if new_key else None
