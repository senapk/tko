from tko.play.floating import Floating, FloatingABC
from tko.util.symbols import symbols
from tko.util.text import Text


import curses
from typing import Callable


class FloatingInputText(FloatingABC):
    def __init__(self, label: Text, action: Callable[[str], None], unallowed_strings: list[str]| None = None):
        self.floating = Floating()
        self.floating.set_footer(" Use Enter para confirmar ou Esc para cancelar ")
        self.floating.set_text_ljust()
        self.floating.frame.set_border_color("m")
        self.floating.set_header(" Entrada de texto ")
        self.label = label
        self.input_text: str = ""
        self.action = action
        self.floating.frame.set_border_color("y")
        if unallowed_strings is None:
            unallowed_strings = []
        self.unallowed_strings = unallowed_strings

    # @override
    def is_enable(self) -> bool:
        return self.floating.is_enable()

    # @override
    def draw(self):
        content = self.floating.content
        content.clear()
        content.append(self.label)
        is_allowed = Text().addf("g", symbols.check.text) if self.input_text not in self.unallowed_strings else Text().addf("r", symbols.failure.text)
        content.append(Text.format("Digite aqui: ") + self.input_text + symbols.cursor + is_allowed)
        content.append(Text())
        self.floating.draw()

    # @override
    def process_input(self, key: int) -> int:
        if key == ord('\n'):
            if self.input_text in self.unallowed_strings:
                return -1
            self.floating.enable = False
            self.action(self.input_text)
            return -1
        elif key == curses.KEY_EXIT:
            self.floating.enable = False
        elif key == curses.KEY_BACKSPACE:
            self.input_text = self.input_text[:-1]
            return -1
        elif 32 <= key < 127:
            self.input_text += chr(key)
            return -1
        return key