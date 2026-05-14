import re

class TaskMatcher:
    PATTERN = r'^- \[ \](.*?)\[(.*?)\]\(([^()]*)\)(.*)$'
    ALLOWED = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-+"

    def __init__(self):
        self.raw_pre: str = ""
        self.raw_pos: str = ""
        self.task_title: str = ""
        self.task_link: str = ""

        self.key: str | None = None
        self.is_view: bool = False

    def match_full_pattern(self, line: str) -> bool:
        match = re.match(self.PATTERN, line)

        if match is None:
            return False

        self.raw_pre = match.group(1)
        self.task_title = match.group(2)
        self.task_link = match.group(3)
        self.raw_pos = match.group(4)
        self.__parse_key_and_resource_type()
        return True
    
    def filter_tags(self, text: str) -> str:
        return text.replace("`", " ").replace("<!--", " ").replace("-->", " ")

    def __parse_key_and_resource_type(self):
        text = self.filter_tags(self.raw_pre + " " + self.raw_pos + " " + self.task_title)
        words = [w for w in text.split()]
        for item in words:
            if item.startswith("@"):
                self.key = TaskMatcher.__filter_task_key(item[1:])
                break
        if self.key is not None and self.key.startswith("+"):
            self.is_view = True
        else:
            self.is_view = False

    @staticmethod
    def __filter_task_key(key: str) -> str | None:
        new_key = ""
        for c in key:
            if c in TaskMatcher.ALLOWED:
                new_key += c
            else:
                break
        return new_key if new_key else None
