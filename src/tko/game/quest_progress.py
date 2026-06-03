from __future__ import annotations

from typing import Callable

from tko.game.quest_grader import QuestGrader
from tko.game.task import Task


class QuestProgress:
    def __init__(self, tasks_getter: Callable[[], list[Task]], min_percent_getter: Callable[[], int], goal_xp: Callable[[], int]):
        self._tasks_getter = tasks_getter
        self._min_percent_getter = min_percent_getter
        self._goal_xp = goal_xp

    def get_obtained_goal_available(self) -> tuple[float, float, float]:
        tasks_info: list[QuestGrader.Elem] = []
        for task in self._tasks_getter():
            percent = task.grader.full_percent
            tasks_info.append(QuestGrader.Elem(task.game.xp, percent))
        obtained, available = QuestGrader.calc_xp_earned_total(tasks_info)
        goal = self._goal_xp()
        if goal == 0:
            goal = available
        return obtained, goal, available

    def get_completion(self) -> tuple[int, int]:
        total = 0
        done = 0
        for task in self._tasks_getter():
            total += 1
            if task.grader.is_complete:
                done += 1
        return done, total

    def get_percent(self) -> float:
        obtainedm, goalm, totalm = self.get_obtained_goal_available()
        if totalm == 0:
            return 0
        return (obtainedm / goalm) * 100


    def is_complete(self) -> bool:
        value = self.get_percent()
        return value >= self._min_percent_getter()
