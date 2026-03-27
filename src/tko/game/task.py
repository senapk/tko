# from typing import override
from __future__ import annotations
from pathlib import Path

from tko.util.symbols import symbols
from tko.util.text import Text
from tko.game.tree_item import TreeItem
from tko.game.task_info import TaskInfo

import enum



class Task(TreeItem):
    str_index = "idx"

    class TaskEval(enum.Enum):
        AUTO = "auto" # rate uses % of test cases passed
        USER = "user" # rate uses user self-evaluation

    class TaskPath(enum.Enum):
        MAIN = "main" # main task, required to complete the quest
        SIDE = "side" # side task, optional to complete the quest, usually with less xp reward

    class TaskHelp(enum.Enum):
        FREE = "free" # help allowed without penalty
        PART = "part" # help allowed with partial penalty
        ZERO = "zero" # if help is given, task is not completed (0% progress)

    class TaskMode(enum.Enum):
        VIEW = "view" # view task details
        EDIT = "edit" # edit task details

    class TaskGrader:
        def __init__(self, task_help: Task.TaskHelp, task_info: TaskInfo):
            self.info = task_info
            self.help = task_help
            self.grades: dict[str, dict[str, int]] = {
                Task.TaskHelp.FREE.value: {
                    "guided": 100,
                    "code": 100,
                    "debug": 100,
                    "problem": 100,
                },
                Task.TaskHelp.PART.value: {
                    "guided": 80,
                    "code": 40,
                    "debug": 80,
                    "problem": 90,
                },
                Task.TaskHelp.ZERO.value: {
                    "guided": 0,
                    "code": 0,
                    "debug": 0,
                    "problem": 0,
                },
            }


        def get_rate_percent(self):
            rate = float(self.info.rate)
            return rate
        
        def get_quality_percent(self):
            if not self.info.feedback:
                return 0.0
            rate = 100.0
            if self.info.guided:
                rate *= self.grades[self.help.value]["guided"] / 100.0
            if self.info.ia_code:
                rate *= self.grades[self.help.value]["code"] / 100.0
            if self.info.ia_debug:
                rate *= self.grades[self.help.value]["debug"] / 100.0
            if self.info.ia_problem:
                rate *= self.grades[self.help.value]["problem"] / 100.0
            return rate

        def get_ratio(self) -> float:
            return self.get_rate_percent() / 100.0

    def __init__(self):

        super().__init__()
        self.line_number = 0
        self.line = ""
        self.info = TaskInfo()
        self.main_idx: int = 0
        
        self.task_eval: Task.TaskEval = Task.TaskEval.AUTO
        self.task_path: Task.TaskPath = Task.TaskPath.MAIN
        self.task_help: Task.TaskHelp = Task.TaskHelp.PART
        self.task_mode: Task.TaskMode = Task.TaskMode.EDIT
        
        self.grader = Task.TaskGrader(self.task_help, self.info)

        self.skills: dict[str, int] = {} # skills
        
        self.xp: int = 1
        
        self.target = ""
        self.quest_key = ""
        self.remote_name = ""
        self.__origin_folder: Path | None = None
        self.__workspace_folder: Path | None = None
        self.__is_reachable = False
        self.default_min_value = 5 # default min grade to complete task

    def clone(self) -> Task:
        new_task = Task()
        new_task.line_number = self.line_number
        new_task.line = self.line
        new_task.info = self.info.clone()
        new_task.main_idx = self.main_idx
        new_task.task_eval = self.task_eval
        new_task.task_path = self.task_path
        new_task.task_help = self.task_help
        new_task.task_mode = self.task_mode
        new_task.grader = Task.TaskGrader(new_task.task_help, new_task.info)
        new_task.skills = self.skills.copy()
        new_task.xp = self.xp
        new_task.target = self.target
        new_task.quest_key = self.quest_key
        new_task.remote_name = self.remote_name
        new_task.__origin_folder = self.__origin_folder
        new_task.__workspace_folder = self.__workspace_folder
        new_task.__is_reachable = self.__is_reachable
        return new_task

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
    
    def is_auto(self):
        return self.task_eval == Task.TaskEval.AUTO

    def is_reachable(self) -> bool:
        return self.__is_reachable

    def is_link(self):
        if self.task_mode == Task.TaskMode.VIEW:
            return True
        return self.__origin_folder is None and self.__workspace_folder is None
    
    def set_remote_view_type(self):
        self.__origin_folder = None
        self.__workspace_folder = None
        return self

    def is_import_type(self):
        return self.task_mode == Task.TaskMode.EDIT and self.__origin_folder is not None and self.__workspace_folder is not None
    
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

    def get_rate_symbol(self, value: int, min_value: None | int = None) -> Text:
        if min_value is None:
            min_value = self.default_min_value
        color = self.get_rate_color(value, min_value)
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

    def get_rate_percent(self) -> float:
        value = self.grader.get_rate_percent()
        if value < 0.1:
            return 0.0
        return value
    
    def get_quality_percent(self) -> float:
        if self.task_help == Task.TaskHelp.FREE:
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
