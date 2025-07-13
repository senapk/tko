from tko.game.cluster import Cluster
from tko.game.quest import Quest
from tko.game.task import Task
import os
from tko.util.decoder import Decoder
from tko.game.game_builder import GameBuilder
from tko.game.game_validator import GameValidator
# from typing import override
from icecream import ic

import yaml # type: ignore
import re

def load_html_tags(task: str) -> None | str:
    pattern = r"<!--\s*(.*?)\s*-->"
    match = re.search(pattern, task)
    if not match:
        return None
    return match.group(1).strip()


class Game:
    def __init__(self):
        self.filename: str = ""
        self.ordered_clusters: list[str] = [] # ordered clusters
        self.clusters: dict[str, Cluster] = {} 
        self.quests: dict[str, Quest] = {}  # quests indexed by quest key
        self.tasks: dict[str, Task] = {}  # tasks indexed by task key

        self.token_level_one = "level_one"
        self.token_level_mult = "level_mult"
        self.level_one: int = 100
        self.level_mult: float = 1.5


    def parse_xp(self, content: str):
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

    def get_skills_resume(self, avaliable_quests: list[Quest]) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
        # obtained, priority, complete
        priority: dict[str, float] = {}
        complete: dict[str, float] = {}
        obtained: dict[str, float] = {}
        for c in self.clusters.values():
            for q in c.get_quests():
                for t in q.get_tasks():
                    for skill, value in t.skills.items():
                        gvalue = (value * t.get_xp() * t.get_ratio())
                        if gvalue < 0.1:
                            gvalue = 0
                        obtained[skill] = obtained.get(skill, 0) + gvalue
                        if not t.is_optional():
                            priority[skill] = priority.get(skill, 0) + value * t.get_xp()
                        complete[skill] = complete.get(skill, 0) + value * t.get_xp()

        # remove all keys with value 0
        # obtained = {k: v for k, v in obtained.items() if v > 0}
        # priority = {k: v for k, v in priority.items() if v > 0}
        # complete = {k: v for k, v in complete.items() if v > 0}
        return obtained, priority, complete

    def sum_xp(self, obtained: dict[str, float], priority: dict[str, float], complete: dict[str, float]) -> tuple[float, float, float]:
        total_obtained = 0
        total_priority = 0
        total_complete = 0
        for key, value in complete.items():
            if obtained.get(key, 0) > 0:
                ic("Warning: skill", key, "has", value, "XP in complete tasks")
            total_obtained += obtained.get(key, 0)
            total_priority += priority.get(key, 0)
            total_complete += value
        return total_obtained, total_priority, total_complete



    def parse_file_and_folder(self, filename: str, folder: str, language: str):
        self.filename = filename
        if filename == "" or not os.path.exists(filename):
            content = ""
        else:
            content = Decoder.load(filename)
        self.parse_xp(content)

        gb = GameBuilder(filename, folder).build_from(content, language)
        self.ordered_clusters = gb.ordered_clusters
        self.clusters = gb.clusters
        self.quests = gb.collect_quests()
        self.tasks = gb.collect_tasks()
        GameValidator(filename, self.clusters).validate()

        # for t in self.tasks.values():
        #     t.get_link(os.path.dirname(filename) + "/")

    @staticmethod
    def is_reachable_quest(q: Quest, cache: dict[str, bool]):
        if q.key in cache:
            return cache[q.key]

        if len(q.requires_ptr) == 0:
            cache[q.key] = True
            return True
        cache[q.key] = all([r.is_complete() and Game.is_reachable_quest(r, cache) for r in q.requires_ptr])
        return cache[q.key]

    # def __get_reachable_quests(self):
    #     # cache needs to be reseted before each call
    #     cache: dict[str, bool] = {}
    #     return [q for q in self.quests.values() if Game.__is_reachable_quest(q, cache)]

    def update_reachable_and_available(self):
        for q in self.quests.values():
            q.set_reachable(False)
            q.update_tasks_reachable()
        for c in self.clusters.values():
            c.set_reachable(False)

        cache: dict[str, bool] = {}
        for c in self.clusters.values():
            for q in c.get_quests():
                if Game.is_reachable_quest(q, cache):
                    q.set_reachable(True)
                    c.set_reachable(True)

    # @override
    def __str__(self):
        output: list[str] = []
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