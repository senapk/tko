from __future__ import annotations

from tko.collect.task_resume import TaskResume
from tko.game.task_info import TaskSelfInfo
from tko.logger.log_sort import LogSort
from typing import Any
from tko.game.task import Task

class TaskUserData:
    class Key:
        KEY: str = "key"
        QUEST: str = "quest"
        GRADER: str = "grader"


    def __init__(self):
        self.key: str = ""
        self._quest: str = ""
        self.grader: float = 0.0
        self.resume: TaskResume = TaskResume()
        self.info: TaskSelfInfo = TaskSelfInfo()

    @property
    def quest(self) -> str:
        return self._quest
    
    @quest.setter
    def quest(self, value: str):
        self._quest = value
        if "@" in value:
            self._quest = value.split("@")[1]


    def setup(self, log_sort: LogSort, task: Task | None):
        self.key = log_sort.key if log_sort.key else ""
        self.quest = task.quest_key if task else ""
        self.grader = task.grader.full_percent if task else 0.0

        self.resume.from_log_sort(log_sort)
        if log_sort.self_list:
            _, last_self = log_sort.self_list[-1]
            self.info = last_self.get_info()
        return self
    
    def get_kv(self, include_key: bool, include_quest: bool) -> dict[str, Any]:
        output: dict[str, Any] = {}
        if include_key:
            output[TaskUserData.Key.KEY] = self.key
        if include_quest:
            output[TaskUserData.Key.QUEST] = self.quest
        output[TaskUserData.Key.GRADER] = f"{round(self.grader):>3}"
        output.update(self.resume.get_kv())
        output.update(self.info.get_kv())
        return output

    def from_kv(self, info: dict[str, str]) -> TaskUserData:
        self.key = info.get(TaskUserData.Key.KEY, "")
        self.quest = info.get(TaskUserData.Key.QUEST, "")
        self.grader = float(info.get(TaskUserData.Key.GRADER, 0.0))
        self.resume.from_kv(info)
        self.info.from_kv(info)
        return self

    def __str__(self) -> str:
        return f"{self.Key.KEY}:{self.key}, {self.Key.QUEST}:{self.quest}, {self.Key.GRADER}:{self.grader}, {self.resume.get_kv()}, {self.info.get_kv()})"
