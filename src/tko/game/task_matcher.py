import re

from tko.game.task_config import TaskLoss, TaskMain, TaskTest
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

        self.resource_type = ResourceType.UNKNOWN
        self.loss = TaskLoss.NULL
        self.xp = 1
        self.test = TaskTest.NULL
        self.main = TaskMain.MAIN

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

    def __decode_task_types(self):
        text = self.filter_tags(self.raw_pre + " " + self.title)
        items = [w.strip() for w in re.split(r'[:\s]+', text)]

        for tag in items:
            # if c is digit, set xp
            if tag.isdigit():
                self.xp = int(tag)
            elif tag == TaskTest.TEST.value:
                self.test = TaskTest.TEST
            elif tag == TaskTest.SELF.value:
                self.test = TaskTest.SELF
            elif tag == ResourceType.DO.value:
                self.resource_type = ResourceType.DO
            elif tag == ResourceType.READ.value:
                self.resource_type = ResourceType.READ
            elif tag == TaskMain.MAIN.value:
                self.main = TaskMain.MAIN
            elif tag == TaskMain.SIDE.value:
                self.main = TaskMain.SIDE
            elif tag == TaskMain.PERK.value:
                self.main = TaskMain.PERK
            elif tag == TaskLoss.FREE.value:
                self.loss = TaskLoss.FREE
            elif tag == TaskLoss.PART.value:
                self.loss = TaskLoss.PART
            elif tag == TaskLoss.ZERO.value:
                self.loss = TaskLoss.ZERO
            # else:
            #     logger.warning(
            #         "Parsing %s:%s, Tipo de tarefa desconhecido: %s",
            #         self.index_path,
            #         self.task.resource.line_number,
            #         tag,
            #     )

        # setting default values
        if self.resource_type == ResourceType.UNKNOWN:
            self.resource_type = ResourceType.DO

        if self.resource_type == ResourceType.READ:
            if self.loss == TaskLoss.NULL:
                self.loss = TaskLoss.FREE
            if self.test == TaskTest.NULL:
                self.test = TaskTest.SELF
        else:
            if self.loss == TaskLoss.NULL:
                self.loss = TaskLoss.PART
            if self.test == TaskTest.NULL:
                self.test = TaskTest.TEST

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
