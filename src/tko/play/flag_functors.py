from tko.play.flags import Flag
from tko.play.floating_manager import FloatingManager
from tko.play.floating import Floating
from typing import Callable


class FlagFunctor:
    def __init__(self, flag: Flag, fman: FloatingManager):
        self.flag = flag
        self.fman = fman

    def __call__(self):
        self.flag.toggle()

        # mensagem do estado atual
        msg = self.flag.msgs[self.flag.get_value()]

        if msg:
            self.fman.add_input(
                Floating().set_warning().put_text(msg)
            )

class GradeFunctor:
    def __init__(self, grade: int, fn: Callable[[int], None]):
        self.grade: int = grade
        self.fn = fn

    def __call__(self):
        self.fn(self.grade)
