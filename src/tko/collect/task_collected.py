from __future__ import annotations
from tko.collect.task_collected_resume import TaskCollectedResume
from tko.game.task_info import TaskSelfInfo
from tko.logger.log_sort import LogSort
from tko.game.task import Task
from typing import Any

class TaskCollected:
    class Key:
        REMOTE: str = "remote"
        KEY: str = "key"
        QUEST: str = "quest"
        GRADER: str = "grader"

    def __init__(self):
        self.remote: str = ""
        self._key: str = ""
        self._quest: str = ""
        self.grader: float = 0.0
        self.resume: TaskCollectedResume = TaskCollectedResume()
        self.info: TaskSelfInfo = TaskSelfInfo()

    @property
    def key(self) -> str:
        return self._key
    
    @key.setter
    def key(self, value: str):
        self._key = value
        if "@" in value:
            self._key = value.split("@")[1]

    @property
    def quest(self) -> str:
        return self._quest
    
    @quest.setter
    def quest(self, value: str):
        self._quest = value
        if "@" in value:
            self._quest = value.split("@")[1]

    def setup(self, log_sort: LogSort, task: Task | None, remote_index: dict[str, str] | None):
        key = log_sort.key if log_sort.key else ""
        remote = None
        if "@" in key:
            remote = key.split("@")[0]
        if remote_index is not None and remote and remote in remote_index.keys():
            self.remote = remote_index[remote]
        self.key = key
        self.quest = task.quest_key if task else ""
        self.grader = task.grader.full_percent if task else 0.0

        self.resume.from_log_sort(log_sort)
        if log_sort.self_list:
            _, last_self = log_sort.self_list[-1]
            self.info = last_self.get_info()
        return self
    
    def get_kv(self, include_key: bool, include_quest: bool) -> dict[str, Any]:
        output: dict[str, Any] = {}
        output[TaskCollected.Key.REMOTE] = self.remote
        if include_key:
            output[TaskCollected.Key.KEY] = self.key
        if include_quest:
            output[TaskCollected.Key.QUEST] = self.quest
        output[TaskCollected.Key.GRADER] = f"{round(self.grader):>3}"
        output.update(self.resume.get_kv())
        output.update(self.info.get_kv())
        return output

    def from_kv(self, info: dict[str, str]) -> TaskCollected:
        self.remote = info.get(TaskCollected.Key.REMOTE, "")
        self.key = info.get(TaskCollected.Key.KEY, "")
        self.quest = info.get(TaskCollected.Key.QUEST, "")
        self.grader = float(info.get(TaskCollected.Key.GRADER, 0.0))
        self.resume.from_kv(info)
        self.info.from_kv(info)
        return self
    
    def csv_keys(self):
        output: list[str] = []
        output.append(TaskCollected.Key.REMOTE)
        output.append(TaskCollected.Key.KEY)
        output.append(TaskCollected.Key.QUEST)
        output.append(TaskCollected.Key.GRADER)
        output.extend(self.resume.get_kv(full=True).keys())
        output.extend(self.info.get_kv(full=True).keys())
        return output

    def csv_values(self) -> list[str]:
        output: list[str] = []
        output.append(self.remote)
        output.append(self.key)
        output.append(self.quest)
        output.append(f"{round(self.grader):>3}")
        output.extend(self.resume.get_kv(full=True).values())
        output.extend(self.info.get_kv(full=True).values())
        return output

    def __str__(self) -> str:
        return f"{self.Key.REMOTE}:{self.remote}, {self.Key.KEY}:{self.key}, {self.Key.QUEST}:{self.quest}, {self.Key.GRADER}:{self.grader}, {self.resume.get_kv(full=True)}, {self.info.get_kv(full=True)})"
