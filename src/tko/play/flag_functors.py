from tko.play.flags import Flag
from typing import Callable

class FlagFunctor:
    def __init__(self, flag: Flag):
        self.flag = flag

    def __call__(self):
        self.flag.toggle()

class GradeFunctor:
    def __init__(self, grade: int, fn: Callable[[int], None]):
        self.grade: int = grade
        self.fn = fn

    def __call__(self):
        self.fn(self.grade)
