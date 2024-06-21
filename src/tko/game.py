#!/usr/bin/env python3

import subprocess
import re
import os
from .format import symbols, colour
from typing import List, Dict, Tuple, Optional

class RE:
    @staticmethod
    def load_html_tags(task: str) -> Optional[str]:
        pattern = r"<!--\s*(.*?)\s*-->"
        match = re.search(pattern, task)
        if not match:
            return None
        return match.group(1).strip()

class Task:

    def __init__(self):
        self.line_number = 0
        self.line = ""
        self.key = ""
        self.grade: int = 0 #valor de 0 a 10

        self.qskills: Dict[str, int] = {} # default quest skills
        self.skills: Dict[str, int] = {} # local skills
        self.xp: int = 0
        
        self.opt: bool = False
        self.title = ""
        self.link = ""

        self.default_min_value = 7 # default min grade to complete task

    def get_grade_color(self, min_value: Optional[int] = None) -> str:
        if min_value is None:
            min_value = self.default_min_value
        if self.grade == 0:
            return "m"
        if self.grade < min_value:
            return "r"
        if self.grade < 10:
            return "y"
        if self.grade == 10:
            return "g"
        return "w"  

    def get_grade_symbol(self, min_value: Optional[int] = None) -> str:
        if min_value is None:
            min_value = self.default_min_value
        color = self.get_grade_color(min_value)
        if self.grade == 0:
            return colour("*," + color, symbols.uncheck)
        if self.grade < min_value:
            return colour("*," + color, str(self.grade))
        if self.grade < 10:
            return colour("*," + color, str(self.grade))
        if self.grade == 10:
            return colour("*," + color, symbols.check)
        return "0"

    def get_percent(self):
        if self.grade == 0:
            return 0
        if self.grade == 10:
            return 100
        return self.grade * 10
    
    def is_complete(self):
        return self.grade == 10

    def not_started(self):
        return self.grade == 0
    
    def in_progress(self):
        return self.grade > 0 and self.grade < 10

    def set_grade(self, grade: int):
        grade = int(grade)
        if grade >= 0 and grade <= 10:
            self.grade = grade
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
        return f"{line}    {self.grade} {key}{self.title} {self.skills} {self.link}"

class TaskParser:

    @staticmethod
    def load_html_tags(task: Task):                   
        pattern = r"<!--\s*(.*?)\s*-->"
        match = re.search(pattern, task.line)
        if not match:
            return

        tags_raw = match.group(1).strip()
        tags = [tag.strip() for tag in tags_raw.split(" ")]
        task.opt = "opt" in tags
        for t in tags:
            if t.startswith("+"):
                key, value = t[1:].split(":")
                task.skills[key] = int(value)
            elif t.startswith("@"):
                task.key = t[1:]

    @staticmethod
    def parse_item_with_link(line) -> Tuple[bool, str, str]:
        pattern = r"\ *-.*\[(.*?)\]\((.+?)\)"
        match = re.match(pattern, line)
        if match:
            return True, match.group(1), match.group(2)
        return False, "", ""
    
    @staticmethod
    def parse_task_with_link(line) -> Tuple[bool, str, str]:
        pattern = r"\ *- \[ \].*\[(.*?)\]\((.+?)\)"
        match = re.match(pattern, line)
        if match:
            return True, match.group(1), match.group(2)
        return False, "", ""

    @staticmethod
    def parse_arroba_from_title_link(titulo, link) -> Tuple[bool, str]:
        pattern = r".*?@(\w*)"
        match = re.match(pattern, titulo)
        if not match:
            return False, ""
        key = match.group(1)
        if not (key + "/Readme.md") in link:
            return False, ""
        return True, key


    # - [Titulo com @palavra em algum lugar](link/@palavra/Readme.md) <!-- tag1 tag2 tag3 -->
    @staticmethod
    def parse_coding_task(line, line_num) -> Optional[Task]:
        if line == "":
            return None
        line = line.lstrip()

        found, titulo, link = TaskParser.parse_item_with_link(line)
        if not found:
            return None
        found, key = TaskParser.parse_arroba_from_title_link(titulo, link)
        if not found:
            return None

        task = Task()

        task.line = line
        task.line_number = line_num
        task.key = key
        task.title = titulo
        task.link = link
        TaskParser.load_html_tags(task)

        return task

    # se com - [ ], não precisa das tags dentro do html, o key será dado pelo título
    # se tiver as tags dentro do html, se alguma começar com @, o key será dado por ela
    # - [ ] [Título](link)
    # - [ ] [Título](link) <!-- tag1 tag2 tag3 -->
    # - [Título](link) <!-- tag1 tag2 tag3 -->
    @staticmethod
    def parse_reading_task(line, line_num) -> Optional[Task]:
        if line == "":
            return None
        line = line.lstrip()

        found, titulo, link = TaskParser.parse_task_with_link(line)

        if found:
            task = Task()
            task.key = link
            task.title = titulo
            task.link = link
            task.line = line
            task.line_number = line_num
            TaskParser.load_html_tags(task)
            return task
        

        task = Task()
        found, titulo, link = TaskParser.parse_item_with_link(line)
        task.key = ""
        if found:
            task.link = link
            task.line = line
            task.line_number = line_num
            TaskParser.load_html_tags(task)
            if task.key == "": # item with links needs a key
                return None
            task.title = titulo
            return task

        return None

