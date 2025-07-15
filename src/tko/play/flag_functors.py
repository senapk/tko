from tko.play.flags import Flag
from tko.play.floating_manager import FloatingManager
from tko.play.floating import Floating
from tko.settings.settings import Settings
from typing import Callable


class FlagFunctor:
    def __init__(self, flag: Flag, fman: FloatingManager, settings: Settings):
        self.flag = flag
        self.fman = fman
        self.settings = settings

    def __call__(self):
        self.flag.toggle()
        index = self.flag.get_index()
        if index < len(self.flag.get_msgs()):
            msg = self.flag.get_msgs()[index]
            self.fman.add_input(Floating(self.settings, "").set_warning().put_text(msg))

class GradeFunctor:
    def __init__(self, grade: int, fn: Callable[[int], None]):
        self.grade: int = grade
        self.fn = fn

    def __call__(self):
        self.fn(self.grade)
