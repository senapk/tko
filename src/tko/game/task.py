# from typing import override
from tko.util.symbols import symbols
from tko.util.text import Text
from tko.game.tree_item import TreeItem
from tko.game.task_info import TaskInfo
from tko.game.task_grader import TaskGrader
import enum
import os


class Task(TreeItem):
    str_index = "idx"

    class Types(enum.Enum):
        UNDEFINED = 0
        VISITABLE_URL = 1
        STATIC_FILE = 2 # static folder inside database
        REMOTE_FILE = 3 # url link do download file
        IMPORT_FILE = 4 # source folder outside database to import files

        # @override
        def __str__(self):
            return self.name

    def __init__(self):

        super().__init__()
        self.line_number = 0
        self.line = ""
        self.info = TaskInfo()
        self.grader = TaskGrader(self.info)
        self.main_idx: int = 0
        self.leet: bool = False # if the task is a leet task, rate must be marked by running test cases
        self.skills: dict[str, int] = {} # skills
        
        self.xp: int = 0
        self.opt: bool = False
        
        self.link = ""
        self.link_type: Task.Types = Task.Types.UNDEFINED

        self.quest_key = ""
        self.cluster_key = ""
        self.__rep_folder_path: str | None = None
        self.__is_reachable = False
        self.default_min_value = 5 # default min grade to complete task

    def is_optional(self) -> bool:
        return self.opt

    def set_leet(self, value: bool):
        self.leet = value
        return self
    
    def is_leet(self) -> bool:
        return self.leet

    def set_reachable(self, reachable: bool):
        self.__is_reachable = reachable
        return self

    def is_reachable(self) -> bool:
        return self.__is_reachable

    def set_rep_folder(self, path: str):
        self.__rep_folder_path = path
        return self

    def get_folder_try(self) -> str:
        if self.__rep_folder_path is None:
            raise Warning("Repository folder path not set for task " + self.get_db_key())
        return os.path.join(self.__rep_folder_path, self.get_database(), self.get_only_key())
    
    @staticmethod
    def decode_approach_autonomy(value: int) -> tuple[int, int]:
        opts = [(0, 0), (1, 1), (1, 2), (2, 2), (3, 2), (1, 3), (2, 3), (3, 3), (4, 3), (3, 4), (4, 4)]
        autonomy = opts[value][0]
        skill = opts[value][1]
        return autonomy, skill

    def decode_from_dict(self, value: str):
        value_list = value[1:-1]
        kv_dict: dict[str, str] = {}
        key_values = value_list.split(",")
        for kv in key_values:
            (k, val) = kv.split(":")
            kv_dict[k.strip()] = val.strip()
        
        self.info.load_from_kv(kv_dict)
        if self.str_index in kv_dict:
            self.main_idx = int(kv_dict[self.str_index])

        # deprecated
        for k, val in kv_dict.items():
            if k == "cov" or k == 'cove':
                self.info.rate = int(val)
            elif k == "aut" or k == "appr":
                self.info.flow = int(val)
            elif k == "hab" or k == "auto":
                self.info.edge = int(val)
            elif k == "desc":
                self.info.neat = int(val)
            elif k == "desire":
                self.info.cool = int(val)
            elif k == "effort":
                self.info.easy = int(val)

    def load_from_db(self, value: str):
        if value.startswith("{"):
            self.decode_from_dict(value)
        # deprecated
        elif ":" not in value:
            self.info.flow, self.info.edge = Task.decode_approach_autonomy(int(value))
        else:
            v = value.split(":")
            if len(v) == 3:
                self.info.flow, self.info.edge = Task.decode_approach_autonomy(int(v[0]))
                self.main_idx = int(v[1])
                self.info.rate = int(v[2])
            elif len(v) == 4:
                self.info.rate = (int(v[0]))
                self.info.flow = (int(v[1]))
                self.info.edge = (int(v[2]))
                self.main_idx = (int(v[3]))
            else:
                raise ValueError(f"Invalid task value format: {value}. Expected format is 'flow:edge:main_idx:rate' or '{self.str_index}:value'.")

    def save_to_db(self) -> str:
        kv_dict = self.info.get_filled_kv()
        if self.main_idx != 0:
            kv_dict[self.str_index] = str(self.main_idx)
        return "{" + ", ".join(f"{k}:{v}" for k, v in kv_dict.items()) + "}"

    def is_db_empty(self) -> bool:
        return len(self.info.get_filled_kv()) == 0

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
        key = "" if self.get_db_key() == self.get_title() else self.get_db_key() + " "
        return f"{lnum} key:{key} title:{self.get_title()} skills:{self.skills} remote:{self.link} type:{self.link_type} folder:{self.get_folder_try()}"

    def has_at_symbol(self):
        return any([s.startswith("@") for s in self.get_title().split(" ")])