class Quest:
    def __init__(self):
        self.line_number = 0
        self.line = ""
        self.key = ""
        self.title = ""
        self.__tasks: List[Task] = []
        self.skills: Dict[str, int] = {} # s:skill
        self.cluster = ""
        self.requires = [] # r:quest_key
        self.requires_ptr = []
        self.opt = False # opt
        self.qmin: Optional[int] = None # q:  minimo de 50 porcento da pontuação total para completar
        self.tmin: Optional[int] = None  # t: ou ter no mínimo esse valor de todas as tarefas

    def __str__(self):
        line = str(self.line_number).rjust(3)
        tasks_size = str(len(self.__tasks)).rjust(2, "0")
        key = "" if self.key == self.title else self.key + " "
        output = f"{line} {tasks_size} {key}{self.title} {self.skills} {self.requires}"
        return output

    def get_resume_by_percent(self) -> str:
        value = self.get_percent()
        return colour(self.get_grade_color() + ",*", str(value)) + "%"
    
    def get_requirement(self):
        if self.qmin is not None:
            return colour("y", f"[{self.qmin}%]")
        if self.tmin is not None:
            return colour("y", f"[t>{self.tmin - 1}]")
        return ""

    def get_resume_by_tasks(self) -> str:
        tmin = self.tmin if self.tmin is not None else 7
        total = len([t for t in self.__tasks if not t.opt])
        plus = len([t for t in self.__tasks if t.opt])
        count = len([t for t in self.__tasks if t.grade >= tmin])
        output = f"{count}/{total}"
        if plus > 0:
            output += f"+{plus}"
        return "(" + colour(self.get_grade_color()+",*", output) + ")"

    def get_grade_color(self) -> str:
        if self.not_started():
            return "magenta"
        if not self.is_complete():
            return "red"
        if self.get_percent() == 100:
            return "green"
        return "yellow"

    def is_complete(self):
        if self.qmin is not None:
            return self.get_percent() >= self.qmin
        # task complete mode
        if self.tmin is not None:
            for t in self.__tasks:
                if not t.opt and t.grade < self.tmin:
                    return False
        return True

    def add_task(self, task: Task, filename: str):
        if self.qmin is not None:
            if task.opt:
                print(f"Quests com requerimento de porcentagem não deve ter Tasks opcionais")
                print(f"{filename}:{task.line_number} {task.key}")
                exit(1)
        task.qskills = self.skills

        task.xp = 0
        for s in task.skills:
            task.xp += task.skills[s]

        for s in task.qskills:
            task.xp += task.qskills[s]
        
        self.__tasks.append(task)

    def get_tasks(self):
        return self.__tasks

    def get_xp(self) -> Tuple[int, int]:
        total = 0
        obtained = 0
        for t in self.__tasks:
            total += t.xp
            if t.grade > 0:
                obtained += t.xp * t.grade // 10

        return obtained, total
        
    def get_percent(self):
        obtained, total = self.get_xp()
        if total == 0:
            return 0
        return obtained * 100 // total

    def in_progress(self):
        if self.is_complete():
            return False
        for t in self.__tasks:
            if t.grade != 0:
                return True
        return False

    def not_started(self):
        if self.is_complete():
            return False
        if self.in_progress():
            return False
        return True

    def is_reachable(self, cache: Dict[str, bool]):
        if self.key in cache:
            return cache[self.key]

        if len(self.requires_ptr) == 0:
            cache[self.key] = True
            return True
        cache[self.key] = all( [r.is_complete() and r.is_reachable(cache) for r in self.requires_ptr] )
        return cache[self.key]
    
