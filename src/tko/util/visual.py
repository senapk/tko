from tko.util.text import Text
from tko.util.symbols import Symbols

class Visual:
    def __init__(self, use_borders: bool = True):
        self.use_borders = use_borders

    def get_lr(self, test: bool) -> tuple[str, str]:
        if test:
            if self.use_borders:
                return Symbols.sharp_left, Symbols.sharp_right
            else:
                return "[", "]"
        else:
            return " ", " "

    def render_button(self, info: str, test: bool):
        left, right = self.get_lr(test)
        bg = "X" if test else ""
        return Text().add(left).addf(bg, info).add(right)