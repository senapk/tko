from tko.game.quest import Quest
from tko.game.game_builder import GameBuilder
from tko.game.game_validator import GameValidator
from tko.game.task import Task
from tko.repository.remote import Remote
# from typing import override
from icecream import ic # type: ignore
import re
from pathlib import Path
from tko.repository.git_cache import GitCache

def load_html_tags(task: str) -> None | str:
    pattern = r"<!--\s*(.*?)\s*-->"
    match = re.search(pattern, task)
    if not match:
        return None
    return match.group(1).strip()

class Game:
    def __init__(self):
        self.remotes: list[Remote] = []
        self.ordered_quests: list[str] = [] # ordered clusters
        self.quests: dict[str, Quest] = {}  # quests indexed by quest key
        self.tasks: dict[str, Task] = {}  # tasks indexed by task key
        self.language: str = ""

    def get_task(self, key: str) -> Task:
        if key in self.tasks:
            return self.tasks[key]
        raise Warning(f"fail: tarefa '{key}' não encontrada no curso")

    def get_sandbox_remote(self) -> Remote:
        for s in self.remotes:
            if s.is_sandbox:
                return s
        raise ValueError("Local sandbox source not found")

    def set_remotes(self, remotes: list[Remote], language: str):
        self.remotes = remotes
        self.language = language
        return self
    
    def build(self, verbose: bool, git_cache: GitCache, root_dir: Path):
        self.ordered_quests = []
        self.quests = {}
        self.tasks = {}
        for remote in self.remotes:
            gb = GameBuilder(remote, verbose)
            try:
                gb.build_from(self.language)
            except ValueError as e:
                print(e)
                continue
            for quest_key in gb.ordered_quests:
                self.ordered_quests.append(remote.data.name + "@" + quest_key)
            gb_quests = gb.collect_quests()
            gb_tasks = gb.collect_tasks()
            for quest in gb_quests.values():
                self.quests[quest.basic.full_key] = quest
            for task in gb_tasks.values():
                self.tasks[task.basic.full_key] = task
        GameValidator(self.quests).validate()
        for task in self.tasks.values():
            task.git_cache = git_cache
            task.root_dir = root_dir
        return self

    @staticmethod
    def is_reachable_quest(q: Quest, cache: dict[str, bool]):
        if q.basic.full_key in cache:
            return cache[q.basic.full_key]

        if len(q.requires_ptr) == 0:
            cache[q.basic.full_key] = True
            return True
        cache[q.basic.full_key] = all([r.is_complete() and Game.is_reachable_quest(r, cache) for r in q.requires_ptr])
        return cache[q.basic.full_key]

    def update_reachable_and_available(self):
        for q in self.quests.values():
            q.set_reachable(False)
            q.update_tasks_reachable()
        for q in self.quests.values():
            q.set_reachable(False)

        cache: dict[str, bool] = {}
        for q in self.quests.values():
            if Game.is_reachable_quest(q, cache):
                q.set_reachable(True)
                q.set_reachable(True)

    # @override
    def __str__(self):
        output: list[str] = []
        for q in self.quests.values():
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
    