class QuestParser:
    quest: Quest

    def __init__(self):
        self.quest = Quest()
        self.line = ""
        self.line_num = 0
        self.default_qmin_requirement = 50
        self.default_task_xp = 10

    def finish_quest(self) -> Quest:

        if self.quest.key == "":
            self.quest.key = get_md_link(self.quest.title)

        if len(self.quest.skills) == 0:
            self.quest.skills["xp"] = self.default_task_xp
        
        if self.quest.qmin is None and self.quest.tmin is None:
            self.quest.qmin = self.default_qmin_requirement

        return self.quest

    def match_full_pattern(self):
        fullpattern = r"^#+\s*(.*?)<!--\s*(.*?)\s*-->.*$"
        match = re.match(fullpattern, self.line)
        tags = []

        if not match:
            return False
        self.quest.title = match.group(1).strip()
        tags_raw = match.group(2).strip()
        tags = [tag.strip() for tag in tags_raw.split()]

        # key
        keys = [t[1:] for t in tags if t.startswith("@")]
        if len(keys) > 0:
            self.quest.key = keys[0]

        # skills
        skills = [t[1:] for t in tags if t.startswith("+")]
        if len(skills) > 0:
            self.quest.skills = {}
            for s in skills:
                k, v = s.split(":")
                self.quest.skills[k] = int(v)
        # requires
        self.quest.requires = [t[2:] for t in tags if t.startswith("r:")]

        self.quest.opt = "opt" in tags
        # type
        # try:
        #     self.quest.type = [t[1:] for t in tags if t.startswith("#")][0]
        # except:
        #     self.quest.type = "main"
        
        # quest percent
        qmin = [t[2:] for t in tags if t.startswith("q:")]
        
        if len(qmin) > 0:
            self.quest.qmin = int(qmin[0])

        # task min value requirement
        tmin = [t[2:] for t in tags if t.startswith("t:")]
        if len(tmin) > 0:
            self.quest.tmin = int(tmin[0])
            if self.quest.tmin > 10:
                print("fail: tmin > 10")
                exit(1)
        return True

    def __match_minimal_pattern(self):
        minipattern = r"^#+\s*(.*?)\s*$"
        match = re.match(minipattern, self.line)
        if match:
            self.quest.title = match.group(1).strip()
            return True
        return False

    def parse_quest(self, filename, line, line_num) -> Optional[Quest]:
        self.line = line
        self.line_num = line_num
        self.filename = filename

        self.quest.line = self.line
        self.quest.line_number = self.line_num
        self.quest.cluster = ""

        if self.match_full_pattern():
            return self.finish_quest()
        
        if self.__match_minimal_pattern():
            return self.finish_quest()
        
        return None

class Cluster:
    def __init__(self, line_number:int = 0, title: str = "", key: str = "", color: Optional[str] = None):
        self.line_number = line_number
        self.title: str = title
        self.key: str = key
        self.quests: List[Quest] = []
        self.color: Optional[str] = color

    def __str__(self):
        line = str(self.line_number).rjust(3)
        quests_size = str(len(self.quests)).rjust(2, "0")
        key = "" if self.key == self.title else self.key + " "
        return f"{line} {quests_size} {key}{self.title}"
    
    def get_grade_color(self) -> str:
        perc = self.get_percent()
        if perc == 0:
            return "m"
        if perc < 50:
            return "r"
        if perc < 100:
            return "y"
        return "g"

    def get_percent(self):
        total = 0
        for q in self.quests:
            total += q.get_percent()
        return total // len(self.quests)

    def get_resume_by_percent(self) -> str:
        return colour(self.get_grade_color() + ",*", f"{self.get_percent()}%")

    def get_resume_by_quests(self):
        total = len(self.quests)
        count = len([q for q in self.quests if q.is_complete()])
        return f"({count}/{total})"
        

# def rm_comments(title: str) -> str:
#     if "<!--" in title and "-->" in title:
#         title = title.split("<!--")[0] + title.split("-->")[1]
#     return title


def get_md_link(title: str) -> str:
    if title is None:
        return ""
    title = title.lower()
    out = ""
    for c in title:
        if c == " " or c == "-":
            out += "-"
        elif c == "_":
            out += "_"
        elif c.isalnum():
            out += c
    return out


