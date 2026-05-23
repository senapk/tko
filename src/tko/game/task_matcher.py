import re

from tko.game.task_enums import TaskEval
from tko.game.task_enums import TaskLoss
from tko.game.task_enums import TaskType

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
    TIER = "tier="
    XP = "xp="
    LOSS = "loss="
    EVAL = "eval="


    PATTERN = r'(.*?)\[(.*?)\]\(([^()]*)\)(.*)$'
    REF_T = r'^- \[x\]' + PATTERN
    REF_F = r'^- \[ \]' + PATTERN
    ALLOWED = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-+"

    def __init__(self):
        self.raw_line: str = ""
        self.raw_pre: str = ""
        self.raw_pos: str = ""
        self.title: str = ""
        self.link: str = ""
        self.is_ref: bool = False

        self.key: str | None = None

        self.resource_type = TaskType.NULL
        self.loss = TaskLoss.NULL
        self.xp = 1
        self.tier = 1
        self.test = TaskEval.NULL

    def match_pattern(self, line: str) -> bool:
        self.raw_line = line
        is_ref: bool = False
        match = re.match(TaskMatcher.REF_T, line)
        if match is not None:
            is_ref = True
        else:
            match = re.match(TaskMatcher.REF_F, line)
            if match is None:
                return False
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
            if item.startswith(TaskMatcher.TYPE):
                self.key = TaskMatcher.__filter_task_key(item[len(TaskMatcher.TYPE):])
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
            v.startswith(TaskMatcher.TYPE) or v.startswith(TaskMatcher.XP) or v.startswith(TaskMatcher.TIER) or 
            v.startswith(TaskMatcher.LOSS) or v.startswith(TaskMatcher.EVAL)
        )

    def get_filled_fields(self) -> list[str]:
        output: list[str] = []
        if self.key is not None:
            output.append(f"@{self.key}")
        
        if self.resource_type != TaskType.NULL:
            output.append(f"{TaskMatcher.TYPE}{self.resource_type.value}")

        output.append(f"{TaskMatcher.XP}{self.xp}")
        if self.is_make:
            output.append(f"{TaskMatcher.TIER}{self.tier}")
            output.append(f"{TaskMatcher.EVAL}{self.test.value}")
            output.append(f"{TaskMatcher.LOSS}{self.loss.value}")

        return output

    def __parse_fields(self, words: list[str]):
        for item in words:
            item = item.lower()
            if item.startswith(TaskMatcher.TIER):
                tier_value = self.parse_int(item[len(TaskMatcher.TIER):])
                if tier_value is not None:
                    self.tier = tier_value
                continue
            if item.startswith(TaskMatcher.XP):
                xp_value = self.parse_int(item[len(TaskMatcher.XP):])
                if xp_value is not None:
                    self.xp = xp_value
                continue
            elif item == f"{TaskMatcher.EVAL}{TaskEval.TEST.value}":
                self.test = TaskEval.TEST
            elif item == f"{TaskMatcher.EVAL}{TaskEval.SELF.value}":
                self.test = TaskEval.SELF
            elif item == f"{TaskMatcher.LOSS}{TaskLoss.FREE.value}":
                self.loss = TaskLoss.FREE
            elif item == f"{TaskMatcher.LOSS}{TaskLoss.PART.value}":
                self.loss = TaskLoss.PART
            elif item == f"{TaskMatcher.LOSS}{TaskLoss.ZERO.value}":
                self.loss = TaskLoss.ZERO
            elif item == f"{TaskMatcher.TYPE}{TaskType.MAKE.value}":
                self.resource_type = TaskType.MAKE
            elif item == f"{TaskMatcher.TYPE}{TaskType.READ.value}":
                self.resource_type = TaskType.READ

    def __parse_fields_legacy(self, items: list[str]):
        for tag in items:
            # if c is digit, set xp
            if tag.isdigit():
                self.xp = int(tag)
            elif tag == TaskEval.TEST.value:
                self.test = TaskEval.TEST
            elif tag == TaskEval.SELF.value:
                self.test = TaskEval.SELF
            elif tag == TaskType.MAKE.value:
                self.resource_type = TaskType.MAKE
            elif tag == TaskType.READ.value:
                self.resource_type = TaskType.READ
            elif tag == TaskLoss.FREE.value:
                self.loss = TaskLoss.FREE
            elif tag == TaskLoss.PART.value:
                self.loss = TaskLoss.PART
            elif tag == TaskLoss.ZERO.value:
                self.loss = TaskLoss.ZERO

    def __set_default_values(self):
        if self.resource_type == TaskType.NULL:
            self.resource_type = TaskType.MAKE

        if self.resource_type == TaskType.READ:
            self.loss = TaskLoss.FREE
            self.test = TaskEval.SELF
        else:
            if self.loss == TaskLoss.NULL:
                self.loss = TaskLoss.PART
            if self.test == TaskEval.NULL:
                self.test = TaskEval.TEST


    @property
    def is_read(self):
        return self.resource_type == TaskType.READ
    
    @property
    def is_make(self):
        return self.resource_type == TaskType.MAKE

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
