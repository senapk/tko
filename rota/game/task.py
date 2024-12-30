from typing import Dict, Optional, Tuple
from rota.util.symbols import symbols
from rota.util.text import Text
from rota.game.tree_item import TreeItem
from rota.util.get_md_link import get_md_link
import re
import os
import enum



class Task(TreeItem):

    class Types(enum.Enum):
        UNDEFINED = 0
        VISITABLE_URL = 1
        STATIC_FOLDER = 2 # static folder inside database
        IMPORT_REMOTE = 3 # url link do download file
        IMPORT_FOLDER = 4 # source folder outside database to import files

        def __str__(self):
            return self.name

    def __init__(self):
        super().__init__()
        self.line_number = 0
        self.line = ""

        self.coverage: int = 0 # valor de 0 a 100
        self.autonomy: int = 0 # valor de 0 a 5
        self.ability: int = 0 # valor de 0 a 5
        self.main_idx: int = 0

        self.qskills: Dict[str, int] = {} # default quest skills
        self.skills: Dict[str, int] = {} # local skills
        self.xp: int = 0

        self.opt: bool = False
        
        self.link = ""
        self.link_type: Task.Types = Task.Types.UNDEFINED

        self.quest_key = ""
        self.cluster_key = ""

        self.folder: str | None = None # the place where are the test case file
        self.__is_reachable = False
        self.default_min_value = 7 # default min grade to complete task


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
    
    def set_autonomy_ability(self, value: int):
        opts = [(0, 0), (1, 1), (1, 2), (2, 2), (3, 2), (1, 3), (2, 3), (3, 3), (4, 3), (3, 4), (4, 4)]
        self.autonomy = opts[value][0]
        self.ability = opts[value][1]

    def load_from_db(self, value: str):
        if value.startswith("{"):
            value_list = value[1:-1]
            key_values = value_list.split(",")
            for kv in key_values:
                k, val = kv.split(":")
                k = k.strip()
                val = val.strip()
                if k == "cov":
                    self.coverage = int(val)
                elif k == "aut":
                    self.autonomy = int(val)
                elif k == "hab":
                    self.ability = int(val)
                elif k == "idx":
                    self.main_idx = int(val)
        elif ":" not in value:
            self.set_autonomy_ability(int(value))
        else:
            v = value.split(":")
            if len(v) == 3:
                self.set_autonomy_ability(int(v[0]))
                self.main_idx = int(v[1])
                self.coverage = int(v[2])
            elif len(v) == 4:
                self.coverage = (int(v[0]))
                self.autonomy = (int(v[1]))
                self.ability = (int(v[2]))
                self.main_idx = (int(v[3]))

    def save_to_db(self) -> str:
        return "{" + f"cov:{self.coverage}, aut:{self.autonomy}, hab:{self.ability}, idx:{self.main_idx}" + "}"
    
    def is_db_empty(self) -> bool:
        return self.autonomy == 0 and self.ability == 0 and self.main_idx == 0 and self.coverage == 0

    def get_prog_color(self, min_value: Optional[int] = None) -> str:
        if min_value is None:
            min_value = self.default_min_value
        prog = self.coverage // 10
        if prog == 0:
            return "c"
        if prog < min_value:
            return "r"
        if prog < 10:
            return "y"
        if prog == 10:
            return "g"
        return "w"  

    def get_prog_symbol(self, min_value: Optional[int] = None) -> Text:
        
        if min_value is None:
            min_value = self.default_min_value
        color = self.get_prog_color(min_value)
        prog = self.coverage // 10
        if prog == 0:
            return Text().add("x")
        if prog < min_value:
            return Text().addf(color, str(prog))
        if prog < 10:
            return Text().addf(color, str(prog))
        if prog == 10:
            return Text().addf(color, symbols.check.text)
        return Text().add("0")

    def get_percent(self):
        return (self.autonomy / 5) * (self.ability / 5) * self.coverage
    
    def get_ratio(self) -> float:
        return self.get_percent() / 10.0

    def is_complete(self):
        return self.get_percent() == 100

    def not_started(self):
        return self.get_percent() == 0
    
    def in_progress(self):
        return self.get_percent() > 0 and self.get_percent() < 100

    def set_coverage(self, coverage: int):
        coverage = int(coverage)
        if coverage >= 0 and coverage <= 100:
            self.coverage = coverage
        else:
            print(f"Progresso inválido: {coverage}")

    def set_autonomy(self, value: int):
        value = int(value)
        if value >= 0 and value <= 5:
            self.autonomy = value
        else:
            print(f"Autonomia inválida: {value}")

    def set_hability(self, value: int):
        value = int(value)
        if value >= 0 and value <= 5:
            self.ability = value
        else:
            print(f"Compreensão inválida: {value}")

    def __str__(self):
        lnum = str(self.line_number).rjust(3)
        key = "" if self.key == self.title else self.key + " "
        return f"{lnum} grade:{self.autonomy}:{self.ability} key:{key} title:{self.title} skills:{self.skills} remote:{self.link} type:{self.link_type} folder:{self.folder}"

    def has_at_symbol(self):
        return any([s.startswith("@") for s in self.title.split(" ")])

