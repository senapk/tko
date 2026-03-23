from __future__ import annotations
from tko.logger.task_resume import TaskResume
from typing import Any

default_value: int = 1
default_leet: bool = True
default_opt: bool = False

class Game:
    key_str: str = "key"
    value_str: str = "value"
    opt_str: str = "opt"
    tasks_str: str = "tasks"
    quests_str: str = "quests"
    leet_str: str = "leet"

    class Task:
        def __init__(self, key: str = "", value: int = default_value, is_leet: bool = default_leet, opt: bool = default_opt):
            self.key = key
            self.value: int = value
            self.opt: bool = opt
            self.leet: bool = is_leet
        
        def to_dict(self) -> dict[str, Any]:
            output: dict[str, Any] = {}
            output[Game.key_str] = self.key
            if self.value != default_value:
                output[Game.value_str] = self.value
            if self.leet != default_leet:
                output[Game.leet_str] = self.leet
            if self.opt != default_opt:
                output[Game.opt_str] = self.opt
            return output
        
        def load_from_dict(self, json_data: dict[str, Any]):
            self.key = json_data.get(Game.key_str, self.key)
            self.value = json_data.get(Game.value_str, self.value)
            self.leet = json_data.get(Game.leet_str, self.leet)
            self.opt = json_data.get(Game.opt_str, self.opt)
            return self

        def __str__(self):
            return f"{self.key}, {Game.value_str}:{self.value}, leet:{self.leet}, {Game.opt_str}:{self.opt}"

    class Quest:
        def __init__(self, key: str):
            self.key = key
            self.tasks: list[Game.Task] = []

        def to_dict(self) -> dict[str, Any]:
            output: dict[str, Any] = {
                Game.key_str: self.key,
                Game.value_str: self.value,
                Game.tasks_str: [task.to_dict() for task in self.tasks]
            }
            return output

        def load_from_dict(self, json_data: dict[str, Any]):
            self.key = json_data.get(Game.key_str, self.key)
            self.value = json_data.get(Game.value_str, self.value)
            tasks_data = json_data.get(Game.tasks_str, [])
            for task in tasks_data:
                collected_task = Game.Task().load_from_dict(task)
                self.tasks.append(collected_task)
            return self

        def __str__(self):
            return f'{self.key}, {Game.value_str}:{self.value}\n' + "\n".join([f"\t{str(t)}" for t in self.tasks])

class Collected:
    quests_str: str = "quests"
    resume_str: str = "resume"
    graph_str: str = "graph"
    log_str: str = "log"

    def __init__(self):
        self.resume: dict[str, TaskResume] = {}
        self.graph: str = ""
        self.log: list[str] = []
        self.quests: list[Game.Quest] = []

    def load_from_dict(self, json_data: dict[str, Any]):
        if not Collected.resume_str in json_data:
            print("No resume data found in the JSON.")
            return self

        task_resume = json_data.get(Collected.resume_str, self.resume)
        for key, value in task_resume.items():
            collected_resume = TaskResume(key)
            collected_resume.from_dict(value)
            self.resume[key] = collected_resume
        self.graph = json_data.get(Collected.graph_str, self.graph)
        self.log = json_data.get(Collected.log_str, self.log)
        quest_data = json_data.get(Collected.quests_str, [])
        for quest in quest_data:
            game_quest = Game.Quest(quest.get(Game.key_str, ""))
            game_quest.load_from_dict(quest)
            self.quests.append(game_quest)
        return self

    def to_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = {}
        resume_dict: dict[str, Any] = {}
        for key, value in self.resume.items():
            resume_dict[key] = value.to_dict()
        output[Collected.resume_str] = resume_dict
        output[Collected.graph_str] = self.graph
        output[Collected.log_str] = self.log
        output[Collected.quests_str] = [quest.to_dict() for quest in self.quests]
        return output
