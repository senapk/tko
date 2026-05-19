from __future__ import annotations

from typing import Callable

from tko.game.quest_grader import QuestGrader
from tko.game.task_config import TaskMain
from tko.game.task import Task


class QuestProgress:
    def __init__(self, tasks_getter: Callable[[], list[Task]], min_percent_getter: Callable[[], int]):
        self._tasks_getter = tasks_getter
        self._min_percent_getter = min_percent_getter

    def get_xp(self, include_main_perk: bool, include_side: bool) -> tuple[float, float]:
        tasks_info: list[QuestGrader.Elem] = []
        for task in self._tasks_getter():
            if task.config.path in [TaskMain.MAIN, TaskMain.PERK] and not include_main_perk:
                continue
            if task.config.path == TaskMain.SIDE and not include_side:
                continue
            percent = task.grader.full_percent
            tasks_info.append(QuestGrader.Elem(task.config.is_optional, task.game.xp, percent))
        return QuestGrader.calc_xp_earned_total(tasks_info)

    def get_completion(self) -> tuple[int, int]:
        total = 0
        done = 0
        for task in self._tasks_getter():
            total += 1
            if task.grader.is_complete:
                done += 1
        return done, total

    def get_percent_main_and_all(self) -> tuple[float | None, float]:
        percent_main: float | None = 0.0
        percent_all: float = 0.0
        obtainedm, totalm = self.get_xp(include_main_perk=True, include_side=False)
        obtaineds, totals = self.get_xp(include_main_perk=False, include_side=True)
        if totalm > 0:
            percent_main = (obtainedm / totalm) * 100
            percent_all = ((obtainedm + obtaineds) / totalm) * 100
        elif totals > 0:
            percent_main = None
            percent_all = (obtaineds / totals) * 100
        else:
            percent_all = 0.0
        return percent_main, percent_all

    def get_percent(self, include_main_perk: bool, include_side: bool) -> float | None:
        if not include_main_perk and not include_side:
            return None
        main_obt, main_total = self.get_xp(include_main_perk=include_main_perk, include_side=False)
        side_obt, side_total = self.get_xp(include_main_perk=False, include_side=include_side)
        if include_main_perk and include_side:
            return QuestGrader.get_percent(main_obt + side_obt, main_total)
        if include_main_perk:
            return QuestGrader.get_percent(main_obt, main_total)
        if include_side:
            return QuestGrader.get_percent(side_obt, side_total)

    def get_percent_main(self) -> float | None:
        return self.get_percent(include_main_perk=True, include_side=False)

    def get_percent_side(self) -> float | None:
        return self.get_percent(include_main_perk=False, include_side=True)

    def is_complete(self) -> bool:
        value = self.get_percent(include_main_perk=True, include_side=True)
        return value is None or value >= self._min_percent_getter()
