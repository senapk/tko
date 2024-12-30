from .flags import Flag

class FlagFunctor:
    def __init__(self, flag: Flag):
        self.flag = flag

    def __call__(self):
        self.flag.toggle()

class GradeFunctor:
    def __init__(self, grade: int, fn):
        self.grade = grade
        self.fn = fn

    def __call__(self):
        self.fn(self.grade)
