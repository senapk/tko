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

        self.default_min_value = 7 # default min grade to complete task


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
    
    def is_downloadable(self):
        return self.downloadable

    def is_downloaded_for_lang(self, rep_dir: str, lang: str) -> bool:
        folder = os.path.join(rep_dir, self.key)
        if not os.path.isfile(os.path.join(folder, "Readme.md")):
            return False
        files = os.listdir(folder)
        if not any([f.endswith("." + lang) for f in files]):
            return False
        return True

"""
- [ ] qq coisa [@label_opcional complemento] <!-- tags opcionais -->

se tem arroba, então é baixável?
pra ser baixável tem que ter label
coisas não baixáveis, tem um link e o link pode ser a

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
        task.link = match.group(3).strip()
        if match.group(4) is not None:
            TaskParser.__load_tags(task, match.group(3))
        
        for item in task.title.split(" "):
            if item.startswith("@"):
                task.key = item[1:]
                task.downloadable = True
        if task.key == "":
            task.key = task.link

        return task