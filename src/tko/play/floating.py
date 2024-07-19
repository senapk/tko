from typing import List
from .frame import Frame
from ..util.ftext import Sentence
from .fmt import Fmt

import curses


class Floating:
    def __init__(self, _align=""):
        self._frame = Frame(0, 0)
        self._content: List[Sentence] = []
        self._type = "warning"
        self._options = []
        self._options_index = 0
        self._fn_answer = None
        self._enable = True
        self._extra_exit: List[int] = []
        self._exit_fn = None
        self._exit_key = None
        self._centralize = True
        self._floating_align = _align

    def disable(self):
        self._enable = False

    def set_ljust_text(self):
        self._centralize = False
        return self

    def set_align(self, _align: str):
        self._floating_align = _align

    def set_header(self, text: str):
        self._frame.set_header(Sentence().addf("/", text), "")
        return self
    
    def set_header_sentence(self, sentence: Sentence):
        self._frame.set_header(sentence, "")
        return self
    
    def set_exit_key(self, key: str):
        self._exit_key = ord(key)
        return self

    def set_exit_fn(self, fn):
        self._exit_fn = fn
        return self

    def _set_xy(self, dy, dx):
        valid = "<>^v"
        for c in self._floating_align:
            if c not in valid:
                raise ValueError("Invalid align " + c)

        lines, cols = Fmt.get_size()

        x = (cols - dx) // 2
        if "<" in self._floating_align:
            x = 1
        elif ">" in self._floating_align:
            x = cols - dx - 3

        y = (lines - dy) // 2
        if "^" in self._floating_align:
            y = 1
        elif "v" in self._floating_align:
            y = lines - dy - 3

        self._frame.set_pos(y, x)
        return self
            
    def is_enable(self):
        return self._enable

    def __setup_frame(self):
        header_len = self._frame.get_header().len()
        footer_len = self._frame.get_footer().len()
        data = [x.len() for x in self._content] + [header_len, footer_len]
        max_dx = max(data)
        dx = max_dx
        dy = len(self._content)
        self._frame.set_inner(dy, dx)
        self._set_xy(dy, dx)
        self._frame.set_fill()
        
        if self._type == "answer":
            footer = Sentence().add(" ")
            for i, option in enumerate(self._options):
                fmt = "kG" if i == self._options_index else ""
                footer.addf(fmt, option).add(" ")
            self._frame.set_footer(footer, "^")

    def put_text(self, text: str):
        lines = text.split("\n")
        for line in lines:
            self._content.append(Sentence().add(line))
        return self

    def put_sentence(self, sentence: Sentence):
        self._content.append(sentence)
        return self
    
    def set_content(self, content: List[str]):
        self._content = [Sentence().add(x) for x in content]
        return self

    def _set_default_footer(self):
        if self._frame.get_footer().len() == 0:
            label = Sentence().addf("/", " Pressione uma tecla ")
            self._frame.set_footer(label, "", "─", "─")
        return self

    def _set_default_header(self):
        if self._frame.get_header().len() == 0:
            if self._type == "warning":
                self.set_header(" Aviso ")
            elif self._type == "error":
                self.set_header(" Erro ")
            elif self._type == "answer":
                self.set_header(" Resposta ")

    def warning(self):
        self._type = "warning"
        self._frame.set_border_color("y")
        return self
    
    def error(self):
        self._type = "warning"
        self._frame.set_border_color("r")
        return self
    
    def answer(self, fn_answer):
        self._type = "answer"
        self._frame.set_border_color("g")
        self._fn_answer = fn_answer
        return self

    def set_options(self, options: List[str]):
        self._options = options
        return self

    def draw(self):
        self._set_default_header()
        self._set_default_footer()
        self.__setup_frame()
        self._frame.draw()
        y = 0

        for line in self._content:
            x = 0
            if self._centralize:
                x = (self._frame.get_dx() - line.len()) // 2
            self._frame.write(y, x, line)
            y += 1
        return self

    def get_input(self) -> int:
        self.draw()
        key: int = Fmt.getch()
        if self._type == "warning" or self._type == "error":
            if key < 300:
                self._enable = False
                if self._exit_fn is not None:
                    self._exit_fn()
                if self._exit_key is not None:
                    return self._exit_key
                if key == " " or key == "\n":
                    return -1
                return key
        if self._type == "answer":
            if key == curses.KEY_LEFT:
                self._options_index = (self._options_index - 1) % len(self._options)
            elif key == curses.KEY_RIGHT:
                self._options_index = (self._options_index + 1) % len(self._options)
            elif key == ord('\n'):
                self._enable = False
                if self._fn_answer is not None:
                    self._fn_answer(self._options[self._options_index])
                if self._exit_fn is not None:
                    self._exit_fn()
                if self._exit_key is not None:
                    return self._exit_key
                return -1
        return -1
        