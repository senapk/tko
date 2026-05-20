from __future__ import annotations

from typing import Callable

from tko.game.quest_grader import QuestGrader
from tko.game.task import Task


class QuestProgress:
    def __init__(self, tasks_getter: Callable[[], list[Task]], min_percent_getter: Callable[[], int], total_xp: Callable[[], int]):
        self._tasks_getter = tasks_getter
        self._min_percent_getter = min_percent_getter
        self._total_xp = total_xp

    def get_xp(self) -> tuple[float, float]:
        tasks_info: list[QuestGrader.Elem] = []
        for task in self._tasks_getter():
            percent = task.grader.full_percent
            tasks_info.append(QuestGrader.Elem(task.game.xp, percent))
        return QuestGrader.calc_xp_earned_total(tasks_info)

    def get_completion(self) -> tuple[int, int]:
        total = 0
        done = 0
        for task in self._tasks_getter():
            total += 1
            if task.grader.is_complete:
                done += 1
        return done, total

    def get_percent(self) -> float:
        obtainedm, totalm = self.get_xp()
        if self._total_xp() == 0:
            totalm = self._total_xp()
        if totalm == 0:
            return 0
        return (obtainedm / totalm) * 100


    def is_complete(self) -> bool:
        value = self.get_percent()
        return value >= self._min_percent_getter()
