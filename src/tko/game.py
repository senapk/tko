#!/usr/bin/env python3

import subprocess
import re
from typing import Optional, Dict, List, Tuple
import os
from .format import GSym, red, green, yellow


class Task:
    def __init__(self):
        self.line_number = 0
        self.line = ""
        self.key = ""
        self.grade = ""
        self.skills = []
        self.title = ""
        self.link = ""

    def get_grade(self):
        if self.grade == "":
            return red(GSym.uncheck)
        if self.grade == "x":
            return green(GSym.check)
        number = int(self.grade)
        return yellow(GSym.numbers[number])

    def get_percent(self):
        if self.grade == "":
            return 0
        if self.grade == "x":
            return 100
        return int(self.grade) * 10

    def is_done(self):
        return (
            self.grade == "x"
            or self.grade == "7"
            or self.grade == "8"
            or self.grade == "9"
        )
    
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

    def __str__(self):
        return f"{self.line_number} : {self.key} : {self.grade} : {self.title} : {self.skills} : {self.link}"

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

    def load_html_tags(self, line) -> Tuple[bool, List[str]]:
        pattern = r"<!--\s*(.*?)\s*-->"
        match = re.match(pattern, line)
        if not match:
            return False, []
        tags_raw = match.group(1).strip()
        tags = [tag.strip() for tag in tags_raw.split()]
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


class Quest:
    def __init__(self):
        self.line_number = 0
        self.line = ""
        self.key = ""
        self.title = ""
        self.mdlink = ""
        self.tasks = []
        self.skills = []
        self.group = ""
        self.requires = []
        self.requires_ptr = []
        self.type = "main"

    def __str__(self):
        output = f"linha={self.line_number} : {self.key} : {self.title}"
        output += f": {self.skills} : {self.requires} : {self.mdlink} : {[t.key for t in self.tasks]}"
        return output

    def is_complete(self):
        return all([t.is_done() for t in self.tasks])

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
        
        pattern = r"^#+\s*(.*?)<!--\s*(.*?)\s*-->\s*$"
        match = re.match(pattern, line)
        tags = []

        if match:
            titulo = match.group(1)
            tags_raw = match.group(2).strip()
            tags = [tag.strip() for tag in tags_raw.split()]
        else:
            pattern = r"^#+\s*(.*?)\s*$"
            match = re.match(pattern, line)
            if match:
                titulo = match.group(1)
                tags.append("@" + get_md_link(titulo))
            else:
                return False

        try:
            key = [t[1:] for t in tags if t.startswith("@")][0]
            self.line = line
            self.line_number = line_num
            self.title = titulo
            self.skills = [t[2:] for t in tags if t.startswith("s:")]
            self.requires = [t[2:] for t in tags if t.startswith("r:")]
            self.mdlink = "#" + get_md_link(titulo)
            groups = [t[2:] for t in tags if t.startswith("g:")]
            if len(groups) > 0:
                self.group = groups[0]
            else:
                self.group = ""
            tx = [t for t in tags if t.startswith("t:")]
            if len(tx) > 0:
                self.type = tx[0][2:]
            self.key = key
            return True
        except Exception as e:
            # print(e)
            return False


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
        self.clusters: Dict[str, List[Quest]] = {"": []}  # quests indexed by group
        self.cluster_order: List[str] = [""]  # order of clusters
        self.quests: Dict[str, Quest] = {}  # quests indexed by quest key
        self.tasks: Dict[str, Task] = {}  # tasks  indexed by task key
        if file is not None:
            self.parse_file(file)

    def get_task(self, key: str) -> Task:
        if key in self.tasks:
            return self.tasks[key]
        raise Exception(f"fail: task {key} not found in course definition")

    @staticmethod
    def load_group(line) -> Tuple[bool, Optional[str]]:
        pattern = r"^#+\s*(.*?)<!--\s*(.*?)\s*-->\s*$"
        match = re.match(pattern, line)
        if match:
            titulo = match.group(1)
            tags_raw = match.group(2).strip()
            tags = [tag.strip() for tag in tags_raw.split(" ")]
            if "group" in tags:
                return True, titulo
        return False, None

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

    def load_task(self, line, line_num, last_quest) -> bool:
        if line == "":
            return False
        task = Task()
        found = False
        if task.parse_reading_task(line, line_num + 1):
            found = True
        if task.parse_coding_task(line, line_num + 1):
            found = True
        if not found:
            return False
        
        if last_quest is None:
            print(f"Task {task.key} não está dentro de uma quest")
            print(task)
            exit(1)
        last_quest.tasks.append(task)
        if task.key in self.tasks:
            print(f"Task {task.key} já existe")
            print(task)
            print(self.tasks[task.key])
            exit(1)
        self.tasks[task.key] = task
        return True

    # Verificar se todas as quests requeridas existem e adiciona o ponteiro
    # Verifica se todas as quests tem tarefas
    def validate_requirements(self):

        # verify is there are keys repeated between quests, tasks and groups

        keys = [k for k in self.clusters.keys()] +\
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
        lines = open(file).read().split("\n")
        last_quest = None
        active_group = ""
        for index, line in enumerate(lines):
            found, group = self.load_group(line)
            if found:
                active_group = group
                continue
            

            found, quest = self.load_quest(line, index)
            if found:
                last_quest = quest
                quest.group = active_group

                if quest.group not in self.clusters:
                    self.clusters[quest.group] = []
                    self.cluster_order.append(quest.group)
                self.clusters[quest.group].append(quest)
                continue

            self.load_task(line, index, last_quest)

        self.validate_requirements()
        for t in self.tasks.values():
            t.process_link(os.path.dirname(file) + "/")

    def get_reachable_quests(self):
        # cache needs to be reseted before each call
        cache = {}
        return [q for q in self.quests.values() if q.is_reachable(cache)]

    def show_quests(self):
        print(
            f"Quests de Entrada: {[q.key for q in self.quests.values() if len(q.requires) == 0]}"
        )
        print(f"Total de quests: {len(self.quests)}")
        print(f"Total de tarefas: {len(self.tasks)}")
        print(f"Total de clusters: {len(self.clusters)}")
        # print("\n".join([str(q) for q in self.quests.values()]))

    def generate_graph(self, output):
        saida = [f"@startuml {output}", "digraph diag {", '  node [style="rounded,filled", shape=box]']

        def info(qx):
            return f'"{qx.title.strip()}:{len(qx.tasks)}"'

        for q in self.quests.values():
            token = "->"
            if len(q.requires_ptr) > 0:
                for r in q.requires_ptr:
                    saida.append(f"  {info(r)} {token} {info(q)}")
            else:
                v = '  "Início"'
                saida.append(f"{v} {token} {info(q)}")

        for q in self.quests.values():
            if q.type == "main":
                saida.append(f"  {info(q)} [fillcolor=lime]")
            else:
                saida.append(f"  {info(q)} [fillcolor=pink]")

        groups = {}
        for q in self.quests.values():
            if q.group == "":
                continue
            if q.group not in groups:
                groups[q.group] = []
            groups[q.group].append(q)

        for c in groups.values():
            if c == "":
                continue
            saida.append(f"  subgraph cluster_{c[0].group} {{")
            saida.append(f'    label="{c[0].group}"')
            saida.append(f"    style=filled")
            saida.append(f"    color=lightgray")
            for q in c:
                saida.append(f"    {info(q)}")

            saida.append("  }")

        saida.append("}")
        saida.append("@enduml")
        saida.append("")

        open(output + ".puml", "w").write("\n".join(saida))
        subprocess.run(["plantuml", output + ".puml", "-tsvg"])
