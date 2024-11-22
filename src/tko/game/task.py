from typing import Dict, Optional, Tuple
from tko.util.symbols import symbols
from tko.util.text import Text
from tko.game.tree_item import TreeItem
from tko.util.get_md_link import get_md_link
import re
import os

class TaskTypes:
    visitable_url = 0 # task link to url 
    select_folder = 1 # task link to a [file|folder] and remote to [local file|none]
    down_from_url = 2 # task link to url
    down_from_dir = 3 # task link to a [file] and remote as file outside folder


class Task(TreeItem):

    def __init__(self):
        super().__init__()
        self.line_number = 0
        self.line = ""

        self.self_grade: int = 0 #valor de 0 a 9
        self.progress: int = 0 #valor de 0 a 100
        self.main_index: int = 0

        self.qskills: Dict[str, int] = {} # default quest skills
        self.skills: Dict[str, int] = {} # local skills
        self.xp: int = 0

        self.opt: bool = False
        self.visit: bool = False
        self.local: bool = False

        self.download_link: str = ""
        self.visitable_url: str = ""

        self.quest_key = ""
        self.cluster_key = ""

        self.folder: str | None = None
        self.track_folder: str | None = None

        self.default_min_value = 7 # default min grade to complete task

    def set_folder(self, folder: str):
        self.folder = folder
        return self
    
    def get_folder(self) -> str | None:
        return self.folder
    
    def set_track_folder(self, folder: str):
        self.track_folder = folder
        return self
    
    def get_track_folder(self) -> str | None:
        return self.track_folder

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
        prog = self.progress // 10
        if prog == 0:
            return Text().addf(color, "0")
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

    def set_progress(self, progress: int):
        progress = int(progress)
        if progress >= 0 and progress <= 100:
            self.progress = progress
        else:
            print(f"Progresso inválido: {progress}")

    def set_grade(self, grade: int):
        grade = int(grade)
        if grade >= 0 and grade <= 10:
            self.self_grade = grade
        else:
            print(f"Grade inválida: {grade}")

    def get_download_link(self) -> str:
        return self.download_link

    def get_visitable_url(self) -> str:
        return self.visitable_url

    def __str__(self):
        lnum = str(self.line_number).rjust(3)
        key = "" if self.key == self.title else self.key + " "
        return f"{lnum} grade:{self.self_grade} key:{key} title:{self.title} skills:{self.skills} down:{self.download_link} vis:{self.visitable_url}"

    def has_at_symbol(self):
        return any([s.startswith("@") for s in self.title.split(" ")])

    def is_downloaded_for_lang(self, lang: str) -> bool:
        if self.folder is None or not os.path.isdir(self.folder):
            return False
        files = os.listdir(self.folder)
        if not any([f.endswith("." + lang) for f in files]):
            return False
        return True

"""
down_from_url = 2 # task link to url
down_from_dir = 3 # task link to a [file] and remote as file outside folder
visitable_url = 0 # task link to url 
select_folder = 1 # task link to a [file|folder] and remote to [local file|none]

----------

Usar @ para definir a chave da tarefa
Pode ser incluído no título da tarefa que está entre os [] ou nas tags url
Exemplo:
- [ ] [@banana Título da tarefa](https://tal_coias/Readme.md) 
Chave: "banana"
Título: "@banana Título da tarefa"
link: "https://tal_coias/Readme.md"

----------
Se a flag visit estiver no html a tarefa será para ser visitada apenas
Exemplo:
- [ ] [@banana Título da tarefa](https://tal_coias/Readme.md) <!-- visit -->

----------
Se o link for um arquivo ou pasta
- [ ] [@banana Título da tarefa](tal_coias/Readme.md)



"""
class TaskParser:

    def __init__(self, index_path: str):
        self.index_path = index_path
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
                task.visit = True
                task.key = item[1:]
            elif item.startswith("!"):
                task.local = True
                task.key = item[1:]

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
        self.adjust_links(link)
        
        if task.key == "":
            task.key = link
        return task
    
    def adjust_links(self, link: str):
        task = self.task
        if task.visit:
            task.visitable_url = link
            task.download_link = ""
            return
        
        if task.local:
            dirname = os.path.dirname(self.index_path)
            task.folder = os.path.dirname(os.path.abspath(os.path.join(dirname, link)))
            task.download_link = ""
            task.visitable_url = ""
            return

        if link.startswith("http") and self.task.key != "":
            task.download_link = link
            task.visitable_url = link
            return
        
        # downloadable task from a file in filesystem
        basedir = os.path.dirname(self.index_path)
        task.download_link = os.path.join(basedir, link)
        task.visitable_url = ""