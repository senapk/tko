from __future__ import annotations

from tko.util.symbols import Symbols
from tko.util.rtext import RText
from tko.game.tree_item import TreeItem, TreeUi
from tko.game.task_info import TaskSelfInfo
from tko.game.task_config import TaskConfig, TaskGrader, TaskLoss, TaskMain, TaskTest
from tko.game.task_location import TaskLocation

class Task:
    def __init__(self):
        self.identity = TreeItem()
        self.ui = TreeUi()
        self.info: TaskSelfInfo = TaskSelfInfo()
        self.config: TaskConfig = TaskConfig()
        self.main_idx: int = 0
        self.skills: dict[str, int] = {} # skills
        self.default_min_value = 5 # default min grade to complete task
        self.xp: int = 1
        self.quest_key = ""
        self.__is_reachable = False
        self.location = TaskLocation()

    @property
    def grader(self) -> TaskGrader:
        return self.config.build_grader(self.info)

    def clone(self) -> Task:
        new_task = Task()
        new_task.identity.set_remote_name(self.identity.get_remote_name())
        new_task.identity.set_key(self.identity.get_key())
        new_task.identity.set_title(self.identity.get_title())
        new_task.ui = self.ui.clone()
        new_task.info = self.info.clone()
        new_task.config = self.config.clone()
        new_task.main_idx = self.main_idx
        new_task.skills = self.skills.copy()
        new_task.xp = self.xp
        new_task.quest_key = self.quest_key
        new_task.__is_reachable = self.__is_reachable
        new_task.location = self.location.clone()
        return new_task

    def get_full_title(self, key_pad: None | int, pad_char: str = " ") -> tuple[str, str, str]:
        if key_pad is None:
            key_pad = len(self.identity.get_key())
        if not f"@{self.identity.get_key()}" in self.identity.get_title():
            key = f"@{self.identity.get_key().ljust(key_pad, pad_char)} "
            title = self.identity.get_title()
            return key + title, key, title
        return self.identity.get_title(), "", self.identity.get_title()

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
        return self.location.is_link(self.config.mode)

    def is_import_type(self):
        return self.location.is_import_type(self.config.mode)
    
    def is_static_type(self):
        return self.location.is_static_type(self.config.mode)
    
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
        lnum = str(self.location.line_number).rjust(3)
        key = "" if self.identity.get_full_key() == self.identity.get_title() else self.identity.get_full_key() + " "
        return f"{lnum} key:{key} title:{self.identity.get_title()} skills:{self.skills} remote:{self.location.target}"

    def has_at_symbol(self):
        return any([s.startswith("@") for s in self.identity.get_title().split(" ")])
