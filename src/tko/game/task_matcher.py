import re

from tko.game.source_xp_config import SourceXpConfig
from tko.game.task_enums import EvalMode
from tko.feno.task_source import strip_source_comments


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
    EVAL = "eval="
    LEGACY_EVALS = {
        "test": EvalMode.DIFF,
        "diff": EvalMode.DIFF,
        "self": EvalMode.SELF,
    }
    PATTERN = r'(.*?)\[(.*?)\]\(([^()]*)\)(.*)$'
    REF_T = r'^- \[x\]' + PATTERN
    REF_F = r'^- \[ \]' + PATTERN
    ALLOWED = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-+/"
    NUMBER = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\Z")

    def __init__(self, xp_config: SourceXpConfig | None = None):
        self.xp_config = xp_config
        self.raw_line: str = ""
        self.raw_pre: str = ""
        self.raw_pos: str = ""
        self.title: str = ""
        self.link: str = ""
        self.is_ref: bool = False
        self.legacy_key: str | None = None
        self.legacy_key_token: str | None = None
        self.eval: EvalMode | None = None
        self.variables: dict[str, float] = {}
        self.variable_tokens: list[str] = []

    def match_pattern(self, line: str) -> bool:
        match = re.match(TaskMatcher.REF_T, line)
        is_ref = match is not None
        if match is None:
            match = re.match(TaskMatcher.REF_F, line)
            if match is None:
                return False

        self.raw_line = line
        self.raw_pre = remove_emojis(match.group(1))
        self.title = remove_emojis(match.group(2))
        self.link = match.group(3).replace("\\", "/")
        self.raw_pos = remove_emojis(match.group(4))
        self.legacy_key = None
        self.legacy_key_token = None
        self.eval = None
        self.variables = {}
        self.variable_tokens = []
        self.is_ref = is_ref
        self.__parse_legacy_key()
        words = self.filter_tags(self.raw_pre + " " + self.title + " " + self.raw_pos).split()
        self.__parse_fields(words)
        self.__require_eval()
        return True

    def filter_tags(self, text: str) -> str:
        return strip_source_comments(text).replace("`", " ").replace("<!--", " ").replace("-->", " ")

    def __parse_legacy_key(self) -> None:
        """Read old ``@key`` metadata without making it part of the format.

        Canonical tasks derive their identity from the local README path.  The
        token is retained solely so old direct GitHub links can still load
        until they are materialized.
        """
        words = self.filter_tags(self.raw_pre).split()
        for item in words:
            if item.startswith("@"):
                self.legacy_key = TaskMatcher.__filter_task_key(item)
                self.legacy_key_token = item
                break

    @staticmethod
    def is_field(value: str) -> bool:
        return value.startswith(":") or ("=" in value and value.count("=") == 1)

    def get_filled_fields(self) -> list[str]:
        output: list[str] = []
        if self.eval is not None:
            output.append(f"{self.EVAL}{self.eval.value}")
        output.extend(self.variable_tokens)
        return output

    def __parse_fields(self, words: list[str]) -> None:
        declared = set(self.xp_config.variables) if self.xp_config and self.xp_config.is_configured else None
        for item in words:
            if item.startswith(self.EVAL):
                value = item[len(self.EVAL):].lower()
                try:
                    self.eval = self.LEGACY_EVALS.get(value)
                    if self.eval is None:
                        self.eval = EvalMode(value)
                except ValueError as exc:
                    raise ValueError("eval= must be one of none, self or diff") from exc
        if self.eval is None:
            self.eval = self.__legacy_eval(words)
        if declared is not None and self.eval == EvalMode.NONE:
            return
        for item in words:
            if item.startswith(self.EVAL):
                continue
            if "=" not in item or item.count("=") != 1:
                continue
            name, raw_value = item.split("=", 1)
            if not name:
                continue
            if declared is not None:
                if name not in declared:
                    raise ValueError(f"Undeclared task variable: {name}")
                if self.NUMBER.fullmatch(raw_value) is None:
                    raise ValueError(f"Task variable {name!r} must be an integer or real number")
                self.variables[name] = float(raw_value)
                self.variable_tokens.append(item)
            else:
                # A source without XP YAML keeps arbitrary task annotations intact.
                self.variable_tokens.append(item)

    @staticmethod
    def __legacy_eval(words: list[str]) -> EvalMode | None:
        """Interpret evaluation markers accepted by repository.yaml-era indexes."""
        tags = set(re.findall(r":([a-zA-Z]+)", " ".join(words).lower()))
        if tags & {"self", "read"}:
            return EvalMode.SELF
        if tags & {"test", "diff", "make"}:
            return EvalMode.DIFF
        return None

    def __require_eval(self) -> None:
        if self.eval is None:
            # Before the unified task format, a missing evaluation meant a
            # test-based activity.  Keep old repository indexes loadable.
            self.eval = EvalMode.DIFF

    @property
    def is_url(self) -> bool:
        return self.link.startswith("http://") or self.link.startswith("https://")

    @staticmethod
    def __filter_task_key(key: str) -> str | None:
        if not key.startswith("@"):
            return None
        filtered = ""
        for char in key[1:]:
            if char in TaskMatcher.ALLOWED:
                filtered += char
            else:
                break
        return filtered or None

    @staticmethod
    def validate_key(key: str) -> None:
        if not key or key.startswith("/") or key.endswith("/") or "//" in key:
            raise ValueError(f"Invalid task key path: {key}")
        parts = key.split("/")
        if any(part in {"", ".", ".."} for part in parts):
            raise ValueError(f"Invalid task key path: {key}")
        if any("~" in part for part in parts):
            raise ValueError(f"Invalid character in task key: {key}")
