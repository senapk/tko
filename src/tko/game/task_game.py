from __future__ import annotations
from tko.util.rt import RT
from tko.util.symbols import Symbols


class TaskGame:
    def __init__(self):
        self.default_min_value: int = 5 # default min grade to complete task
        self._xp: int = 1
        self._tier: int = 1
        self.skills: set[str] = set()
        self.is_reachable: bool = False

    def clone(self) -> TaskGame:
        new_task = TaskGame()
        new_task.skills = self.skills.copy()
        new_task._xp = self._xp
        new_task._tier = self._tier
        new_task.is_reachable = self.is_reachable
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

    @property
    def xp(self) -> int:
        if self._xp == 0:
            return 1
        return self._xp

    @xp.setter
    def xp(self, value: int):
        if value < 0:
            value = 1
        self._xp = value

    @property
    def tier(self) -> int:
        if self._tier == 0:
            return 1
        return self._tier

    @tier.setter
    def tier(self, value: int):
        if value < 0:
            value = 1
        if value > 4:
            value = 4
        self._tier = value

    @property
    def tier_symbol(self) -> RT:
        #values: list[RT] = [RT("▁", "w"), RT("▃", "g"), RT("▅", "y"), RT("▇", "r")]
        values: list[RT] = [RT("░", "g"), RT("▒", "g"), RT("▓", "g"), RT("▇", "r")]
        return values[self.tier - 1]
    