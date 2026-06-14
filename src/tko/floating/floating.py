from __future__ import annotations
from dataclasses import dataclass
from tko.widget.frame import Frame
from tko.util.rt import RT
from tko.widget.fmt import Fmt
from tko.i18n import Msg
from typing import Callable
import enum
import curses
from abc import ABC, abstractmethod
from tko.util.countdown import Countdown

_FLOATING_INVALID_ALIGN = Msg(
    pt="Invalid align {align}",
    en="Invalid align {align}",
)


class FloatingType(enum.Enum):
    WARNING = "warning"
    ERROR = "error"


class FloatingABC(ABC):
    def __init__(self):
        self.id = ""

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def process_input(self, key: int) -> int:
        pass

    @abstractmethod
    def is_enable(self) -> bool:
        pass


class AlignY(enum.Enum):
    center = "center"
    top = "top"
    bottom = "bottom"

class AlignX(enum.Enum):
    center = "center"
    left = "left"
    right = "right"

@dataclass(frozen=True)
class Position:
    align_y: AlignY
    align_x: AlignX
    offset_y: int = 0
    offset_x: int = 0

class Floating(FloatingABC):
    class Time:
        FAST = 20
        MEDIUM = 45
        SLOW = 70

    def __init__(self):
        super().__init__()
        self.frame = Frame(0, 0)
        self.content: list[RT] = []
        self.type: FloatingType = FloatingType.WARNING
        self.enable = True
        self.exit_fn: Callable[[], None] | None = None
        self.exit_key: None | int = None
        self.centralize_text = True
        self.floating_align: Position = Position(AlignY.center, AlignX.center)

        self.counting_enable = False
        self.counting = 0
        self.max_count = 30
        self.frame.countdown_fn = lambda: RT() if not self.counting_enable else RT(Countdown.braille(self.counting, self.max_count, 5), "y")

    def set_countdown(self, max_count: int = 30):
        self.counting_enable = True
        self.counting = 0
        self.max_count = max_count
        return self

    def disable(self):
        self.enable = False

    def set_text_ljust(self):
        self.centralize_text = False
        return self

    def set_text_center(self):
        self.centralize_text = True
        return self

    def set_frame_position(self, pos: Position):
        self.floating_align = pos
        return self
    
    def set_offsets(self, offset_y: int = 0, offset_x: int = 0):
        fa = self.floating_align
        self.floating_align = Position(align_y=fa.align_y, align_x=fa.align_x, offset_y=offset_y, offset_x=offset_x)
        return self
    
    def left(self):
        fa = self.floating_align
        self.floating_align = Position(align_x=AlignX.left, align_y=fa.align_y, offset_x= fa.offset_x, offset_y=fa.offset_y)
        return self
    
    def right(self):
        fa = self.floating_align
        self.floating_align = Position(align_x=AlignX.right, align_y=fa.align_y, offset_x= fa.offset_x, offset_y=fa.offset_y)
        return self
    
    def top(self):
        fa = self.floating_align
        self.floating_align = Position(align_x=fa.align_x, align_y=AlignY.top, offset_x= fa.offset_x, offset_y=fa.offset_y)
        return self
    
    def bottom(self):
        fa = self.floating_align
        self.floating_align = Position(align_x=fa.align_x, align_y=AlignY.bottom, offset_x= fa.offset_x, offset_y=fa.offset_y)
        return self

    def set_header(self, text: str):
        self.frame.set_header(RT(text, "/"), "")
        return self
    
    def set_header_text(self, sentence: RT):
        self.frame.set_header(sentence, "")
        return self
    
    def set_footer(self, text: str):
        self.frame.set_footer(RT(text, "/"), "")
        return self
    
    def set_footer_text(self, sentence: RT):
        self.frame.set_footer(sentence, "")
        return self
    
    def set_exit_key(self, key: str):
        self.exit_key = ord(key)
        return self

    def set_exit_fn(self, fn: Callable[[], None]):
        self.exit_fn = fn
        return self

    def _set_xy(self, dy: int, dx: int):
        lines, cols = Fmt.get_lines_cols()

        x = (cols - dx) // 2
        if self.floating_align.align_x == AlignX.left:
            x = 1
        elif self.floating_align.align_x == AlignX.right:
            x = cols - dx - 2

        y = (lines - dy) // 2
        if self.floating_align.align_y == AlignY.top:
            y = 1
        elif self.floating_align.align_y == AlignY.bottom:
            y = lines - dy - 2
        y += self.floating_align.offset_y
        x += self.floating_align.offset_x

        self.frame.set_pos(y, x)
        return self
            
    def is_enable(self):
        return self.enable

    def calc_dy_dx(self):
        header_len = len(self.frame.get_header())
        footer_len = len(self.frame.get_footer())
        data = [len(x) for x in self.content] + [header_len, footer_len]
        max_dx = max(data)
        dx = max_dx
        dy = len(self.content)
        return dy, dx

    def setup_frame(self):
        dy, dx = self.calc_dy_dx()
        self.frame.set_inner(dy, dx)
        self._set_xy(dy, dx)
        self.frame.set_fill()

    def put_text(self, text: str | RT):
        if isinstance(text, str):
            text = RT(text)
        lines = text.splitlines()
        for line in lines:
            self.content.append(line)
        return self

    def put_sentence(self, sentence: RT):
        for line in sentence.split('\n'):
            self.content.append(line)
        return self
    
    def set_content(self, content: list[str]):
        self.content = [RT(x) for x in content]
        return self
    
    def set_content_rt(self, content: list[RT]):
        self.content = content
        return self

    def set_default_footer(self):
        if len(self.frame.get_footer()) == 0:
            label = RT(" Pressione espaço ", "/")
            self.frame.set_footer(label, "", "─", "─")
        return self

    def set_default_header(self):
        if len(self.frame.get_header()) == 0:
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
                x = (self.frame.get_dx() - len(line)) // 2
            self.frame.write(y, x, line)
            y += 1
        return self

    def process_input(self, key: int) -> int:
        if key == -1:
            if self.counting_enable:
                self.counting += 1
                if self.counting >= self.max_count:
                    self.enable = False
                    if self.exit_fn is not None:
                        self.exit_fn()
            return -1
        
        if self.type == FloatingType.WARNING or self.type == FloatingType.ERROR:
            if key == curses.KEY_RESIZE:
                return -1
            self.enable = False
            if self.exit_fn is not None:
                self.exit_fn()
            if self.exit_key is not None:
                return self.exit_key
            if key == ord(" ") or key == curses.KEY_EXIT:
                return -1
            return key
        return -1
