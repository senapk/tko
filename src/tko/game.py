#!/usr/bin/env python3

import subprocess
import re
from typing import Optional, Dict, List, Tuple
import os
from .format import symbols, red, green, yellow


class Task:
    def __init__(self):
        self.line_number = 0
        self.line = ""
        self.key = ""
        self.grade = ""
        self.skills = []
        self.title = ""
        self.link = ""
        self.opt = False


    def get_grade_symbol(self, min_value: int = 1):
        if self.grade == "":
            return red(symbols.uncheck)
        if self.grade == "x":
            return green(symbols.check)
        if int(self.grade) >= min_value:
            return yellow(self.grade)
        return red(self.grade)

    def get_grade_value(self):
        if self.grade == "":
            return 0
        if self.grade == "x":
            return 10
        return int(self.grade)

    def get_percent(self):
        if self.grade == "":
            return 0
        if self.grade == "x":
            return 100
        return int(self.grade) * 10
    
    def is_complete(self):
        return self.grade == "x"

    def not_started(self):
        return self.grade == ""
    
    def in_progress(self):
        return self.grade != "" and self.grade != "x"

    def set_grade(self, grade):
        valid = ["", "x", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        if grade in valid:
            self.grade = grade
            return
        if grade == "0":
            self.grade = ""
            return
        if grade == "10":
            self.grade = "x"
            return
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

    def load_html_tags(self, line):
        pattern = r"<!--\s*(.*?)\s*-->"
        match = re.match(pattern, line)
        if not match:
            return
        tags_raw = match.group(1).strip()
        tags = [tag.strip() for tag in tags_raw.split()]
        for t in tags:
            if t.startswith("s:"):
                self.skills.append(t[2:])
            elif t.startswith("@"):
                self.key = t[1:]
            elif t == "opt":
                self.opt = True
        
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

        self.load_html_tags(line)

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
            self.load_html_tags(line)
            return True
        
        found, titulo, link = Task.parse_item_with_link(line)
        self.key = ""
        if found:
            self.load_html_tags(line)
            if self.key == "":
                return False
            self.title = titulo
            self.link = link
            self.line = line
            self.line_number = line_num
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
        self.qmin = 70 # q:  minimo de 70 porcento da pontuação total para completar
        self.tmin = 5  # t: ou ter no mínimo 5 de todas as tarefas

    def __str__(self):
        line = str(self.line_number).rjust(3)
        tasks_size = str(len(self.tasks)).rjust(2, "0")
        key = "" if self.key == self.title else self.key + " "
        output = f"{line}   {tasks_size} {key}{self.title} {self.skills} {self.requires}"
        return output

    def count_valid_tasks(self):
        return len([t for t in self.tasks if t.get_grade_value() >= self.tmin])

    def is_complete(self):
        return self.is_complete_by_percent() or self.is_complete_by_tasks()

    def is_complete_by_percent(self):
        return self.get_percent() >= self.qmin
    
    def is_complete_by_tasks(self):
        return self.count_valid_tasks() >= len(self.tasks)

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
            if t.grade != "":
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
            return True

        minipattern = r"^#+\s*(.*?)\s*$"
        match = re.match(minipattern, line)
        if match:
            self.title = match.group(1)
            self.key = get_md_link(self.title)
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

    def generate_graph(self, output, reachable: Optional[List[str]] = None, counts: Optional[Dict[str, str]] = None):
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
        out_file = output + ".svg"
        open(dot_file, "w").write("\n".join(saida))
        subprocess.run(["dot", "-Tsvg", dot_file, "-o", out_file])
