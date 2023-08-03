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
    __map = {
        Color.RED     : '\u001b[31m',
        Color.GREEN   : '\u001b[32m',
        Color.YELLOW  : '\u001b[33m',
        Color.BLUE    : '\u001b[34m',
        Color.MAGENTA : '\u001b[35m',
        Color.CYAN    : '\u001b[36m',
        Color.WHITE   : '\u001b[37m',
        Color.RESET   : '\u001b[0m',
        Color.BOLD    : '\u001b[1m',
        Color.ULINE   : '\u001b[4m'
    }

    @staticmethod
    def paint(text: str, color: Color, color2: Optional[Color] = None) -> str:
        return Colored.__map[color] + ("" if color2 is None else Colored.__map[color2]) + text + Colored.__map[Color.RESET]

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
    def center(text: str, width: int, filler) -> str:
        return filler * ((width - Colored.len(text)) // 2) + text + filler * ((width - Colored.len(text) + 1) // 2)

    @staticmethod
    def remove_colors(text: str) -> str:
        for color in Colored.__map.values():
            text = text.replace(color, '')
        return text

    @staticmethod
    def len(text):
        return len(Colored.remove_colors(text))
