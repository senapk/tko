import re

from tko.game.task_enums import TaskEval, TaskType

def remove_emojis(text: str) -> str:
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002700-\U000027BF"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )

    return emoji_pattern.sub('', text)

class TaskMatcher:
    TYPE = "type="
    GAIN = "gain="
    HARD = "hard="
    SIZE = "size="
    EVAL = "eval="


    PATTERN = r'(.*?)\[(.*?)\]\(([^()]*)\)(.*)$'
    REF_T = r'^- \[x\]' + PATTERN
    REF_F = r'^- \[ \]' + PATTERN
    ALLOWED = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-+/"

    def __init__(self):
        self.raw_line: str = ""
        self.raw_pre: str = ""
        self.raw_pos: str = ""
        self.title: str = ""
        self.link: str = ""
        self.is_ref: bool = False

        self.key: str | None = None

        self.resource_type = TaskType.NULL
        self.eval = TaskEval.SELF
        self._legacy_eval: TaskEval | None = None
        self._legacy_read = False
        self._explicit_type = False
        self.gain = 1
        self.hard = 1
        self.size = 1

    def match_pattern(self, line: str) -> bool:
        is_ref: bool = False
        match = re.match(TaskMatcher.REF_T, line)
        if match is not None:
            is_ref = True
        else:
            match = re.match(TaskMatcher.REF_F, line)
            if match is None:
                return False

        self.raw_line = line
        self.raw_pre = ""
        self.raw_pos = ""
        self.title = ""
        self.link = ""
        self.key = None
        self.resource_type = TaskType.NULL
        self.eval = TaskEval.SELF
        self._legacy_eval = None
        self._legacy_read = False
        self._explicit_type = False
        self.gain = 1
        self.hard = 1
        self.size = 1
        self.is_ref = is_ref
        self.raw_pre = remove_emojis(match.group(1))
        self.title = remove_emojis(match.group(2))
        self.link = match.group(3).replace("\\", "/")
        self.raw_pos = remove_emojis(match.group(4))
        self.__parse_key()

        text = self.filter_tags(self.raw_pre + " " + self.title + " " + self.raw_pos)
        words = [w for w in text.split()]
        self.__parse_fields(words)

        text = text.replace(":", " :")
        items = [w[1:].strip() for w in text.split() if w[0] == ':']
        self.__parse_fields_legacy(items)

        self.__set_default_values()
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

    @staticmethod
    def parse_int(value: str) -> int | None:
        try:
            return int(value)
        except ValueError:
            return None

    @staticmethod
    def is_field(v: str) -> bool:
        return ( v.startswith("@") or v.startswith(":") or ("=" in v and len(v.split("=")) == 2))

    def get_filled_fields(self) -> list[str]:
        output: list[str] = []
        if self.key is not None:
            output.append(f"@{self.key}")

        if self.resource_type != TaskType.NULL:
            output.append(f"{TaskMatcher.TYPE}{self.resource_type.value}")

        output.append(f"{TaskMatcher.GAIN}{self.gain}")
        output.append(f"{TaskMatcher.HARD}{self.hard}")
        output.append(f"{TaskMatcher.SIZE}{self.size}")

        return output

    def __parse_fields(self, words: list[str]):
        for item in words:
            item = item.lower()
            if item.startswith(TaskMatcher.HARD):
                if (hard_value := self.parse_int(item[len(TaskMatcher.HARD):])) is not None:
                    self.hard = hard_value
                continue
            if item.startswith("tier="):
                if (hard_value := self.parse_int(item[len("tier="):])) is not None:
                    self.hard = hard_value
                continue
            if item.startswith(TaskMatcher.GAIN):
                if (gain_value := self.parse_int(item[len(TaskMatcher.GAIN):])) is not None:
                    self.gain = gain_value
                continue
            if item.startswith("xp="):
                if (gain_value := self.parse_int(item[len("xp="):])) is not None:
                    self.gain = gain_value
                continue
            if item.startswith(TaskMatcher.SIZE):
                if (size_value := self.parse_int(item[len(TaskMatcher.SIZE):])) is not None:
                    self.size = size_value
                continue
            elif item == f"{TaskMatcher.TYPE}{TaskType.WIKI.value}" or item == f"{TaskMatcher.TYPE}read":
                self.resource_type = TaskType.WIKI
                self._legacy_read = item.endswith("read")
                self._explicit_type = True
            elif item == f"{TaskMatcher.TYPE}{TaskType.SELF.value}":
                self.resource_type = TaskType.SELF
                self._explicit_type = True
            elif item == f"{TaskMatcher.TYPE}{TaskType.DIFF.value}":
                self.resource_type = TaskType.DIFF
                self._explicit_type = True
            elif item == f"{TaskMatcher.TYPE}{TaskType.CODE.value}":
                self.resource_type = TaskType.CODE
                self._explicit_type = True
            elif item == f"{TaskMatcher.TYPE}{TaskType.MAKE.value}":
                self.resource_type = TaskType.MAKE
                self._explicit_type = True
            elif item == f"{TaskMatcher.EVAL}self":
                self._legacy_eval = TaskEval.SELF
            elif item in (f"{TaskMatcher.EVAL}test", f"{TaskMatcher.EVAL}diff"):
                self._legacy_eval = TaskEval.TEST

    def __parse_fields_legacy(self, items: list[str]):
        for tag in items:
            # if c is digit, set xp
            if tag.isdigit():
                self.gain = int(tag)
            elif tag == "test":
                self._legacy_eval = TaskEval.TEST
            elif tag == "diff":
                self.resource_type = TaskType.DIFF
            elif tag == "self":
                self._legacy_eval = TaskEval.SELF
            elif tag == TaskType.MAKE.value:
                self.resource_type = TaskType.MAKE
            elif tag in ("read", TaskType.WIKI.value):
                self.resource_type = TaskType.WIKI
                self._legacy_read = tag == "read"


    def __set_default_values(self):
        if self.resource_type == TaskType.NULL:
            raise ValueError("Task type is required: use type=wiki, type=self, type=diff or type=code")
        if self.resource_type == TaskType.MAKE:
            if self._legacy_eval == TaskEval.SELF:
                self.resource_type = TaskType.SELF
            elif self._legacy_eval == TaskEval.TEST:
                self.resource_type = TaskType.DIFF
            else:
                raise ValueError("type=make is obsolete; use type=self or type=diff")
        elif self._explicit_type and not self._legacy_read and self._legacy_eval is not None:
            raise ValueError("eval= is obsolete; use type=wiki, type=self, type=diff or type=code")
        if self.resource_type in (TaskType.SELF, TaskType.DIFF, TaskType.CODE):
            self.eval = {TaskType.SELF: TaskEval.SELF, TaskType.DIFF: TaskEval.TEST, TaskType.CODE: TaskEval.TEST}[self.resource_type]


    @property
    def is_read(self):
        return self.resource_type == TaskType.WIKI

    @property
    def is_wiki(self):
        return self.resource_type == TaskType.WIKI
    
    @property
    def is_make(self):
        return self.resource_type != TaskType.WIKI and self.resource_type != TaskType.NULL

    @property
    def is_url(self):
        return self.link.startswith("http://") or self.link.startswith("https://")

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

    @staticmethod
    def validate_key(key: str) -> None:
        if not key or key.startswith("/") or key.endswith("/") or "//" in key:
            raise ValueError(f"Invalid task key path: {key}")
        parts = key.split("/")
        if any(part in {"", ".", ".."} for part in parts):
            raise ValueError(f"Invalid task key path: {key}")
        if any("~" in part for part in parts):
            raise ValueError(f"Invalid character in task key: {key}")
