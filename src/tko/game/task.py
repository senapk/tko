from __future__ import annotations
from pathlib import Path

from tko.util.symbols import Symbols
from tko.util.rtext import RText
from tko.game.tree_item import TreeItem
from tko.game.task_info import TaskSelfInfo
from tko.game.task_config import TaskConfig, TaskEdit, TaskGrader, TaskLoss, TaskMain, TaskTest

class Task(TreeItem):
    def __init__(self):

        super().__init__()
        self.info: TaskSelfInfo = TaskSelfInfo()
        self.config: TaskConfig = TaskConfig()
        self.skills: dict[str, int] = {} # skills
        self.default_min_value = 5 # default min grade to complete task
        self.xp: int = 1
        self.quest_key = ""
        self.__is_reachable = False

        # location info
        self.target = ""
        self.line_number = 0
        self.line = ""
        self.remote_name = ""
        self.__origin_folder: Path | None = None
        self.__workspace_folder: Path | None = None

    @property
    def grader(self) -> TaskGrader:
        return self.config.build_grader(self.info)

    def clone(self) -> Task:
        new_task = Task()
        new_task.info = self.info.clone()
        new_task.config = self.config.clone()
        new_task.skills = self.skills.copy()
        new_task.xp = self.xp
        new_task.target = self.target
        new_task.quest_key = self.quest_key
        new_task.__is_reachable = self.__is_reachable

        # location info
        new_task.line_number = self.line_number
        new_task.line = self.line
        new_task.remote_name = self.remote_name
        new_task.__origin_folder = self.__origin_folder
        new_task.__workspace_folder = self.__workspace_folder
        return new_task

    def get_full_title(self, key_pad: None | int, pad_char: str = " ") -> tuple[str, str, str]:
        if key_pad is None:
            key_pad = len(self.get_key())
        if not f"@{self.get_key()}" in self.get_title():
            key = f"@{self.get_key().ljust(key_pad, pad_char)} "
            title = self.get_title()
            return key + title, key, title
        return self.get_title(), "", self.get_title()

    def set_reachable(self, reachable: bool):
        self.__is_reachable = reachable
        return self
    
    def is_optional(self):
        return self.config.path == TaskMain.SIDE
    
    def is_auto(self):
        return self.config.test == TaskTest.TEST

    def is_reachable(self) -> bool:
        return self.__is_reachable

    def is_link(self):
        if self.config.mode == TaskEdit.VIEW:
            return True
        return self.__origin_folder is None and self.__workspace_folder is None
    
    def set_remote_view_type(self):
        self.__origin_folder = None
        self.__workspace_folder = None
        return self

    def is_import_type(self):
        return self.config.mode == TaskEdit.EDIT and self.__origin_folder is not None and self.__workspace_folder is not None
    
    def is_static_type(self):
        if self.is_link():
            return False
        return self.get_origin_folder() == self.get_workspace_folder()

    def set_origin_folder(self, folder: Path):
        self.__origin_folder = folder.resolve()
        return self
    
    def get_origin_readme(self) -> Path:
        origin_folder = self.get_origin_folder()
        if origin_folder is not None:
            return origin_folder / "README.md"
        return Path("")
    
    def set_workspace_folder(self, folder: Path):
        self.__workspace_folder = folder.resolve()
        return self

    def get_origin_folder(self) -> Path | None:
        return self.__origin_folder.resolve() if self.__origin_folder is not None else None
    
    def get_workspace_folder(self) -> Path | None:
        if self.__workspace_folder is not None:
            return self.__workspace_folder.resolve()
        return self.__origin_folder.resolve() if self.__origin_folder is not None else None
    
    def is_db_empty(self) -> bool:
        return len(self.info.get_kv()) == 0

    def get_rate_color(self, value: int, min_value: None | int = None) -> str:
        if min_value is None:
            min_value = self.default_min_value
        prog = value
        if prog == 0:
            return "c"
        if prog < min_value:
            return "r"
        if prog < 10:
            return "y"
        if prog == 10:
            return "g"
        return "w"  

    def get_rate_symbol(self, value: int, min_value: None | int = None) -> RText:
        if value < 0:
            if min_value is not None:
                if value < min_value:
                    return RText("x")
        elif value < 100:
            prog = (value + 5) // 10
            color = "y" if value >= 50 else "r"
            if prog == 10:
                prog = 9
            return RText(str(prog), color)
        elif value >= 100:
            color = "g"
            return RText(Symbols.check, color)
        return RText("0")

    def get_xp(self) -> int:
        if self.xp == 0:
            return 1
        return self.xp

    def get_rate_percent(self) -> float:
        value = self.grader.get_rate_percent()
        if value < 0.1:
            return 0.0
        return value
    
    def get_quality_percent(self) -> float:
        if self.config.loss == TaskLoss.FREE:
            return 100
        value = self.grader.get_quality_percent()
        if value < 0.1:
            return 0.0
        return value



    def get_ratio(self) -> float:
        return self.grader.get_ratio()

    def is_complete(self):
        return self.grader.get_rate_percent() >= 70

    def not_started(self):
        return self.grader.get_rate_percent() == 0

    def in_progress(self):
        return 0 < self.grader.get_rate_percent() < 100

    # @override
    def __str__(self):
        lnum = str(self.line_number).rjust(3)
        key = "" if self.get_full_key() == self.get_title() else self.get_full_key() + " "
        return f"{lnum} key:{key} title:{self.get_title()} skills:{self.skills} remote:{self.target}"

    def has_at_symbol(self):
        return any([s.startswith("@") for s in self.get_title().split(" ")])
