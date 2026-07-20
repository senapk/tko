from __future__ import annotations
from tko.game.tree_item import TreeBasic, TreeUi
from tko.game.task import Task
from tko.game.quest_source import QuestSource
from tko.game.quest_config import QuestGame
from tko.game.quest_requirements import QuestRequirements
from tko.game.quest_state import QuestState
from tko.game.quest_progress import QuestProgress

# from typing import override

class Quest:
    def __init__(self, title: str = "", key: str = ""):
        self.basic = TreeBasic()
        self.ui = TreeUi()
        self.source = QuestSource()
        self.game = QuestGame()
        self.requirements = QuestRequirements()
        self.state = QuestState()

        self.basic.key = key
        self.basic.title = title

        self.__tasks: list[Task] = []
        self.progress = QuestProgress( # using lambda functions to shared primitives
            lambda: self.__tasks, 
            lambda: self.game.threshold, 
            lambda: self.game.goal_xp
        )
    
    def update_tasks_reachable(self):
        for task in self.__tasks:
            task.game.is_reachable = True
        return

    # @override
    def __str__(self):
        line = str(self.source.line_number).rjust(3)
        tasks_size = str(len(self.__tasks)).rjust(2, "0")
        key = "" if self.basic.full_key == self.basic.title else self.basic.full_key + " "
        output = f"{line} {tasks_size} {key}{self.basic.title} {self.game.skill} {self.requirements.requires}"
        return output

    def add_task(self, task: Task):
        task.game.skill = self.game.skill
        self.__tasks.append(task)

    def get_tasks(self):
        return self.__tasks

    def sort_tasks_by_title(self):
        self.__tasks = sorted(self.__tasks, key=lambda tr: tr.basic.title)
