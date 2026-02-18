from tko.play.frame import Frame
from tko.util.text import Text
from tko.play.fmt import Fmt
from typing import Callable
import enum
import curses
from abc import ABC, abstractmethod


class FloatingType(enum.Enum):
    WARNING = "warning"
    ERROR = "error"


class FloatingABC(ABC):
    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def process_input(self, key: int) -> int:
        pass

    @abstractmethod
    def is_enable(self) -> bool:
        pass

class Floating(FloatingABC):
    def __init__(self, _align: str = ""):
        self.frame = Frame(0, 0)
        self.content: list[Text] = []
        self.type: FloatingType = FloatingType.WARNING
        self.enable = True
        self.extra_exit: list[int] = []
        self.exit_fn: Callable[[], None] | None = None
        self.exit_key: None | int = None
        self.centralize_text = True
        self.floating_align = _align

    def disable(self):
        self.enable = False

    def set_text_ljust(self):
        self.centralize_text = False
        return self

    def set_text_center(self):
        self.centralize_text = True
        return self

    def set_frame_align(self, _align: str):
        self.floating_align = _align
        return self

    def set_header(self, text: str):
        self.frame.set_header(Text().addf("/", text), "")
        return self
    
    def set_header_text(self, sentence: Text):
        self.frame.set_header(sentence, "")
        return self
    
    def set_footer(self, text: str):
        self.frame.set_footer(Text().addf("/", text), "")
        return self
    
    def set_footer_text(self, sentence: Text):
        self.frame.set_footer(sentence, "")
        return self
    
    def set_exit_key(self, key: str):
        self.exit_key = ord(key)
        return self

    def set_exit_fn(self, fn: Callable[[], None]):
        self.exit_fn = fn
        return self

    def _set_xy(self, dy: int, dx: int):
        valid = "<>^v"
        for c in self.floating_align:
            if c not in valid:
                raise ValueError("Invalid align " + c)

        lines, cols = Fmt.get_size()

        x = (cols - dx) // 2
        if "<" in self.floating_align:
            x = 1
        elif ">" in self.floating_align:
            x = cols - dx - 2

        y = (lines - dy) // 2
        if "^" in self.floating_align:
            y = 1
        elif "v" in self.floating_align:
            y = lines - dy - 2

        self.frame.set_pos(y, x)
        return self
            
    def is_enable(self):
        return self.enable

    def calc_dy_dx(self):
        header_len = self.frame.get_header().len()
        footer_len = self.frame.get_footer().len()
        data = [x.len() for x in self.content] + [header_len, footer_len]
        max_dx = max(data)
        dx = max_dx
        dy = len(self.content)
        return dy, dx

    def setup_frame(self):
        dy, dx = self.calc_dy_dx()
        self.frame.set_inner(dy, dx)
        self._set_xy(dy, dx)
        self.frame.set_fill()

    def put_text(self, text: str):
        lines = text.splitlines()
        for line in lines:
            self.content.append(Text().add(line))
        return self

    def put_sentence(self, sentence: Text):
        for line in sentence.split('\n'):
            self.content.append(line)
        return self
    
    def set_content(self, content: list[str]):
        self.content = [Text().add(x) for x in content]
        return self

    def set_default_footer(self):
        if self.frame.get_footer().len() == 0:
            label = Text().addf("/", " Pressione espaço ")
            self.frame.set_footer(label, "", "─", "─")
        return self

    def set_default_header(self):
        if self.frame.get_header().len() == 0:
            if self.type == FloatingType.WARNING:
                self.set_header(" Aviso ")
            elif self.type == FloatingType.ERROR:
                self.set_header(" Erro ")

    def set_warning(self):
        self.type = FloatingType.WARNING
        self.frame.set_border_color("y")
        return self


    def set_error(self):
        self.type = FloatingType.ERROR
        self.frame.set_border_color("r")
        return self

    def draw(self):
        self.set_default_header()
        self.set_default_footer()
        self.setup_frame()
        self.frame.draw()
        self.write_content()

    def write_content(self):
        y = 0
        for line in self.content:
            x = 0
            if self.centralize_text:
                x = (self.frame.get_dx() - line.len()) // 2
            self.frame.write(y, x, line)
            y += 1
        return self

    def process_input(self, key: int) -> int:
        if self.type == FloatingType.WARNING or self.type == FloatingType.ERROR:
            if key < 300 or key == curses.KEY_EXIT:
                self.enable = False
                if self.exit_fn is not None:
                    self.exit_fn()
                if self.exit_key is not None:
                    return self.exit_key
                if key == ord(" ") or key == curses.KEY_EXIT: # evita propagar a tecla
                    return -1
                return key
        
        return -1