class TaskParser:

    def __init__(self, index_path: str, database_folder: str):
        self.index_path = os.path.abspath(index_path) # path of Repository Root Readme file
        self.database_folder = os.path.abspath(database_folder)
        self.task = Task()

    def __load_tags(self, tags_raw: str):
        task = self.task
        tags = [tag.strip() for tag in tags_raw.split(" ")]
        task.opt = "opt" in tags
        for t in tags:
            if t.startswith("+"):
                key, value = t[1:].split(":")
                task.skills[key] = int(value)

    def parse_line(self, line: str, line_num: int = 0) -> Optional[Task]:
        pattern = r'\s*?- \[ \](.*?)\[([^\]]+)\]\(([^)]+)\)(?:\s*<!--(.*?)-->)?'

        match = re.match(pattern, line)
        if match is None:
            return None
        task = self.task
        task.line_number = line_num
        task.line = line
        task.title = match.group(1).strip()
        if task.title != "":
            task.title += " "
        task.title += match.group(2).strip()
        task.title = task.title.replace("`", "")
        
        if match.group(4) is not None:
            self.__load_tags(match.group(4))

        for item in task.title.split(" "):
            if item.startswith("@"):
                task.key = item[1:]
            elif item.startswith("#"):
                task.key = item[1:]
                task.link_type = Task.Types.VISITABLE_URL

        #remove last non alfa char from key
        allowed = "0123456789_abcdefghijklmnopqrstuvwxyz-ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        key = ""
        for c in task.key:
            if c in allowed:
                key += c
            else:
                break
        task.key = key

        link = match.group(3).strip()
        self.select_link_type(link)
        
        if task.key == "":
            task.key = link
        return task
    
    def select_link_type(self, link: str):
        task = self.task
        task.link = link

        if task.link_type == Task.Types.VISITABLE_URL:
            # open both url and files
            return

        if self.task.key == "":
            raise Warning(f"Chave não definida para tarefa: {link}")

        if link.startswith("http:") or link.startswith("https:"):
            task.set_folder(os.path.join(self.database_folder, task.key))
            task.link_type = Task.Types.IMPORT_REMOTE
            return

        if not os.path.isabs(link):
            basedir = os.path.dirname(self.index_path)
            link = os.path.join(basedir, link)
            task.link = link
        # verify if file exists
        # update link using index_path to update de relative path
        if not os.path.isfile(link):
            raise Warning(f"Arquivo não encontrado: {link}")

        # verify if file is inside database_folder/folder
        task_folder = os.path.abspath(os.path.join(self.database_folder, task.key))
        task.set_folder(task_folder)
        if link.startswith(task_folder):
            task.link_type = Task.Types.STATIC_FOLDER
            return
        
        task.link_type = Task.Types.IMPORT_FOLDER
        return
