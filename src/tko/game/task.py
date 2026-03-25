# from typing import override
from pathlib import Path

from tko.util.symbols import symbols
from tko.util.text import Text
from tko.game.tree_item import TreeItem
from tko.game.task_info import TaskInfo
from tko.game.task_grader import TaskGrader
import enum


class Task(TreeItem):
    str_index = "idx"

    class TaskRate(enum.Enum):
        AUTO = "auto" # rate uses % of test cases passed
        USER = "user" # rate uses user self-evaluation
        TICK = "tick" # no rate, just tick when complete

    class TaskPath(enum.Enum):
        MAIN = "main" # main task, required to complete the quest
        SIDE = "side" # side task, optional to complete the quest, usually with less xp reward

    class TaskHelp(enum.Enum):
        OPEN = "open" # help allowed
        EXAM = "exam" # no help allowed, must be done alone

    class TaskAction(enum.Enum):
        VIEW = "view" # view task details
        EDIT = "edit" # edit task details

    def __init__(self):

        super().__init__()
        self.line_number = 0
        self.line = ""
        self.info = TaskInfo()
        self.grader = TaskGrader(self.info)
        self.main_idx: int = 0
        
        self.task_rate: Task.TaskRate = Task.TaskRate.AUTO
        self.task_path: Task.TaskPath = Task.TaskPath.MAIN
        self.task_help: Task.TaskHelp = Task.TaskHelp.OPEN
        self.task_action: Task.TaskAction = Task.TaskAction.EDIT

        self.skills: dict[str, int] = {} # skills
        
        self.xp: int = 1
        
        self.target = ""
        self.quest_key = ""
        self.remote_name = ""
        self.__origin_folder: Path | None = None
        self.__workspace_folder: Path | None = None
        self.__is_reachable = False
        self.default_min_value = 5 # default min grade to complete task

    def get_full_title(self, key_pad: None | int):
        if key_pad is None:
            key_pad = len(self.get_key())
        if not f"@{self.get_key()}" in self.get_title():
            return f"@{self.get_key().ljust(key_pad)} {self.get_title()}"
        return self.get_title()

    def set_reachable(self, reachable: bool):
        self.__is_reachable = reachable
        return self
    
    def is_optional(self):
        return self.task_path == Task.TaskPath.SIDE
    
    def is_leet(self):
        return self.task_rate == Task.TaskRate.AUTO

    def is_reachable(self) -> bool:
        return self.__is_reachable

    def is_link(self):
        if self.task_action == Task.TaskAction.VIEW:
            return True
        return self.__origin_folder is None and self.__workspace_folder is None
    
    def set_remote_view_type(self):
        self.__origin_folder = None
        self.__workspace_folder = None
        return self

    def is_import_type(self):
        return self.task_action == Task.TaskAction.EDIT and self.__origin_folder is not None and self.__workspace_folder is not None
    
    def is_static_type(self):
        if self.is_link():
            return False
        return self.get_origin_folder() == self.get_workspace_folder()

    def set_origin_folder(self, folder: Path):
        self.__origin_folder = folder
        return self
    
    def get_origin_readme(self) -> Path:
        origin_folder = self.get_origin_folder()
        if origin_folder is not None:
            return origin_folder / "README.md"
        return Path("")
    
    def set_workspace_folder(self, folder: Path):
        self.__workspace_folder = folder
        return self

    def get_origin_folder(self) -> Path | None:
        return self.__origin_folder
    
    def get_workspace_folder(self) -> Path | None:
        if self.__workspace_folder is not None:
            return self.__workspace_folder
        return self.__origin_folder
    
    def decode_from_dict(self, value: str):
        value_list = value[1:-1]
        kv_dict: dict[str, str] = {}
        key_values = value_list.split(",")
        for kv in key_values:
            if ":" not in kv:
                continue
            (k, val) = kv.split(":")
            kv_dict[k.strip()] = val.strip()
        
        self.info.load_from_kv(kv_dict)
        if self.str_index in kv_dict:
            self.main_idx = int(kv_dict[self.str_index])

        # deprecated
        # for k, val in kv_dict.items():
        #     if k == "cov" or k == 'cove':
        #         self.info.rate = int(val)
        #     elif k == "aut" or k == "appr":
        #         self.info.flow = int(val)
        #     elif k == "hab" or k == "auto":
        #         self.info.edge = int(val)
        #     elif k == "desc":
        #         self.info.neat = int(val)
        #     elif k == "desire":
        #         self.info.cool = int(val)
        #     elif k == "effort":
        #         self.info.easy = int(val)

    def load_from_db(self, value: str):
        if value.startswith("{"):
            self.decode_from_dict(value)
        else:
            raise ValueError(f"Invalid task value format: {value}. Expected format is 'flow:edge:main_idx:rate' or '{self.str_index}:value'.")

    def save_to_db(self) -> str:
        kv_dict = self.info.get_kv()
        if self.main_idx != 0:
            kv_dict[self.str_index] = str(self.main_idx)
        return "{" + ", ".join(f"{k}:{v}" for k, v in kv_dict.items()) + "}"

    def is_db_empty(self) -> bool:
        return len(self.info.get_kv()) == 0

    def get_prog_color(self, value: int, min_value: None | int = None) -> str:
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

    def get_prog_symbol(self, value: int, min_value: None | int = None) -> Text:
        if min_value is None:
            min_value = self.default_min_value
        color = self.get_prog_color(value, min_value)
        prog = value
        if prog == 0:
            return Text().add("x")
        if prog < min_value:
            return Text().addf(color, str(prog))
        if prog < 10:
            return Text().addf(color, str(prog))
        if prog == 10:
            return Text().addf(color, symbols.check.text)
        return Text().add("0")

    def get_xp(self) -> int:
        if self.xp == 0:
            return 1
        return self.xp

    def get_percent(self) -> float:
        value = self.grader.get_percent()
        if value < 0.1:
            return 0.0
        return value

    def get_ratio(self) -> float:
        return self.grader.get_ratio()

    def is_complete(self):
        return self.grader.get_percent() >= 70

    def not_started(self):
        return self.grader.get_percent() == 0

    def in_progress(self):
        return 0 < self.grader.get_percent() < 100

    # @override
    def __str__(self):
        lnum = str(self.line_number).rjust(3)
        key = "" if self.get_full_key() == self.get_title() else self.get_full_key() + " "
        return f"{lnum} key:{key} title:{self.get_title()} skills:{self.skills} remote:{self.target}"

    def has_at_symbol(self):
        return any([s.startswith("@") for s in self.get_title().split(" ")])
