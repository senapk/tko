from typing import List, Dict, Optional, Tuple
from .cluster import Cluster
from .quest import Quest, QuestParser
from .task import Task, TaskParser
import re
import os


def load_html_tags(task: str) -> Optional[str]:
    pattern = r"<!--\s*(.*?)\s*-->"
    match = re.search(pattern, task)
    if not match:
        return None
    return match.group(1).strip()

class Game:
    def __init__(self, file: Optional[str] = None):
        self.clusters: List[Cluster] = []  # clusters ordered
        self.quests: Dict[str, Quest] = {}  # quests indexed by quest key
        self.tasks: Dict[str, Task] = {}  # tasks indexed by task key

        self.token_level_one = "level_one"
        self.token_level_mult = "level_mult"
        self.level_one = 100
        self.level_mult = 1.5

        self.filename = None
        if file is not None:
            self.filename = file
            self.parse_file(file)

    def parse_xp(self, line: str):
        values = load_html_tags(line)
        if values is not None:
            tags = values.split(" ")
            for t in tags:
                if t.startswith(self.token_level_one):
                    self.level_one = int(t.split(":")[1])
                if t.startswith(self.token_level_mult):
                    self.level_mult = float(t.split(":")[1])

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
        task = TaskParser.parse_line(line, line_num + 1)
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

    def get_skills_resume(self) -> Tuple[Dict[str, int], Dict[str, int]]:
        total: Dict[str, int] = {}
        obtained: Dict[str, int] = {}
        for q in self.quests.values():
            for t in q.get_tasks():
                for s in t.skills:
                    if s in total:
                        total[s] += t.skills[s]
                        obtained[s] += int(t.skills[s] * t.grade/10)
                    else:
                        total[s] = t.skills[s]
                        obtained[s] = int(t.skills[s] * t.grade/10)
                for s in t.qskills:
                    if s in total:
                        total[s] += t.qskills[s]
                        obtained[s] += int(t.qskills[s] * t.grade/10)
                    else:
                        total[s] = t.qskills[s]
                        obtained[s] = int(t.qskills[s] * t.grade/10)
        return total, obtained

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
            self.parse_xp(lines[0])

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
