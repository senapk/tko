#!/usr/bin/env python3

import subprocess
import re
from typing import Optional, Dict, List, Tuple
import os
from .format import symbols, colour, bold


class Task:
    def __init__(self):
        self.line_number = 0
        self.line = ""
        self.key = ""
        self.grade: int = 0 #valor de 0 a 10
        self.skills = []
        self.title = ""
        self.link = ""
        self.opt = False
        self.default_min_value = 7


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
            return bold(color, symbols.uncheck)
        if self.grade < min_value:
            return bold(color, str(self.grade))
        if self.grade < 10:
            return bold(color, str(self.grade))
        if self.grade == 10:
            return bold(color, symbols.check)


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

    def load_html_tags(self):                   
        pattern = r"<!--\s*(.*?)\s*-->"
        match = re.search(pattern, self.line)
        if not match:
            return

        tags_raw = match.group(1).strip()
        tags = [tag.strip() for tag in tags_raw.split(" ")]
        self.opt = "opt" in tags
        for t in tags:
            if t.startswith("s:"):
                self.skills.append(t[2:])
            elif t.startswith("@"):
                self.key = t[1:]

        
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

    def process_link(self, base_file):
        if self.link.startswith("http"):
            return
        if self.link.startswith("./"):
            self.link = self.link[2:]
        # todo trocar / por \\ se windows
        self.link = base_file + self.link

    # - [Titulo com @palavra em algum lugar](link/@palavra/Readme.md) <!-- tag1 tag2 tag3 -->
    def parse_coding_task(self, line, line_num):
        if line == "":
            return False
        line = line.lstrip()

        found, titulo, link = Task.parse_item_with_link(line)
        if not found:
            return False
        found, key = Task.parse_arroba_from_title_link(titulo, link)
        if not found:
            return False

        self.line = line
        self.line_number = line_num
        self.key = key
        self.title = titulo
        self.link = link

        self.load_html_tags()

        return True

    # se com - [ ], não precisa das tags dentro do html, o key será dado pelo título
    # se tiver as tags dentro do html, se alguma começar com @, o key será dado por ela
    # - [ ] [Título](link)
    # - [ ] [Título](link) <!-- tag1 tag2 tag3 -->
    # - [Título](link) <!-- tag1 tag2 tag3 -->
    def parse_reading_task(self, line, line_num):
        if line == "":
            return False
        line = line.lstrip()

        found, titulo, link = Task.parse_task_with_link(line)
        if found:
            self.key = link
            self.title = titulo
            self.link = link
            self.line = line
            self.line_number = line_num
            self.load_html_tags()
            return True
        
        found, titulo, link = Task.parse_item_with_link(line)
        self.key = ""
        if found:
            self.link = link
            self.line = line
            self.line_number = line_num
            self.load_html_tags()
            if self.key == "":
                return False
            self.title = titulo
            return True

        return False

    def __str__(self):
        line = str(self.line_number).rjust(3)
        key = "" if self.key == self.title else self.key + " "
        return f"{line}    {self.grade} {key}{self.title} {self.skills} {self.link}"

