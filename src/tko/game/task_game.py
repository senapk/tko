from __future__ import annotations
from tko.util.rt import RT
from tko.util.symbols import Symbols


class TaskGame:
    def __init__(self):
        self.default_min_value: int = 5 # default min grade to complete task
        self._gain: int = 1
        self._cost: int = 1
        self._size: int = 1
        self.skill: str | None = None
        self.is_reachable: bool = False

    def clone(self) -> TaskGame:
        new_task = TaskGame()
        new_task.skill = self.skill
        new_task._gain = self._gain
        new_task._cost = self._cost
        new_task._size = self._size
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
    def gain(self) -> int:
        if self._gain == 0:
            return 1
        return round(self._gain)
    

    @gain.setter
    def gain(self, value: int):
        if value < 0:
            value = 1
        if value > 3:
            value = 3
        self._gain = value

    @property
    def cost(self) -> int:
        if self._cost == 0:
            return 1
        return self._cost

    @cost.setter
    def cost(self, value: int):
        if value < 0:
            value = 1
        if value > 6:
            value = 6
        self._cost = value

    @property
    def size(self) -> int:
        if self._size == 0:
            return 1
        return self._size

    @size.setter
    def size(self, value: int):
        if value < 0:
            value = 1
        if value > 3:
            value = 3
        self._size = value

    @property
    def cost_symbol(self) -> RT:
        #values: list[RT] = [RT("▁", "w"), RT("▃", "g"), RT("▅", "y"), RT("▇", "r")]
        values: list[RT] = [RT(Symbols.block_1, "g"), RT(Symbols.block_2, "g"), RT(Symbols.block_3, "g"), RT(Symbols.block_4, "r")]
        return values[min(self.cost, len(values)) - 1]
