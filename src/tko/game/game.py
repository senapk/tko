from typing import List, Dict, Optional, Tuple
from tko.game.cluster import Cluster
from tko.game.quest import Quest, QuestParser
from tko.game.task import Task, TaskParser
from tko.util.get_md_link import get_md_link
from tko.util.to_asc import uni_to_asc
from tko.util.decoder import Decoder
import yaml # type: ignore

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
        self.ordered_clusters: List[str] = [] # ordered clusters
        self.clusters: Dict[str, Cluster] = {} 
        self.quests: Dict[str, Quest] = {}  # quests indexed by quest key
        self.tasks: Dict[str, Task] = {}  # tasks indexed by task key

        self.available_quests: List[str] = []
        self.available_clusters: List[str] = []

        self.token_level_one = "level_one"
        self.token_level_mult = "level_mult"
        self.level_one: int = 100
        self.level_mult: float = 1.5

        self.filename = None
        if file is not None:
            self.filename = file
            self.parse_file(file)

    def parse_xp(self, content):
        if content.startswith('---'):
            front_matter = content.split('---')[1].strip()
            yaml_data = yaml.safe_load(front_matter)
            if self.token_level_one in yaml_data:
                self.level_one = int(yaml_data[self.token_level_one])
            if self.token_level_mult in yaml_data:
                self.level_mult = float(yaml_data[self.token_level_mult])

    def get_task(self, key: str) -> Task:
        if key in self.tasks:
            return self.tasks[key]
        raise Warning(f"fail: tarefa '{key}' não encontrada no curso")

    # se existir um cluster nessa linha, insere na lista de clusters e 
    # retorno o objeto cluster inserido
    def load_cluster(self, line: str, line_num: int) -> Optional[Cluster]:
        if not line.startswith("## "):
            return None
        line = line[3:]

        titulo = line
        tags_raw = ""
        if "<!--" in line:
            pieces = line.split("<!--")
            titulo = pieces[0]
            middle_end = pieces[1].split("-->")
            tags_raw = middle_end[0]
            titulo += middle_end[1]

        tags = [tag.strip() for tag in tags_raw.split(" ")]        
        key = uni_to_asc(get_md_link(titulo))
        try:
            color = [tag[2:] for tag in tags if tag.startswith("c:")][0]
        except IndexError as _e:
            color = None
        
        cluster = Cluster(line_num, titulo, key, color)

        if key in self.clusters.keys():
            c = self.clusters[key]
            print(f"Cluster {key} já existe")
            print(f"{self.filename}:{line_num}")
            print(f"{self.filename}:{c.line_number}")
            print("  " + str(c))
            print("  " + str(cluster))
            exit(1)
                
        self.clusters[key] = cluster
        self.ordered_clusters.append(key)
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

    def get_skills_resume(self, avaliable_quests: List[Quest]) -> Tuple[Dict[str, int], Dict[str, int]]:
        total: Dict[str, int] = {}
        obtained: Dict[str, int] = {}
        avaliable_keys = [q.key for q in avaliable_quests]
        for q in self.quests.values():
            reachable = q.key in avaliable_keys
            for t in q.get_tasks():
                for s in t.skills:
                    if s in total:
                        total[s] += t.skills[s]
                        if reachable:
                            obtained[s] += int(t.skills[s] * t.self_grade/10)
                        else:
                            obtained[s] += 0
                    else:
                        total[s] = t.skills[s]
                        if reachable:
                            obtained[s] = int(t.skills[s] * t.self_grade/10)
                        else:
                            obtained[s] = 0
                for s in t.qskills:
                    if s in total:
                        total[s] += t.qskills[s]
                        if reachable:
                            obtained[s] += int(t.qskills[s] * t.self_grade/10)
                        else:
                            obtained[s] += 0
                    else:
                        total[s] = t.qskills[s]
                        if reachable:
                            obtained[s] = int(t.qskills[s] * t.self_grade/10)
                        else:
                            obtained[s] = 0
        return total, obtained

    # Verificar se todas as quests requeridas existem e adiciona o ponteiro
    # Verifica se todas as quests tem tarefas
    def validate_requirements(self):

        # verify is there are keys repeated between quests, tasks and groups

        keys = [c.key for c in self.clusters.values()] +\
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

        # trim titles
        for q in self.quests.values():
            q.title = q.title.strip()
        for c in self.clusters.values():
            c.title = c.title.strip()

        self.quests = valid_quests
        # verificar auto dependencia
        for q in self.quests.values():
            for r in q.requires:
                if q.key == r:
                    print(f"Erro: auto refência {q.line_number} {q.line}")
                    exit(1)


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

    def tie_cluster_quest(self, cluster: Cluster, quest: Quest):
        quest.cluster_key = cluster.key
        cluster.quests.append(quest)

    def create_unamed_quest(self, cluster):
        key = cluster.key + "_Sem_Missão"
        quest: Quest = Quest("Sem Missão", key)
        self.quests[key] = quest
        self.tie_cluster_quest(cluster, quest)
        return quest

    def parse_file(self, filename: str):
        self.filename = filename
        content = Decoder.load(filename)
        lines = content.splitlines()
        self.parse_xp(content)

        key = "Sem Grupo"
        active_cluster: Cluster = Cluster(0, key, key)
        self.clusters[key] = active_cluster
        self.ordered_clusters.append(key)
        
        active_quest: Quest = self.create_unamed_quest(active_cluster)

        for line_num, line in enumerate(lines):
            cluster = self.load_cluster(line, line_num)
            if cluster is not None:
                active_cluster = cluster
                active_quest = self.create_unamed_quest(active_cluster)
                continue
            
            quest = self.load_quest(line, line_num)
            if quest is not None:
                active_quest = quest
                self.tie_cluster_quest(active_cluster, active_quest)
                continue

            task = self.load_task(line, line_num)
            if task is not None:
                active_quest.add_task(task, filename)
                task.quest_key = active_quest.key
                task.cluster_key = active_cluster.key

        self.clear_empty()

        self.validate_requirements()
        for t in self.tasks.values():
            t.process_link(os.path.dirname(filename) + "/")

    def clear_empty(self):

        # apagando quests vazias da lista de quests
        for k in list(self.quests.keys()):
            if len(self.quests[k].get_tasks()) == 0:
                del self.quests[k]

        # apagando quests vazias dos clusters e clusters vazios
        ordered_clusters: List[str] = []
        clusters: Dict[str, Cluster] = {}
        for key in self.ordered_clusters:
            cluster = self.clusters[key]
            quests = [q for q in cluster.quests if len(q.get_tasks()) > 0]
            if len(quests) > 0:
                cluster.quests = quests
                clusters[cluster.key] = cluster
                ordered_clusters.append(cluster.key)

        self.ordered_clusters = ordered_clusters
        self.clusters = clusters

    @staticmethod
    def __is_reachable_quest(q: Quest, cache: Dict[str, bool]):
        if q.key in cache:
            return cache[q.key]

        if len(q.requires_ptr) == 0:
            cache[q.key] = True
            return True
        cache[q.key] = all([r.is_complete() and Game.__is_reachable_quest(r, cache) for r in q.requires_ptr])
        return cache[q.key]

    # def __get_reachable_quests(self):
    #     # cache needs to be reseted before each call
    #     cache: Dict[str, bool] = {}
    #     return [q for q in self.quests.values() if Game.__is_reachable_quest(q, cache)]

    def update_reachable_and_available(self, admin_mode: bool):
        for q in self.quests.values():
            q.set_reachable(False)
        for c in self.clusters.values():
            c.set_reachable(False)

        cache: Dict[str, bool] = {}
        for c in self.clusters.values():
            for q in c.quests:
                if Game.__is_reachable_quest(q, cache):
                    q.set_reachable(True)
                    c.set_reachable(True)

        self.available_quests = []
        self.available_clusters = []
        if admin_mode:
            self.available_quests = [key for key in self.quests.keys()]
            self.available_clusters = [key for key in self.clusters.keys()]
        else:
            self.available_quests = [q.key for q in self.quests.values() if q.is_reachable()]
            self.available_clusters = [c.key for c in self.clusters.values() if c.is_reachable()]


    def __str__(self):
        output = []
        for c in self.clusters.values():
            output.append(str(c))
            for q in c.quests:
                output.append(str(q))
                for t in q.get_tasks():
                    output.append(str(t))
        return "\n".join(output)
