from tko.util.text import Text
from tko.util.symbols import symbols

class Visual:
    def get_lr(self, test: bool) -> tuple[str, str]:
        if test:
            return symbols.right_arrow_filled.text, symbols.left_arrow_filled.text
        else:
            return " ", " "

    def render_button(self, info: str, test: bool):
        left, right = self.get_lr(test)
        bg = "X" if test else ""
        return Text().addf(bg, left).addf(bg, info).addf(bg, right)