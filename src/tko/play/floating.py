from typing import List
from .frame import Frame
from ..util.text import Text
from .fmt import Fmt
import curses
from abc import ABC

class Floating:
    def __init__(self, _align=""):
        self._frame = Frame(0, 0)
        self._content: List[Text] = []
        self._type = "warning"
        self._fn_answer = None
        self._enable = True
        self._extra_exit: List[int] = []
        self._exit_fn = None
        self._exit_key = None
        self._centralize = True
        self._floating_align = _align

    def disable(self):
        self._enable = False

    def set_text_ljust(self):
        self._centralize = False
        return self

    def set_text_center(self):
        self._centralize = True
        return self

    def set_frame_align(self, _align: str):
        self._floating_align = _align
        return self

    def set_header(self, text: str):
        self._frame.set_header(Text().addf("/", text), "")
        return self
    
    def set_header_sentence(self, sentence: Text):
        self._frame.set_header(sentence, "")
        return self
    
    def set_footer(self, text: str):
        self._frame.set_footer(Text().addf("/", text), "")
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
            y = lines - dy - 5

        self._frame.set_pos(y, x)
        return self
            
    def is_enable(self):
        return self._enable

    def calc_dy_dx(self):
        header_len = self._frame.get_header().len()
        footer_len = self._frame.get_footer().len()
        data = [x.len() for x in self._content] + [header_len, footer_len]
        max_dx = max(data)
        dx = max_dx
        dy = len(self._content)
        return dy, dx

    def setup_frame(self):
        dy, dx = self.calc_dy_dx()
        self._frame.set_inner(dy, dx)
        self._set_xy(dy, dx)
        self._frame.set_fill()

    def put_text(self, text: str):
        lines = text.split("\n")
        for line in lines:
            self._content.append(Text().add(line))
        return self

    def put_sentence(self, sentence: Text):
        for line in sentence.split("\n"):
            self._content.append(line)
        return self
    
    def set_content(self, content: List[str]):
        self._content = [Text().add(x) for x in content]
        return self

    def _set_default_footer(self):
        if self._frame.get_footer().len() == 0:
            label = Text().addf("/", " Pressione espaço ")
            self._frame.set_footer(label, "", "─", "─")
        return self

    def _set_default_header(self):
        if self._frame.get_header().len() == 0:
            if self._type == "warning":
                self.set_header(" Aviso ")
            elif self._type == "error":
                self.set_header(" Erro ")

    def warning(self):
        self._type = "warning"
        self._frame.set_border_color("y")
        return self
    
    def error(self):
        self._type = "error"
        self._frame.set_border_color("r")
        return self
    
    def answer(self, fn_answer):
        self._type = "answer"
        self._frame.set_border_color("g")
        self._fn_answer = fn_answer
        return self

    def draw(self):
        self._set_default_header()
        self._set_default_footer()
        self.setup_frame()
        self._frame.draw()
        self.write_content()

    def write_content(self):
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
                if key == ord(" ") or key == 27:
                    return -1
                return key
        
        return -1
        
class FloatingInput(Floating):
    def __init__(self, _align=""):
        super().__init__(_align)
        self._input = ""
        self._max_input = 100
        self._fn_input = None
        self._options_index = 0

    def calc_dy_dx(self):
        dy, dx = super().calc_dy_dx()
        dy += len(self._options)
        return dy, dx

    def write_content(self):
        options: List[Text] = []
        for i, option in enumerate(self._options):
            fmt = "kG" if i == self._options_index else ""
            options.append(Text().addf(fmt, option))
            
        y = 0
        for line in self._content + options:
            x = 0
            if self._centralize:
                x = (self._frame.get_dx() - line.len()) // 2
            self._frame.write(y, x, line)
            y += 1

        return self

    def set_options(self, options: List[str]):
        self._options = options
        return self
    
    def set_default_index(self, index: int):
        self._options_index = index
        return self

    def get_input(self) -> int:
        self.draw()
        key: int = Fmt.getch()
        
        if key == curses.KEY_UP:
            self._options_index = (self._options_index - 1) % len(self._options)
        elif key == curses.KEY_DOWN:
            self._options_index = (self._options_index + 1) % len(self._options)
        elif key == 27:
            self._enable = False
        elif key == ord('\n'):
            self._enable = False
            if self._fn_answer is not None:
                self._fn_answer(self._options[self._options_index])
            if self._exit_fn is not None:
                self._exit_fn()
            if self._exit_key is not None:
                return self._exit_key
            return -1
        else:
            return key
        return -1