class XP:
    token_level_one = "level_one"
    token_level_mult = "level_mult"
    level_one: int = 100
    level_mult: float = 1.5
    
    @staticmethod
    def get_level(xp: int) -> int:
        level = 1
        while XP.get_xp(level) <= xp:
            level += 1
        return level - 1
    
    @staticmethod
    def get_xp(level: int) -> int:
        total = 0
        for i in range(level - 1):
            total += XP.level_one * (XP.level_mult ** i)
        return int(total)

    @staticmethod
    def parse_settings(line: str):
        values = RE.load_html_tags(line)
        if values is not None:
            tags = values.split(" ")
            for t in tags:
                if t.startswith(XP.token_level_one):
                    XP.level_one = int(t.split(":")[1])
                if t.startswith(XP.token_level_mult):
                    XP.level_mult = float(t.split(":")[1])


class Game:
    def __init__(self, file: Optional[str] = None):
        self.clusters: List[Cluster] = []  # clusters ordered
        self.quests: Dict[str, Quest] = {}  # quests indexed by quest key
        self.tasks: Dict[str, Task] = {}  # tasks indexed by task key
        self.filename = None
        if file is not None:
            self.filename = file
            self.parse_file(file)

    def get_task(self, key: str) -> Task:
        if key in self.tasks:
            return self.tasks[key]
        raise Exception(f"fail: task {key} not found in course definition")

    # se existir um cluster nessa linha, insere na lista de clusters e 
    # retorno o objeto cluster inserido
    def load_cluster(self, line: str, line_num: int) -> Optional[Cluster]:
        pattern = r"^#+\s*(.*?)<!--\s*(.*?)\s*-->\s*$"
        match = re.match(pattern, line)
        if not match:
            return None
        titulo = match.group(1)
        tags_raw = match.group(2).strip()
        tags = [tag.strip() for tag in tags_raw.split(" ")]
        if not "group" in tags:
            return None
        
        keys = [tag[1:] for tag in tags if tag.startswith("@")]
        key = titulo
        try:
            color = [tag[2:] for tag in tags if tag.startswith("c:")][0]
        except:
            color = None
        if len(keys) > 0:
            key = keys[0]
        
        cluster = Cluster(line_num, titulo, key, color)

        # search for existing cluster in self.clusters
        for c in self.clusters:
            if c.key == key:
                print(f"Cluster {key} já existe")
                print(f"{self.filename}:{line_num}")
                print(f"{self.filename}:{c.line_number}")
                print("  " + str(c))
                print("  " + str(cluster))
                exit(1)
                
        self.clusters.append(cluster)
        return cluster
                
    def load_quest(self, line, line_num) -> Optional[Quest]:
        quest = QuestParser().parse_quest(self.filename, line, line_num + 1)
        if quest is None:
            return None
        if quest.key in self.quests:
            print(f"Quest {quest.key} já existe")
            print(f"{self.filename}:{quest.line_number}")
            print(f"{self.filename}:{self.quests[quest.key].line_number}")
            print("  " + str(quest))
            print("  " + str(self.quests[quest.key]))
            exit(1)
        self.quests[quest.key] = quest
        return quest

    def load_task(self, line, line_num) -> Optional[Task]:
        if line == "":
            return None
        task = TaskParser.parse_reading_task(line, line_num + 1)
        if task is None:
            task = TaskParser.parse_coding_task(line, line_num + 1)
        if task is None:
            return None
        
        if task.key in self.tasks:
            print(f"Task {task.key} já existe")
            print(f"{self.filename}:{task.line_number}")
            print(f"{self.filename}:{self.tasks[task.key].line_number}")
            print("  " + str(task))
            print("  " + str(self.tasks[task.key]))
            exit(1)
        self.tasks[task.key] = task
        return task

    def get_xp_resume(self):
        total = 0
        obtained = 0
        for q in self.quests.values():
            o, t = q.get_xp()
            total += t
            obtained += o
        return obtained, total

    def get_skills_resume(self) -> Dict[str, int]:
        skills: Dict[str, int] = {}
        for q in self.quests.values():
            for t in q.get_tasks():
                if t.grade > 0:
                    for s in t.skills:
                        if s in skills:
                            skills[s] += t.skills[s]
                        else:
                            skills[s] = t.skills[s]
                    for s in t.qskills:
                        if s in skills:
                            skills[s] += t.qskills[s]
                        else:
                            skills[s] = t.qskills[s]
        return skills

    # Verificar se todas as quests requeridas existem e adiciona o ponteiro
    # Verifica se todas as quests tem tarefas
    def validate_requirements(self):

        # verify is there are keys repeated between quests, tasks and groups

        keys = [c.key for c in self.clusters] +\
               [k for k in self.quests.keys()] +\
               [k for k in self.tasks.keys()]

        # print chaves repetidas
        for k in keys:
            if keys.count(k) > 1:
                print(f"Chave repetida: {k}")
                exit(1)

        # remove all quests without tasks
        valid_quests = {}
        for k, q in self.quests.items():
            if len(q.get_tasks()) > 0:
                valid_quests[k] = q

        self.quests = valid_quests

        # verificar se todas as quests requeridas existem e adicionar o ponteiro
        for q in self.quests.values():
            for r in q.requires:
                if r in self.quests:
                    q.requires_ptr.append(self.quests[r])
                else:
                    # print(f"keys: {self.quests.keys()}")
                    print(f"Quest\n{self.filename}:{q.line_number}\n{str(q)}\nrequer {r} que não existe")
                    exit(1)

    def check_cycle(self):
        def dfs(qx, visitedx):
            if len(visitedx) > 0:
                if visitedx[0] == qx.key:
                    print(f"Cycle detected: {visitedx}")
                    exit(1)
            if q.key in visitedx:
                return
            visitedx.append(q.key)
            for r in q.requires_ptr:
                dfs(r, visitedx)

        for q in self.quests.values():
            visited: List[str] = []
            dfs(q, visited)

    def parse_file(self, file):
        self.filename = file
        lines = open(file, encoding="utf-8").read().split("\n")
        active_quest = None
        active_cluster = None

        if len(lines) > 0:
            XP.parse_settings(lines[0])


        for line_num, line in enumerate(lines):
            cluster = self.load_cluster(line, line_num)
            if cluster is not None:
                active_cluster = cluster
                continue
            
            quest = self.load_quest(line, line_num)
            if quest is not None:
                active_quest = quest
                if active_cluster is None:
                    self.clusters.append(Cluster(0, "Sem grupo", "Sem grupo"))
                    active_cluster = self.clusters[-1]
                quest.cluster = active_cluster.key
                active_cluster.quests.append(quest)
                continue

            task = self.load_task(line, line_num)
            if task is not None:
                
                if active_quest is None:
                    print(f"Task {task.key} não está dentro de uma quest")
                    print(f"{file}:{task.line_number}")
                    print(f"  {task}")
                    exit(1)
                if self.filename is not None:
                    active_quest.add_task(task, self.filename)

        self.clear_empty()

        self.validate_requirements()
        for t in self.tasks.values():
            t.process_link(os.path.dirname(file) + "/")

    def clear_empty(self):

        # apagando quests vazias da lista de quests
        for k in list(self.quests.keys()):
            if len(self.quests[k].get_tasks()) == 0:
                del self.quests[k]

        # apagando quests vazias dos clusters e clusters vazios
        clusters = []
        for c in self.clusters:
            quests = [q for q in c.quests if len(q.get_tasks()) > 0]
            if len(quests) > 0:
                c.quests = quests
                clusters.append(c)
        self.clusters = clusters

    def get_reachable_quests(self):
        # cache needs to be reseted before each call
        cache: Dict[str, bool] = {}
        return [q for q in self.quests.values() if q.is_reachable(cache)]

    def __str__(self):
        output = []
        for c in self.clusters:
            output.append(str(c))
            for q in c.quests:
                output.append(str(q))
                for t in q.get_tasks():
                    output.append(str(t))
        return "\n".join(output)


