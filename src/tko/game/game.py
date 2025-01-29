from typing import List, Dict, Tuple

from tko.game.cluster import Cluster
from tko.game.quest import Quest
from tko.game.task import Task

from tko.util.decoder import Decoder
from tko.game.game_builder import GameBuilder
from tko.game.game_validator import GameValidator

import yaml # type: ignore

import re
import os

def load_html_tags(task: str) -> None | str:
    pattern = r"<!--\s*(.*?)\s*-->"
    match = re.search(pattern, task)
    if not match:
        return None
    return match.group(1).strip()


class Game:
    def __init__(self):
        self.ordered_clusters: List[str] = [] # ordered clusters
        self.clusters: Dict[str, Cluster] = {} 
        self.quests: Dict[str, Quest] = {}  # quests indexed by quest key
        self.tasks: Dict[str, Task] = {}  # tasks indexed by task key

        self.token_level_one = "level_one"
        self.token_level_mult = "level_mult"
        self.level_one: int = 100
        self.level_mult: float = 1.5


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
                            obtained[s] += int(t.skills[s] * t.get_ratio())
                        else:
                            obtained[s] += 0
                    else:
                        total[s] = t.skills[s]
                        if reachable:
                            obtained[s] = int(t.skills[s] * t.get_ratio())
                        else:
                            obtained[s] = 0
                for s in t.qskills:
                    if s in total:
                        total[s] += t.qskills[s]
                        if reachable:
                            obtained[s] += int(t.qskills[s] * t.get_ratio())
                        else:
                            obtained[s] += 0
                    else:
                        total[s] = t.qskills[s]
                        if reachable:
                            obtained[s] = int(t.qskills[s] * t.get_ratio())
                        else:
                            obtained[s] = 0
        return total, obtained


    def parse_file_and_folder(self, filename: str, folder: str):
        self.filename = filename
        content = Decoder.load(filename)
        self.parse_xp(content)

        gb = GameBuilder(filename, folder).build_from(content)
        self.ordered_clusters = gb.ordered_clusters
        self.clusters = gb.clusters
        self.quests = gb.collect_quests()
        self.tasks = gb.collect_tasks()
        GameValidator(filename, self.clusters, self.quests, self.tasks).validate()

        # for t in self.tasks.values():
        #     t.get_link(os.path.dirname(filename) + "/")

    @staticmethod
    def is_reachable_quest(q: Quest, cache: Dict[str, bool]):
        if q.key in cache:
            return cache[q.key]

        if len(q.requires_ptr) == 0:
            cache[q.key] = True
            return True
        cache[q.key] = all([r.is_complete() and Game.is_reachable_quest(r, cache) for r in q.requires_ptr])
        return cache[q.key]

    # def __get_reachable_quests(self):
    #     # cache needs to be reseted before each call
    #     cache: Dict[str, bool] = {}
    #     return [q for q in self.quests.values() if Game.__is_reachable_quest(q, cache)]

    def update_reachable_and_available(self):
        for q in self.quests.values():
            q.set_reachable(False)
            q.update_tasks_reachable()
        for c in self.clusters.values():
            c.set_reachable(False)

        cache: Dict[str, bool] = {}
        for c in self.clusters.values():
            for q in c.get_quests():
                if Game.is_reachable_quest(q, cache):
                    q.set_reachable(True)
                    c.set_reachable(True)


    def __str__(self):
        output = []
        for c in self.clusters.values():
            output.append("# " + str(c))
            for q in c.get_quests():
                output.append("  - " + str(q))
                for t in q.get_tasks():
                    output.append("    - " + str(t))
        output.append(100 * "-")
        for q in self.quests.values():
            output.append(str(q))
        output.append(100 * "-")
        for t in self.tasks.values():
            output.append(str(t))
        return "\n".join(output)