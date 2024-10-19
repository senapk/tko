from typing import Dict, Optional, Tuple
from tko.util.symbols import symbols
from tko.util.text import Text
# from tko.util.logger import Logger, LogAction
from tko.game.tree_item import TreeItem
import re
import os

class Task(TreeItem):

    def __init__(self):
        super().__init__()
        self.line_number = 0
        self.line = ""
        self.downloadable = False
        self.self_grade: int = 0 #valor de 0 a 9
        self.progress: int = 0 #valor de 0 a 100
        self.main_index: int = 0

        self.qskills: Dict[str, int] = {} # default quest skills
        self.skills: Dict[str, int] = {} # local skills
        self.xp: int = 0
        
        self.opt: bool = False
        self.link: str = ""

        self.quest_key = ""
        self.cluster_key = ""
        self.folder: str = ""

        self.default_min_value = 7 # default min grade to complete task

    def set_folder(self, folder: str):
        self.folder = folder
        return self

    def load_from_db(self, value: str):
        if ":" not in value:
            self.self_grade = int(value)
        else:
            v = value.split(":")
            if len(v) == 3:
                self.self_grade = int(v[0])
                self.main_index = int(v[1])
                self.progress = int(v[2])

    def save_to_db(self) -> str:
        return f"{self.self_grade}:{self.main_index}:{self.progress}"
    
    def is_db_empty(self) -> bool:
        return self.self_grade == 0 and self.main_index == 0 and self.progress == 0

    def get_prog_color(self, min_value: Optional[int] = None) -> str:
        if min_value is None:
            min_value = self.default_min_value
        prog = self.progress // 10
        if prog == 0:
            return "m"
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
        prog = self.progress // 10
        if prog == 0:
            return Text().addf(color, symbols.uncheck.text)
        if prog < min_value:
            return Text().addf(color, str(prog))
        if prog < 10:
            return Text().addf(color, str(prog))
        if prog == 10:
            return Text().addf(color, symbols.check.text)
        return Text().add("0")

    def get_percent(self):
        if self.self_grade == 0:
            return 0
        if self.self_grade == 10:
            return 100
        return self.self_grade * 10
    
    def is_complete(self):
        return self.self_grade == 10

    def not_started(self):
        return self.self_grade == 0
    
    def in_progress(self):
        return self.self_grade > 0 and self.self_grade < 10

    def set_grade(self, grade: int):
        grade = int(grade)
        if grade >= 0 and grade <= 10:
            if grade != self.self_grade:
                self.self_grade = grade
        else:
            print(f"Grade inválida: {grade}")
    
    def process_link(self, base_file):
        if self.link.startswith("http"):
            return
        if self.link.startswith("./"):
            self.link = self.link[2:]
        # todo trocar / por \\ se windows
        self.link = base_file + self.link

    def __str__(self):
        line = str(self.line_number).rjust(3)
        key = "" if self.key == self.title else self.key + " "
        return f"{line}    {self.self_grade} {key}{self.title} {self.skills} {self.link}"
    
    def has_remote_link(self):
        return self.link.startswith("http:") or self.link.startswith("https:")

    def has_at_symbol(self):
        return any([s.startswith("@") for s in self.title.split(" ")])

    def is_downloadable(self):
        return self.downloadable

    def is_downloaded_for_lang(self, task_dir: str, lang: str) -> bool:
        if not os.path.isfile(os.path.join(task_dir, "Readme.md")):
            return False
        files = os.listdir(task_dir)
        if not any([f.endswith("." + lang) for f in files]):
            return False
        return True

"""
Usar @ ou # para definir a chave da tarefa
Pode ser incluído no título da tarefa que está entre os [] ou nas tags url
Exemplo:
- [ ] [@banana Título da tarefa](https://tal_coias/Readme.md) 
Chave: "banana"
Título: "@banana Título da tarefa"
link: "https://tal_coias/Readme.md"
É uma tarefa de download

----------
Nessas tarefas que não serão baixadas para o repositório, se não for inserido o #, será utilizado como chave o link da tarefa
- [ ] [#banana Título da tarefa](https://tal_coias/Readme.md)
Chave: "banana"
Título: "#banana Título da tarefa"
link: "https://tal_coias/Readme.md"


"""
class TaskParser:

    @staticmethod
    def __load_tags(task: Task, tags_raw: str):
        tags = [tag.strip() for tag in tags_raw.split(" ")]
        task.opt = "opt" in tags
        for t in tags:
            if t.startswith("+"):
                key, value = t[1:].split(":")
                task.skills[key] = int(value)
            elif t.startswith("@"):
                task.key = t[1:]
                task.downloadable = True
            elif t.startswith("#"):
                task.key = t[1:]

    @staticmethod
    def parse_line(line: str, line_num: int) -> Optional[Task]:
        pattern = r'\s*?- \[ \](.*?)\[([^\]]+)\]\(([^)]+)\)(?:\s*<!--(.*?)-->)?'

        match = re.match(pattern, line)
        if match is None:
            return None
        task = Task()
        task.line_number = line_num
        task.line = line
        task.opt = False
        task.title = match.group(1).strip()
        if task.title != "":
            task.title += " "
        task.title += match.group(2).strip()
        task.title = task.title.replace("`", "")
        task.link = match.group(3).strip()
        if match.group(4) is not None:
            TaskParser.__load_tags(task, match.group(3))
        
        for item in task.title.split(" "):
            if item.startswith("@"):
                task.key = item[1:]
                task.downloadable = True
            if item.startswith("#"):
                task.key = item[1:]
        if task.key == "":
            task.key = task.link
        return task