class Graph:

    colorlist: List[Tuple[str, str]] = [
            ("aquamarine3","aquamarine4"),
            ("bisque3","bisque4"),
            ("brown3","brown4"),
            ("chartreuse3","chartreuse4"),
            ("coral3","coral4"),
            ("cyan3","cyan4"),
            ("darkgoldenrod3","darkgoldenrod4"),
            ("darkolivegreen3","darkolivegreen4"),
            ("darkorchid3","darkorchid4"),
            ("darkseagreen3","darkseagreen4"),
            ("darkslategray3","darkslategray4"),
            ("deeppink3","deeppink4"),
            ("deepskyblue3","deepskyblue4"),
            ("dodgerblue3","dodgerblue4"),
            ("firebrick3","firebrick4"),
            ("gold3","gold4"),
            ("green3","green4"),
            ("hotpink3","hotpink4"),
            ("indianred3","indianred4"),
            ("khaki3","khaki4"),
            ("lightblue3","lightblue4"),
            ("lightcoral","lightcoral"),
            ("lightcyan3","lightcyan4"),
            ("lightgoldenrod3","lightgoldenrod4"),
            ("lightgreen","lightgreen"),
            ("lightpink3","lightpink4"),
            ("lightsalmon3","lightsalmon4"),
            ("lightseagreen","lightseagreen"),
            ("lightskyblue3","lightskyblue4"),
            ("lightsteelblue3","lightsteelblue4"),
            ("lightyellow3","lightyellow4"),
            ("magenta3","magenta4"),
            ("maroon3","maroon4"),
            ("mediumorchid3","mediumorchid4"),
            ("mediumpurple3","mediumpurple4"),
            ("mediumspringgreen","mediumspringgreen"),
            ("mediumturquoise","mediumturquoise"),
            ("mediumvioletred","mediumvioletred"),
            ("mistyrose3","mistyrose4"),
            ("navajowhite3","navajowhite4"),
            ("olivedrab3","olivedrab4"),
            ("orange3","orange4"),
            ("orangered3","orangered4"),
            ("orchid3","orchid4"),
            ("palegreen3","palegreen4"),
            ("paleturquoise3","paleturquoise4"),
            ("palevioletred3","palevioletred4")
            ]

    def __init__(self, game: Game):
        self.game = game
        self.reachable: Optional[List[str]] = None
        self.counts: Optional[Dict[str, str]] = None
        self.graph_ext = ".png"
        self.output = "graph"
        self.opt = False

    def set_opt(self, opt: bool):
        self.opt = opt
        return self

    def set_reachable(self, reachable: List[str]):
        self.reachable = reachable
        return self

    def set_counts(self, counts: Dict[str, str]):
        self.counts = counts
        return self

    def set_graph_ext(self, graph_ext: str):
        self.graph_ext = graph_ext
        return self
    
    def set_output(self, output: str):
        self.output = output
        return self

    def info(self, qx: Quest):
        text = f'{qx.title.strip()}'
        if self.reachable is None or self.counts is None:
            return f'"{text}"'
        return f'"{text}\\n{self.counts[qx.key]}"'


    def is_reachable_or_next(self, q: Quest):
        if self.reachable is None:
            return True
        if q.key in self.reachable:
            return True
        for r in q.requires_ptr:
            if r.key in self.reachable:
                return True
        return False

    def generate(self):
        saida = ["digraph diag {", '  node [penwidth=1, style="rounded,filled", shape=box]']

        targets = [q for q in self.game.quests.values() if self.is_reachable_or_next(q)]
        for q in targets:
            token = "->"
            if len(q.requires_ptr) > 0:
                for r in q.requires_ptr:
                    extra = ""
                    if self.reachable is not None:
                        if q.key not in self.reachable and not r.is_complete():
                            extra = "[style=dotted]"
                    saida.append(f"  {self.info(r)} {token} {self.info(q)} {extra}")
            else:
                v = '  "Início"'
                saida.append(f"{v} {token} {self.info(q)}")

        for i, c in enumerate(self.game.clusters):
            cluster_targets = [q for q in c.quests if self.is_reachable_or_next(q)]
            for q in cluster_targets:
                if self.opt:
                    if q.opt:
                        fillcolor = "pink"
                    else:
                        fillcolor = "lime"
                else:
                    if c.color is not None:
                        fillcolor = c.color
                    else:
                        fillcolor = self.colorlist[i][0]

                    if q.opt:
                        fillcolor = f'"{fillcolor};0.9:orange"'
                    else:
                        fillcolor = f'"{fillcolor};0.9:lime"'
                shape = "ellipse"
                color = "black"
                width = 1
                if self.reachable is not None:
                    if q.key not in self.reachable:
                        color = "white"
                    else:
                        width = 3
                        color = q.get_grade_color()
                saida.append(f"  {self.info(q)} [shape={shape} color={color} penwidth={width} fillcolor={fillcolor} ]")

        saida.append("}")
        # saida.append("@enduml")
        saida.append("")

        dot_file = self.output + ".dot"
        out_file = self.output + self.graph_ext
        open(dot_file, "w").write("\n".join(saida))

        if self.graph_ext == ".png":
            subprocess.run(["dot", "-Tpng", dot_file, "-o", out_file])
        elif self.graph_ext == ".svg":
            subprocess.run(["dot", "-Tsvg", dot_file, "-o", out_file])
        else:
            print("Formato de imagem não suportado")
