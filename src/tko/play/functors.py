from .floating_manager import FloatingManager
from .flags import Flag, Flags
from .floating import Floating
from ..util.sentence import Sentence

class FlagFunctor:
    def __init__(self, fman: FloatingManager, flag: Flag):
        self.fman = fman
        self.flag = flag

    def __call__(self):
        self.flag.toggle()
        if (self.flag.get_location() == "left" or self.flag.get_location() == "geral") and self.flag.is_bool():
            f = Floating("v>").warning()
            f.put_text("")
            f.put_text(self.flag.get_description())
            if self.flag.is_true():
                f.put_sentence(Sentence().addf("g", "ligado"))
            else:
                f.put_sentence(Sentence().addf("r", "desligado"))
            f.put_text("")
            self.fman.add_input(f)

class GradeFunctor:
    def __init__(self, grade: int, fn):
        self.grade = grade
        self.fn = fn

    def __call__(self):
        self.fn(self.grade)

