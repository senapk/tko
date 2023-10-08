import shutil

from enum import Enum
from typing import Optional

class Color(Enum):
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7
    RESET = 8
    BOLD = 9
    ULINE = 10


class Colored:
    enabled = False

    __map = {
        Color.RED: '\u001b[31m',
        Color.GREEN: '\u001b[32m',
        Color.YELLOW: '\u001b[33m',
        Color.BLUE: '\u001b[34m',
        Color.MAGENTA: '\u001b[35m',
        Color.CYAN: '\u001b[36m',
        Color.WHITE: '\u001b[37m',
        Color.RESET: '\u001b[0m',
        Color.BOLD: '\u001b[1m',
        Color.ULINE: '\u001b[4m'
    }

    @staticmethod
    def paint(text: str, color: Color, color2: Optional[Color] = None) -> str:
        if not Colored.enabled:
            return text
        return (Colored.__map[color] + ("" if color2 is None else Colored.__map[color2])
                + text + Colored.__map[Color.RESET])

    @staticmethod
    def green(text: str) -> str:
        return Colored.paint(text, Color.GREEN)
    
    @staticmethod
    def red(text: str) -> str:
        return Colored.paint(text, Color.RED)
    
    @staticmethod
    def magenta(text: str) -> str:
        return Colored.paint(text, Color.MAGENTA)

    @staticmethod
    def yellow(text: str) -> str:
        return Colored.paint(text, Color.YELLOW)
    
    @staticmethod
    def blue(text: str) -> str:
        return Colored.paint(text, Color.BLUE)

    @staticmethod
    def ljust(text: str, width: int) -> str:
        return text + ' ' * (width - Colored.len(text))

    @staticmethod
    def center(text: str, width: int, filler: str) -> str:
        return filler * ((width - Colored.len(text)) // 2) + text + filler * ((width - Colored.len(text) + 1) // 2)

    @staticmethod
    def remove_colors(text: str) -> str:
        for color in Colored.__map.values():
            text = text.replace(color, '')
        return text

    @staticmethod
    def len(text):
        return len(Colored.remove_colors(text))


class __Symbols:
    def __init__(self):
        self.opening     = ""
        self.neutral     = ""
        self.success     = ""
        self.failure     = ""
        self.wrong       = ""
        self.compilation = ""
        self.execution   = ""
        self.unequal     = ""
        self.equalbar    = ""
        self.hbar        = ""
        self.vbar        = ""
        self.whitespace  = ""  # interpunct
        self.newline     = ""  # carriage return
        self.cfill       = ""
        self.tab         = ""
        self.arrow_up    = ""

        self.ascii = False
        self.set_unicode()

    def get_mode(self) -> str:
        return "ASCII" if self.ascii else "UTF-8"

    def set_ascii(self):
        self.ascii = True

        self.opening     = "=> "
        self.neutral     = "."
        self.success     = "S"
        self.failure     = "X"
        self.wrong       = "W"
        self.compilation = "C"
        self.execution   = "E"
        self.unequal     = "#"
        self.equalbar    = "|"
        self.hbar        = "─"
        self.vbar        = "│"
        self.whitespace  = "\u2E31"  # interpunct
        self.newline     = "\u21B5"  # carriage return
        self.cfill       = "_"
        self.tab         = "    "
        self.arrow_up    = "A"

    def set_unicode(self):
        self.ascii = False

        self.opening     = "=> "
        self.neutral     = "»"
        self.success     = "✓"
        self.failure     = "✗"
        self.wrong       = "ω"
        self.compilation = "ϲ"
        self.execution   = "ϵ"
        self.unequal     = "├"
        self.equalbar    = "│"
        self.hbar        = "─"
        self.vbar        = "│"
        self.whitespace  = "\u2E31"  # interpunct
        self.newline     = "\u21B5"  # carriage return
        self.cfill       = "_"
        self.tab         = "    "
        self.arrow_up    = "↑"

    def set_colors(self):
        self.opening     = Colored.paint(self.opening,     Color.BLUE)
        self.neutral     = Colored.paint(self.neutral,     Color.BLUE)
        self.success     = Colored.paint(self.success,     Color.GREEN)
        self.failure     = Colored.paint(self.failure,     Color.RED)
        self.wrong       = Colored.paint(self.wrong,       Color.RED)
        self.compilation = Colored.paint(self.compilation, Color.YELLOW)
        self.execution   = Colored.paint(self.execution,   Color.YELLOW)
        self.unequal     = Colored.paint(self.unequal,     Color.RED)
        self.equalbar    = Colored.paint(self.equalbar,    Color.GREEN)

symbols = __Symbols()


class Report:
    __term_width: Optional[int] = None

    def __init__(self):
        pass

    @staticmethod
    def update_terminal_size():
        term_width = shutil.get_terminal_size().columns
        if term_width % 2 == 0:
            term_width -= 1
        Report.__term_width = term_width

    @staticmethod
    def get_terminal_size():
        if Report.__term_width is None:
            Report.update_terminal_size()

        return Report.__term_width

    @staticmethod
    def set_terminal_size(value: int):
        if value % 2 == 0:
            value -= 1
        Report.__term_width = value

    @staticmethod
    def centralize(text, sep=' ', left_border: Optional[str] = None, right_border: Optional[str] = None) -> str:
        if left_border is None:
            left_border = sep
        if right_border is None:
            right_border = sep
        term_width = Report.get_terminal_size()

        size = Colored.len(text)
        pad = sep if size % 2 == 0 else ""
        tw = term_width - 2
        filler = sep * int(tw / 2 - size / 2)
        return left_border + pad + filler + text + filler + right_border
