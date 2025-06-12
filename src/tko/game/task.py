# from typing import override
from tko.util.symbols import symbols
from tko.util.text import Text
from tko.game.tree_item import TreeItem
import enum


class Task(TreeItem):

    class Types(enum.Enum):
        UNDEFINED = 0
        VISITABLE_URL = 1
        STATIC_FILE = 2 # static folder inside database
        REMOTE_FILE = 3 # url link do download file
        IMPORT_FILE = 4 # source folder outside database to import files

        # @override
        def __str__(self):
            return self.name

    # default values for tasks
    flow_max = 6
    edge_max = 5
    neat_max = 5
    cool_max = 5
    easy_max = 5

    def __init__(self):

        super().__init__()
        self.line_number = 0
        self.line = ""

        self.rate: int = 0 # valor de 0 a 100
        self.flow: int = 0 # valor de 0 a approach_max
        self.edge: int = 0 # valor de 0 a autonomy_max
        self.main_idx: int = 0

        self.neat: int = 0
        self.cool: int = 0
        self.easy: int = 0

        self.leet: bool = False # if the task is a leet task

        self.qskills: dict[str, int] = {} # default quest skills
        self.skills: dict[str, int] = {} # local skills
        
        self.xp: int = 0
        self.opt: bool = False
        
        self.link = ""
        self.link_type: Task.Types = Task.Types.UNDEFINED

        self.quest_key = ""
        self.cluster_key = ""

        self.folder: str | None = None # the place where are the test case file
        self.__is_reachable = False
        self.default_min_value = 7 # default min grade to complete task

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

    def set_folder(self, folder: str):
        self.folder = folder
        return self
    
    def get_folder(self) -> str | None:
        return self.folder
    
    @staticmethod
    def decode_approach_autonomy(value: int) -> tuple[int, int]:
        opts = [(0, 0), (1, 1), (1, 2), (2, 2), (3, 2), (1, 3), (2, 3), (3, 3), (4, 3), (3, 4), (4, 4)]
        autonomy = opts[value][0]
        skill = opts[value][1]
        return autonomy, skill

    def load_from_db(self, value: str):
        if value.startswith("{"):
            value_list = value[1:-1]
            key_values = value_list.split(",")
            for kv in key_values:
                k, val = kv.split(":")
                k = k.strip()
                val = val.strip()
                if k == "cov" or k == "rate":
                    self.rate = int(val)
                elif k == "aut" or k == "flow":
                    self.flow = int(val)
                elif k == "hab" or k == "edge":
                    self.edge = int(val)
                elif k == "desc" or k == "neat":
                    self.neat = int(val)
                elif k == "desire" or k == "cool":
                    self.cool = int(val)
                elif k == "effort" or k == "easy":
                    self.easy = int(val)
                elif k == "idx":
                    self.main_idx = int(val)
        elif ":" not in value:
            self.flow, self.edge = Task.decode_approach_autonomy(int(value))
        else:
            v = value.split(":")
            if len(v) == 3:
                self.flow, self.edge = Task.decode_approach_autonomy(int(v[0]))
                self.main_idx = int(v[1])
                self.rate = int(v[2])
            elif len(v) == 4:
                self.rate = (int(v[0]))
                self.flow = (int(v[1]))
                self.edge = (int(v[2]))
                self.main_idx = (int(v[3]))

    def save_to_db(self) -> str:
        return "{" + f"rate:{self.rate}, flow:{self.flow}, edge:{self.edge}, neat:{self.neat}, cool:{self.cool}, easy:{self.easy}, idx:{self.main_idx}" + "}"

    def is_db_empty(self) -> bool:
        return self.flow == 0 and self.edge == 0 and self.main_idx == 0 and self.rate == 0

    def get_prog_color(self, min_value: None | int = None) -> str:
        if min_value is None:
            min_value = self.default_min_value
        prog = self.rate // 10
        if prog == 0:
            return "c"
        if prog < min_value:
            return "r"
        if prog < 10:
            return "y"
        if prog == 10:
            return "g"
        return "w"  

    def get_prog_symbol(self, min_value: None | int = None) -> Text:
        
        if min_value is None:
            min_value = self.default_min_value
        color = self.get_prog_color(min_value)
        prog = self.rate // 10
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

    def get_percent(self):
        app_aut = ((self.flow + self.edge) * 100) / 11
        return (app_aut + self.rate) / 2

    def get_ratio(self) -> float:
        return self.get_percent() / 10.0

    def is_complete(self):
        return self.get_percent() >= 100

    def not_started(self):
        return self.get_percent() == 0
    
    def in_progress(self):
        return self.get_percent() > 0 and self.get_percent() < 100

    def set_rate(self, coverage: int):
        coverage = int(coverage)
        if coverage >= 0 and coverage <= 100:
            self.rate = coverage
        else:
            print(f"Progresso inválido: {coverage}")

    def set_flow(self, value: int):
        value = int(value)
        if value >= 0 and value <= Task.flow_max:
            self.flow = value
        else:
            print(f"Flow inválido: {value}")

    def set_edge(self, value: int):
        value = int(value)
        if value >= 0 and value <= Task.edge_max:
            self.edge = value
        else:
            print(f"Edge inválido: {value}")

    def set_neat(self, value: int):
        value = int(value)
        if value >= 0 and value <= Task.neat_max:
            self.neat = value
        else:
            print(f"Neat inválido: {value}")

    def set_cool(self, value: int):
        value = int(value)
        if value >= 0 and value <= Task.cool_max:
            self.cool = value
        else:
            print(f"Cool inválido: {value}")

    def set_easy(self, value: int):
        value = int(value)
        if value >= 0 and value <= Task.easy_max:
            self.easy = value
        else:
            print(f"Easy inválido: {value}")

    # @override
    def __str__(self):
        lnum = str(self.line_number).rjust(3)
        key = "" if self.key == self.title else self.key + " "
        return f"{lnum} grade:{self.flow}:{self.edge} key:{key} title:{self.title} skills:{self.skills} remote:{self.link} type:{self.link_type} folder:{self.folder}"

    def has_at_symbol(self):
        return any([s.startswith("@") for s in self.title.split(" ")])
