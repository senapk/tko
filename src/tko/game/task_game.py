from __future__ import annotations

from tko.util.rt import RT
from tko.util.symbols import Symbols


class TaskGame:
    def __init__(self):
        self.default_min_value: int = 5 # default min grade to complete task
        self.xp: float = 0.0
        self.skill: str | None = None

    def clone(self) -> TaskGame:
        new_task = TaskGame()
        new_task.skill = self.skill
        new_task.xp = self.xp
        return new_task

    def get_rate_color(self, value: int, min_value: None | int = None) -> str:
        if min_value is None:
            min_value = self.default_min_value
        if value == 0:
            return "c"
        if value < min_value:
            return "r"
        if value < 10:
            return "y"
        if value == 10:
            return "g"
        return "w"

    def get_rate_symbol(self, value: int, min_value: None | int = None) -> RT:
        if value < 0:
            if min_value is not None:
                if value < min_value:
                    return RT("x")
        elif value < 100:
            prog = (value + 5) // 10
            color = "y" if value >= 50 else "r"
            if prog == 10:
                prog = 9
            return RT(str(prog), color)
        elif value >= 100:
            color = "g"
            return RT(Symbols.check, color)
        return RT("0")
