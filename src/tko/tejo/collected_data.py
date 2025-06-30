from __future__ import annotations
from tko.logger.task_resume import TaskResume
from typing import Any

class CollectedData:
    class Task:
        def __init__(self, key: str, value: int = 1, is_leet: bool = False, opt: bool = False):
            self.key = key
            self.xp: int = value
            self.leet: bool = is_leet
            self.opt: bool = opt

        def __str__(self):
            return f"{self.key}, xp:{self.xp}, leet:{self.leet}, opt:{self.opt}"
        
    class Quest:
        def __init__(self, key: str, value: int = 0, opt: bool = False):
            self.key = key
            self.value: int = value
            self.opt: bool = opt
            self.tasks: list[CollectedData.Task] = []

        def load_from_dict(self, json_data: dict[str, Any]):
            self.key = json_data.get("key", self.key)
            self.value = json_data.get("value", self.value)
            self.opt = json_data.get("opt", self.opt)
            tasks_data = json_data.get("tasks", [])
            for task in tasks_data:
                collected_task = CollectedData.Task(task.get("key", ""), task.get("value", 1), task.get("leet", False), task.get("opt", False))
                self.tasks.append(collected_task)

        def __str__(self):
            return f'{self.key}, value:{self.value}\n' + "\n".join([f"\t{str(t)}" for t in self.tasks])
        
    def __init__(self):
        self.resume: dict[str, TaskResume] = {}
        self.graph: str = ""
        self.log: list[str] = []
        self.game: list[CollectedData.Quest] = []

    def load_from_dict(self, json_data: dict[str, Any]):
        task_resume = json_data.get("resume", self.resume)
        for key, value in task_resume.items():
            collected_resume = TaskResume()
            collected_resume.from_dict(value)
            self.resume[key] = collected_resume
        self.graph = json_data.get("graph", self.graph)
        self.log = json_data.get("log", self.log)
        game_data = json_data.get("game", [])
        for quest in game_data:
            collected_quest = CollectedData.Quest(quest.get("key", ""))
            collected_quest.load_from_dict(quest)
            self.game.append(collected_quest)
        return self
