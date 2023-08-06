import shutil

from enum import Enum
from typing import Optional
from .settings import SettingsParser

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


class Symbol:
    opening = "=>"
    neutral = ""
    success = ""
    failure = ""
    wrong = ""
    compilation = ""
    execution = ""
    unequal = ""
    equalbar = ""
    hbar = "─"
    vbar = "│"
    whitespace = "\u2E31"  # interpunct
    newline = "\u21B5"  # carriage return
    cfill = "_"
    tab = "    "

    def __init__(self):
        pass

    @staticmethod
    def initialize(_asc2only: bool):
        # print("Initializing symbols... in " + ("ASCII" if _asc2only else "UTF-8"))
        Symbol.neutral = "." if _asc2only else "»"  # u"\u2610"  # ☐
        Symbol.success = "S" if _asc2only else "✓"
        Symbol.failure = "X" if _asc2only else "✗"
        Symbol.wrong = "W" if _asc2only else "ω"
        Symbol.compilation = "C" if _asc2only else "ϲ"
        Symbol.execution = "E" if _asc2only else "ϵ"
        Symbol.unequal = "#" if _asc2only else "≠"
        Symbol.equalbar = "|" if _asc2only else "│"

        Symbol.opening = Colored.paint(Symbol.opening, Color.BLUE)
        Symbol.neutral = Colored.paint(Symbol.neutral, Color.BLUE)

        Symbol.success = Colored.paint(Symbol.success, Color.GREEN)
        Symbol.failure = Colored.paint(Symbol.failure, Color.RED)
        
        # Symbol.wrong       = Colored.paint(Symbol.wrong,       Color.RED)
        Symbol.compilation = Colored.paint(Symbol.compilation, Color.YELLOW)
        Symbol.execution = Colored.paint(Symbol.execution,   Color.YELLOW)
        Symbol.unequal = Colored.paint(Symbol.unequal,     Color.RED)
        Symbol.equalbar = Colored.paint(Symbol.equalbar,    Color.GREEN)


Symbol.initialize(SettingsParser().get_ascii())  # inicalizacao estatica


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
