from loguru import logger
import re
from pathlib import Path

from icecream import ic # type: ignore

from tko.game.game_builder import GameBuilder
from tko.game.game_validator import GameValidator
from tko.game.quest import Quest
from tko.game.task import Task
from tko.repository.git_cache import GitCache
from tko.repository.remote import Remote
from tko.i18n import Msg
# from typing import override




_GAME_TASK_NOT_FOUND_IN_COURSE = Msg.text(
    pt="fail: tarefa '{task_key}' não encontrada no curso",
    en="fail: task '{task_key}' not found in course",
)
_GAME_SANDBOX_SOURCE_NOT_FOUND = Msg.text(
    pt="Local sandbox source not found",
    en="Local sandbox source not found",
)
_GAME_BUILD_FAILED_FOR_SOURCE = Msg.text(
    pt="Falha ao construir jogo para a fonte {name}",
    en="Failed to build game for source {name}",
)

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

    def get_task_throw(self, key: str) -> Task:
        if key in self.tasks:
            return self.tasks[key]
        raise Warning(str(_GAME_TASK_NOT_FOUND_IN_COURSE).format(task_key=key))

    def get_task(self, key: str) -> Task | None:
        if key in self.tasks:
            return self.tasks[key]
        return None
    
    def get_sandbox_remote_throw(self) -> Remote:
        for s in self.remotes:
            if s.is_sandbox:
                return s
        raise ValueError(str(_GAME_SANDBOX_SOURCE_NOT_FOUND))

    def set_remotes(self, remotes: list[Remote], language: str):
        self.remotes = remotes
        self.language = language
        return self
    
    def build(self, git_cache: GitCache, root_dir: Path):
        self.ordered_quests = []
        self.quests = {}
        self.tasks = {}
        for remote in self.remotes:
            gb = GameBuilder(remote)
            try:
                gb.build_from(self.language)
            except ValueError:
                logger.exception(str(_GAME_BUILD_FAILED_FOR_SOURCE).format(name=remote.data.name))
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

        if len(q.requirements.requires_ptr) == 0:
            cache[q.basic.full_key] = True
            return True
        cache[q.basic.full_key] = all(
            [r.progress.is_complete() and Game.is_reachable_quest(r, cache) for r in q.requirements.requires_ptr]
        )
        return cache[q.basic.full_key]

    def update_reachable_and_available(self):
        for q in self.quests.values():
            q.state.is_reachable = False
            q.update_tasks_reachable()
        for q in self.quests.values():
            q.state.is_reachable = False

        cache: dict[str, bool] = {}
        for q in self.quests.values():
            if Game.is_reachable_quest(q, cache):
                q.state.is_reachable = True
                q.state.is_reachable = True

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
    
