from pathlib import Path
from tko.game.task_enums import TaskEval, TaskType
from tko.i18n import  Msg
from tko.game.task_matcher import TaskMatcher
from tko.run.wdir import Wdir
from tko.config.settings import Settings

_INDEXER_INVALID_LABEL = Msg.text(
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
        self.tm.raw_line = ""
        self.tm.raw_pre = ""
        self.tm.raw_pos = ""
        self.tm.key = readme_file.parent.name
        self.tm.resource_type = TaskType.MAKE
        self.tm.eval = TaskEval.TEST
        self.tm.title = title
        self.origin_key = self.target_file.parent.name
        return self

    def get_pre(self, key_pad: int, fields_pad: int) -> str:
        fields = self.tm.get_filled_fields()
        tags = [f for f in fields if not f.startswith("@")]
        tags_str = " ".join(tags)

        words = self.tm.raw_pre.replace("`", " ").replace("- [ ]", " ").replace("- [x]", " ").replace("<!--", " ").replace("-->", " ").split()
        left = " ".join(x for x in words if not self.tm.is_field(x))

        key_tag = f"@{self.key}"
        if left:
            out = f" `{key_tag:<{key_pad + 1}} {tags_str:<{fields_pad}}` {left} "
        else:
            out = f" `{key_tag:<{key_pad + 1}} {tags_str:<{fields_pad}}` "
        return out

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

    def render_line(self, key_pad: int, fields_pad: int = 42) -> str:
        ref = "x" if self.tm.is_ref else " "
        link = self.tm.link
        if self.target_file is not None:
            link = self.target_file.resolve().relative_to(self.index_path.parent.resolve(), walk_up=True).as_posix()
        elif self.url is not None:
            link = self.url
        return f"- [{ref}]{self.get_pre(key_pad, fields_pad)}[{self.tm.title}]({link}){self.tm.raw_pos}"