class Quest:
    def __init__(self):
        self.line_number = 0
        self.line = ""
        self.key = ""
        self.title = ""
        self.tasks: List[Task] = []
        self.skills: List[str] = [] # s:skill
        self.cluster = ""
        self.requires = [] # r:quest_key
        self.requires_ptr = []
        self.opt = False # opt
        self.qmin: Optional[int] = None # q:  minimo de 50 porcento da pontuação total para completar
        self.tmin: Optional[int] = None  # t: ou ter no mínimo esse valor de todas as tarefas

    def __str__(self):
        line = str(self.line_number).rjust(3)
        tasks_size = str(len(self.tasks)).rjust(2, "0")
        key = "" if self.key == self.title else self.key + " "
        output = f"{line}   {tasks_size} {key}{self.title} {self.skills} {self.requires}"
        return output

    def get_resume_by_percent(self) -> str:
        value = self.get_percent()
        ref = self.qmin if self.qmin is not None else 100
        if self.qmin is None:
            return bold("white", str(value) + "%")
        return bold(self.get_grade_color(), str(value)) + "%" + bold("w", "/") + bold("y", str(ref) ) + "%"

    def get_resume_by_tasks(self) -> str:
        tmin = self.tmin if self.tmin is not None else 7
        total = len([t for t in self.tasks if not t.opt])
        plus = len([t for t in self.tasks if t.opt])
        count = len([t for t in self.tasks if t.grade >= tmin])
        output = f"{count}/{total}"
        if plus > 0:
            output += f"+{plus}"
        if self.tmin is None:
            return "(" + bold("white", output) + ")"
        return "(" + bold(self.get_grade_color(), output) + ")"

    def get_grade_color(self) -> str:
        if self.not_started():
            return "m"
        if not self.is_complete():
            return "r"
        if self.get_percent() == 100:
            return "g"
        return "y"

    def is_complete(self):
        if self.qmin is not None:
            return self.is_complete_by_percent()
        if self.tmin is not None:
            return self.is_complete_by_tasks()
        return False

    def is_complete_by_percent(self):
        if self.qmin is None:
            return False
        return self.get_percent() >= self.qmin
    
    def is_complete_by_tasks(self):
        if self.tmin is None:
            return False
        for t in self.tasks:
            if not t.opt and t.grade < self.tmin:
                return False
        return True

    def get_percent(self):
        total = len(self.tasks)
        if total == 0:
            return 0
        done = sum([t.get_percent() for t in self.tasks])
        return done // total

    def in_progress(self):
        if self.is_complete():
            return False
        for t in self.tasks:
            if t.grade != 0:
                return True
        return False

    def not_started(self):
        if self.is_complete():
            return False
        if self.in_progress():
            return False
        return True

    def is_reachable(self, cache):
        if self.key in cache:
            return cache[self.key]

        if len(self.requires_ptr) == 0:
            cache[self.key] = True
            return True
        cache[self.key] = all(
            [r.is_complete() and r.is_reachable(cache) for r in self.requires_ptr]
        )
        return cache[self.key]

    def update_requirements(self):
        if self.qmin is None and self.tmin is None:
            self.qmin = 50

    def parse_quest(self, line, line_num):
        
        fullpattern = r"^#+\s*(.*?)<!--\s*(.*?)\s*-->\s*$"
        match = re.match(fullpattern, line)
        tags = []

        self.line = line
        self.line_number = line_num
        self.cluster = ""

        if match:
            self.title = match.group(1).strip()
            tags_raw = match.group(2).strip()
            tags = [tag.strip() for tag in tags_raw.split()]
            keys = [t[1:] for t in tags if t.startswith("@")]
            if len(keys) > 0:
                self.key = keys[0]
            else:
                self.key = get_md_link(self.title)
            self.skills = [t[2:] for t in tags if t.startswith("s:")]
            self.requires = [t[2:] for t in tags if t.startswith("r:")]
            self.opt = "opt" in tags
            qmin = [t[2:] for t in tags if t.startswith("q:")]
            if len(qmin) > 0:
                self.qmin = int(qmin[0])
            tmin = [t[2:] for t in tags if t.startswith("t:")]
            if len(tmin) > 0:
                self.tmin = int(tmin[0])
                if self.tmin > 10:
                    print("fail: tmin > 10")
                    exit(1)
            self.update_requirements()
            return True

        minipattern = r"^#+\s*(.*?)\s*$"
        match = re.match(minipattern, line)
        if match:
            self.title = match.group(1)
            self.key = get_md_link(self.title)
            self.update_requirements()
            return True
        
        return False

