from __future__ import annotations

from tko.collect.task_collected_resume import TaskCollectedResume
from typing import Any

class SkillsCollected:
    class Key:
        QUEST: str = "quest"
        GRADER: str = "grader"


    def __init__(self):
        self.remote: str = ""
        self.index: str = ""
        self.quest: str = ""
        self.grader: float = 0.0
        self.resume: TaskCollectedResume = TaskCollectedResume()

    
    def get_kv(self) -> dict[str, Any]:
        output: dict[str, Any] = {}
        output[SkillsCollected.Key.QUEST] = self.quest
        output[SkillsCollected.Key.GRADER] = f"{round(self.grader):>3}"
        output.update(self.resume.get_kv())
        return output

    def from_kv(self, info: dict[str, str]) -> SkillsCollected:
        self.quest = info.get(SkillsCollected.Key.QUEST, "")
        self.grader = float(info.get(SkillsCollected.Key.GRADER, 0.0))
        self.resume.from_kv(info)
        return self
    
    def csv_keys(self):
        output: list[str] = []
        output.append(SkillsCollected.Key.QUEST)
        output.append(SkillsCollected.Key.GRADER)
        output.extend(self.resume.get_kv(full=True).keys())
        return output

    def csv_values(self) -> list[str]:
        output: list[str] = []
        output.append(self.quest)
        output.append(f"{round(self.grader):>3}")
        output.extend(self.resume.get_kv(full=True).values())
        return output

    def __str__(self) -> str:
        return f"{self.Key.QUEST}:{self.quest}, {self.Key.GRADER}:{self.grader}, {self.resume.get_kv(full=True)} )"
