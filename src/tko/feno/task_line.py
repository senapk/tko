from pathlib import Path
from tko.game.task_enums import TaskEval
from tko.i18n import  Msg
from tko.game.task_matcher import TaskMatcher
from tko.run.wdir import Wdir
from tko.config.settings import Settings
from tko.game.task_enums import TaskType
import logging

logger = logging.getLogger(__name__)

_INDEXER_INVALID_LABEL = Msg(
    pt="Rótulo inválido na linha: {label}",
    en="Invalid label in line: {label}",
)

class TestsFinder:
    @staticmethod
    def find_tests(folder: Path) -> bool:
        wdir: Wdir = Wdir(Settings(None))
        wdir.lang = "c"
        wdir.setup_from_target_list([folder])
        wdir.build_unit_list()
        return len(wdir.unit_list) > 0


class TaskLine:
    def __init__(self, index_path: Path, base_dir: Path):
        self.tm = TaskMatcher()

        self.origin_key: str | None = None
        self.target_file: Path | None = None
        self.url: str | None = None
        
        self.index_path: Path = index_path.resolve()
        self.base_dir: Path = base_dir.resolve()
    
    def init_by_line(self, line: str) -> bool:
        self.raw_line = line
        tm = self.tm
        if not tm.match_pattern(line):
            return False

        self.origin_key = tm.key
        if self.tm.is_url:
            self.url = self.tm.link
            return True

        link = Path(tm.link)
        if not self.tm.is_read:
            if link.name != "README.md":
                raise ValueError(f"Task activity must point to a README file: {link}")
        if link.is_absolute():
            self.target_file = Path(link).resolve()
        else:
            self.target_file = (self.index_path.parent / link).resolve()
        return True

    def init_by_readme_file(self, readme_file: Path, title: str):
        self.target_file = readme_file
        self.tm.title = title
        self.origin_key = self.target_file.parent.name
        return self

    def get_pre(self, key_pad: int, fields_pad: int) -> str:
        _eval = ""
        if self.tm.is_make:
            if self.has_tests():
                _eval = f" :{TaskEval.TEST.value}"
            else:
                _eval = f" :{TaskEval.SELF.value}"

        test_icon = "🤖"
        self_icon = "👤"

        read_icon = "📖"
        make_icon = "🛠️"

        def make_icons() -> str:
            icons: list[str] = []
            if self.tm.is_read:
                icons.append(read_icon)
            elif self.tm.is_make:
                icons.append(make_icon)

            if self.tm.is_make and self.has_tests():
                icons.append(test_icon)
            else:
                icons.append(self_icon)
            return " ".join(icons)
        
        def filter_icons(s: str) -> str:
            for icon in [read_icon, make_icon, test_icon, self_icon]:
                s = s.replace(icon, "")
            return s

        fields = self.tm.get_filled_fields()
        fields = [f for f in fields if (
            not f.startswith("@") and 
            not f.startswith(TaskMatcher.EVAL)
            )]
        fields = " ".join(fields) + _eval
        words = self.tm.raw_pre.replace("`", " ").replace("- [ ]", " ").replace("<!--", " ").replace("-->", " ").split()
        left = " ".join(x for x in words if not self.tm.is_field(x))
        left = filter_icons(left)
        out = f" `@{self.key:<{key_pad + 1}}{make_icons()} {fields:<{fields_pad}}` {left}"
        return out
    
    def has_tests(self) -> bool:
        if self.tm.is_read or self.target_file is None:
            return False
        return TestsFinder().find_tests(self.target_file.parent)
        # load wdir in this folder and check number os tests

    @property
    def key(self) -> str:
        if self.tm.is_read:
            return self.origin_key if self.origin_key is not None else ""
        if self.target_file is not None:
            if self.target_file.resolve().is_relative_to(self.base_dir.resolve()):
                return self.target_file.parent.name
        if self.origin_key is not None:
            return self.origin_key
        return ""
    
    def render_line(self, key_pad: int) -> str:
        # after = f"{_type} {_eval}"
        fields_pad = len("type=make xp=4 tier=1 loss=part :test")
        ref = "x" if self.tm.is_ref else " "
        link = self.tm.link
        if self.target_file is not None:
            link = self.target_file.resolve().relative_to(self.index_path.parent.resolve(), walk_up=True)
        elif self.url is not None:
            link = self.url
        return f"- [{ref}]{self.get_pre(key_pad, fields_pad)}[{self.tm.title}]({link}){self.tm.raw_pos}"