class Cluster:
    def __init__(self, line_number:int = 0, title: str = "", key: str = ""):
        self.line_number = line_number
        self.title: str = title
        self.key: str = key
        self.quests: list[Quest] = []

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
        return bold(self.get_grade_color(), f"{self.get_percent()}%")

    def get_resume_by_quests(self):
        total = len(self.quests)
        count = len([q for q in self.quests if q.is_complete()])
        return f"({count}/{total})"
        

def rm_comments(title: str) -> str:
    if "<!--" in title and "-->" in title:
        title = title.split("<!--")[0] + title.split("-->")[1]
    return title


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


class Game:
    def __init__(self, file: Optional[str] = None):
        self.clusters: List[Cluster] = []  # clusters ordered
        self.quests: Dict[str, Quest] = {}  # quests indexed by quest key
        self.tasks: Dict[str, Task] = {}  # tasks indexed by task key
        if file is not None:
            self.parse_file(file)

    def get_task(self, key: str) -> Task:
        if key in self.tasks:
            return self.tasks[key]
        raise Exception(f"fail: task {key} not found in course definition")

    # se existir um cluster nessa linha, insere na lista de clusters e retorno o objeto cluster inserido
    def load_cluster(self, line: str, line_num: int) -> Tuple[bool, Optional[Cluster]]:
        pattern = r"^#+\s*(.*?)<!--\s*(.*?)\s*-->\s*$"
        match = re.match(pattern, line)
        if not match:
            return False, None
        titulo = match.group(1)
        tags_raw = match.group(2).strip()
        tags = [tag.strip() for tag in tags_raw.split(" ")]
        if not "group" in tags:
            return False, None
        
        keys = [tag[1:] for tag in tags if tag.startswith("@")]
        key = titulo
        if len(keys) > 0:
            key = keys[0]
        
        cluster = Cluster(line_num, titulo, key)

        # search for existing cluster in self.clusters
        for c in self.clusters:
            if c.key == key:
                print(f"Cluster {key} já existe")
                print(c)
                print(cluster)
                exit(1)
                
        self.clusters.append(cluster)
        return True, cluster
                

    def load_quest(self, line, line_num) -> Tuple[bool, Optional[Quest]]:
        quest = Quest()
        if not quest.parse_quest(line, line_num + 1):
            return False, None
        if quest.key in self.quests:
            print(f"Quest {quest.key} já existe")
            print(quest)
            print(self.quests[quest.key])
            exit(1)
        self.quests[quest.key] = quest
        return True, quest

    def load_task(self, line, line_num) -> Tuple[bool, Optional[Task]]:
        if line == "":
            return False, None
        task = Task()
        found = False
        if task.parse_reading_task(line, line_num + 1):
            found = True
        if task.parse_coding_task(line, line_num + 1):
            found = True
        if not found:
            return False, None
        
        if task.key in self.tasks:
            print(f"Task {task.key} já existe")
            print(task)
            print(self.tasks[task.key])
            exit(1)
        self.tasks[task.key] = task
        return True, task

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
            if len(q.tasks) > 0:
                valid_quests[k] = q

        self.quests = valid_quests

        # for q in self.quests.values():
        #   if len(q.tasks) == 0:
        #     print(f"Quest {q.key} não tem tarefas")
        #     exit(1)

        for q in self.quests.values():
            for r in q.requires:
                if r in self.quests:
                    q.requires_ptr.append(self.quests[r])
                else:
                    print(f"keys: {self.quests.keys()}")
                    print(f"Quest\n{str(q)}\nrequer {r} que não existe")
                    exit(1)

        # check if there is a cycle

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
            visited = []
            dfs(q, visited)

    def parse_file(self, file):
        lines = open(file, encoding="utf-8").read().split("\n")
        active_quest = None
        active_cluster = None
        for line_num, line in enumerate(lines):
            found, cluster = self.load_cluster(line, line_num)
            if found:
                active_cluster = cluster
                continue
            
            found, quest = self.load_quest(line, line_num)
            if found:
                active_quest = quest
                if active_cluster is None:
                    self.clusters.append(Cluster(0, "Sem grupo", "Sem grupo"))
                    active_cluster = self.clusters[-1]
                quest.cluster = active_cluster.key
                active_cluster.quests.append(quest)
                continue

            found, task = self.load_task(line, line_num)
            if found:
                if active_quest is None:
                    print(f"Task {task.key} não está dentro de uma quest")
                    print(task)
                    exit(1)
                active_quest.tasks.append(task)

        self.clear_empty()

        self.validate_requirements()
        for t in self.tasks.values():
            t.process_link(os.path.dirname(file) + "/")

    def clear_empty(self):

        # apagando quests vazias da lista de quests
        for k in list(self.quests.keys()):
            if len(self.quests[k].tasks) == 0:
                del self.quests[k]

        # apagando quests vazias dos clusters e clusters vazios
        clusters = []
        for c in self.clusters:
            quests = [q for q in c.quests if len(q.tasks) > 0]
            if len(quests) > 0:
                c.quests = quests
                clusters.append(c)
        self.clusters = clusters

    def get_reachable_quests(self):
        # cache needs to be reseted before each call
        cache = {}
        return [q for q in self.quests.values() if q.is_reachable(cache)]

    def __str__(self):
        output = []
        for c in self.clusters:
            output.append(str(c))
            for q in c.quests:
                output.append(str(q))
                for t in q.tasks:
                    output.append(str(t))
        return "\n".join(output)

    def generate_graph(self, output, reachable: Optional[List[str]] = None, counts: Optional[Dict[str, str]] = None, graph_ext=".png"):
        saida = ["digraph diag {", '  node [penwidth=1, style="rounded,filled", shape=box]']

        def info(qx):
            text = f'{qx.title.strip()}'
            if reachable is None:
                return f'"{text}"'
            return f'"{text}\\n{counts[qx.key]}"'

        for q in self.quests.values():
            token = "->"
            if len(q.requires_ptr) > 0:
                for r in q.requires_ptr:
                    extra = ""
                    if reachable is not None:
                        if q.key not in reachable:
                            extra = "[style=dotted]"
                    saida.append(f"  {info(r)} {token} {info(q)} {extra}")
            else:
                v = '  "Início"'
                saida.append(f"{v} {token} {info(q)}")

        colorlist = ["lightblue", "pink", "lightgreen", "cyan", "gold", "yellow", "orange", "tomato", "violet", "brown", "gray"]
        for i, c in enumerate(self.clusters):
            for q in c.quests:
                if q.opt:
                    shape = "ellipse"
                else:
                    shape = "box"
                color = "black"
                width = 1
                if reachable is not None:
                    if q.key not in reachable:
                        color = "white"
                    else:
                        width = 3
                        if q.is_complete():
                            color = "green"
                        elif q.in_progress():
                            color = "yellow"
                        elif q.not_started():
                            color = "red"
                saida.append(f"  {info(q)} [shape={shape}, color={color}, penwidth={width}, fillcolor={colorlist[i]}]")


        # for c in self.clusters:
        #     key = get_md_link(c.key).replace("-", "_")
        #     saida.append(f"  subgraph cluster_{key}{{")
        #     saida.append(f'    label="{c.title.strip()}"')
        #     saida.append(f"    style=filled")
        #     saida.append(f"    color=lightgray")
        #     for q in c.quests:
        #         saida.append(f"    {info(q)}")

        #     saida.append("  }")

        saida.append("}")
        # saida.append("@enduml")
        saida.append("")

        dot_file = output + ".dot"
        out_file = output + graph_ext
        open(dot_file, "w").write("\n".join(saida))
        if graph_ext == ".png":
            subprocess.run(["dot", "-Tpng", dot_file, "-o", out_file])
        elif graph_ext == ".svg":
            subprocess.run(["dot", "-Tsvg", dot_file, "-o", out_file])
        else:
            print("Formato de imagem não suportado")
