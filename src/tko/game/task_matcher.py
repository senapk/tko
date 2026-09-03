import re

from tko.game.task_enums import EvalMode

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
    GAIN = "gain="
    COST = "cost="
    SIZE = "size="
    GCS = "gcs="
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

        self.eval: EvalMode | None = None
        self.gain = 1
        self.cost = 1
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
        self.eval = None
        self.gain = 1
        self.cost = 1
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

        if self.eval is not None:
            output.append(f"{TaskMatcher.EVAL}{self.eval.value}")

        gcs = [self.gain, self.cost, self.size]
        while len(gcs) > 1 and gcs[-1] == 1:
            gcs.pop()
        output.append(f"{TaskMatcher.GCS}{''.join(str(value) for value in gcs)}")

        return output

    def __parse_fields(self, words: list[str]):
        compact_values: tuple[int, int, int] | None = None
        explicit_gain: int | None = None
        explicit_cost: int | None = None
        explicit_size: int | None = None

        for item in words:
            item = item.lower()
            if item.startswith(TaskMatcher.GCS):
                compact_values = self.__parse_gcs(item[len(TaskMatcher.GCS):])
                continue
            if item.startswith(TaskMatcher.COST):
                if (cost_value := self.parse_int(item[len(TaskMatcher.COST):])) is not None:
                    explicit_cost = min(cost_value, 6)
                continue
            if item.startswith(TaskMatcher.GAIN):
                if (gain_value := self.parse_int(item[len(TaskMatcher.GAIN):])) is not None:
                    explicit_gain = min(gain_value, 3)
                continue
            if item.startswith(TaskMatcher.SIZE):
                if (size_value := self.parse_int(item[len(TaskMatcher.SIZE):])) is not None:
                    explicit_size = min(size_value, 3)
                continue
            elif item.startswith(TaskMatcher.EVAL):
                value = item[len(TaskMatcher.EVAL):]
                try:
                    self.eval = EvalMode(value)
                except ValueError as exc:
                    raise ValueError("eval= must be one of none, self or diff") from exc
            elif item.startswith(("hard=", "tier=", "xp=", "type=")):
                raise ValueError("Obsolete task field; use eval=none|self|diff, gain=, cost= and size=")
            elif item.startswith(":") and item[1:] in {"read", "make", "self", "diff", "test"}:
                raise ValueError("Legacy colon task tags are unsupported; use eval=none|self|diff")

        if compact_values is not None:
            self.gain, self.cost, self.size = compact_values
        if explicit_gain is not None:
            self.gain = explicit_gain
        if explicit_cost is not None:
            self.cost = explicit_cost
        if explicit_size is not None:
            self.size = explicit_size

    @staticmethod
    def __parse_gcs(value: str) -> tuple[int, int, int]:
        if not re.fullmatch(r"[1-9][0-9]{0,2}", value):
            raise ValueError("gcs= must contain one to three non-zero digits")

        values = [int(digit) for digit in value]
        gain, cost, size = (values + [1, 1, 1])[:3]
        if not 1 <= gain <= 3 or not 1 <= cost <= 6 or not 1 <= size <= 3:
            raise ValueError("gcs= values must be gain 1-3, cost 1-6 and size 1-3")
        return gain, cost, size

    def __set_default_values(self):
        if self.eval is None:
            raise ValueError("Task evaluation is required: use eval=none, eval=self or eval=diff")

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
