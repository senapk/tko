from tko.floating.floating import Floating, FloatingABC
from tko.util.symbols import Symbols
from tko.util.rt import RT
from tko.i18n import Msg

import curses
from typing import Callable


_INPUT_TEXT_PROMPT = Msg.text(pt="Digite aqui: ", en="Type here: ")


class FloatingInputText(FloatingABC):
    def __init__(self, label: RT, action: Callable[[str], None], unallowed_strings: list[str] | None = None):
        super().__init__()
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

    def is_enable(self) -> bool:
        return self.floating.is_enable()

    def draw(self):
        content = self.floating.content
        content.clear()
        content.append(self.label)
        is_allowed = RT(Symbols.check, "g") if self.input_text not in self.unallowed_strings else RT(Symbols.failure, "r")
        content.append(RT(str(_INPUT_TEXT_PROMPT)) + self.input_text + Symbols.cursor + is_allowed)
        content.append(RT())
        self.floating.draw()

    def process_input(self, key: int) -> int:
        if key == ord('\n'):
            if self.input_text in self.unallowed_strings:
                return -1
            self.floating.enable = False
            self.action(self.input_text)
            return -1
        elif key == curses.KEY_EXIT:
            self.floating.enable = False
            return -1
        elif key == curses.KEY_BACKSPACE:
            self.input_text = self.input_text[:-1]
            return -1
        elif 32 <= key < 127:
            self.input_text += chr(key)
            return -1
        return key
