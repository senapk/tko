import shutil

from typing import Optional


class Color:
    enabled = False
    map = {
        "red": "\u001b[31m",
        "r": "\u001b[31m",
        "green": "\u001b[32m",
        "g": "\u001b[32m",
        "yellow": "\u001b[33m",
        "y": "\u001b[33m",
        "blue": "\u001b[34m",
        "b": "\u001b[34m",
        "magenta": "\u001b[35m",
        "m": "\u001b[35m",
        "cyan": "\u001b[36m",
        "c": "\u001b[36m",
        "white": "\u001b[37m",
        "w": "\u001b[37m",
        "reset": "\u001b[0m",
        "bold": "\u001b[1m",
        "uline": "\u001b[4m",
    }

    @staticmethod
    def ljust(text: str, width: int) -> str:
        return text + " " * (width - Color.len(text))

    @staticmethod
    def center(text: str, width: int, filler: str) -> str:
        return (
            filler * ((width - Color.len(text)) // 2)
            + text
            + filler * ((width - Color.len(text) + 1) // 2)
        )

    @staticmethod
    def remove_colors(text: str) -> str:
        for color in Color.map.values():
            text = text.replace(color, "")
        return text

    @staticmethod
    def len(text):
        return len(Color.remove_colors(text))


def colour(color: str, text: str, color2: Optional[str] = None) -> str:
    if not Color.enabled:
        return text
    return ("" if color2 is None else Color.map[color2]) + Color.map[color] + text + Color.map["reset"]


class __Symbols:
    def __init__(self):
        self.opening = ""
        self.neutral = ""
        self.success = ""
        self.failure = ""
        self.wrong = ""
        self.compilation = ""
        self.execution = ""
        self.unequal = ""
        self.equalbar = ""
        self.hbar = ""
        self.vbar = ""
        self.whitespace = ""  # interpunct
        self.newline = ""  # carriage return
        self.cfill = ""
        self.tab = ""
        self.arrow_up = ""
        self.check = ""  
        self.uncheck = ""
        self.opcheck = ""
        self.opuncheck = ""

        self.ascii = False
        self.set_unicode()

    def get_mode(self) -> str:
        return "ASCII" if self.ascii else "UTF-8"

    def set_ascii(self):
        self.ascii = True

        self.opening = "=> "
        self.neutral = "."
        self.success = "S"
        self.failure = "X"
        self.wrong = "W"
        self.compilation = "C"
        self.execution = "E"
        self.unequal = "#"
        self.equalbar = "|"
        self.hbar = "─"
        self.vbar = "│"
        self.whitespace = "\u2E31"  # interpunct
        self.newline = "\u21B5"  # carriage return
        self.cfill = "_"
        self.tab = "    "
        self.arrow_up = "A"

        self.check = "x"  
        self.uncheck = " "
        self.opcheck = "█"# ▄ 	▅ 	▆ 	▇ 	█ 
        self.opuncheck = "▒" # ▒

    def set_unicode(self):
        self.ascii = False

        self.opening = "=> "
        self.neutral = "»"
        self.success = "✓"
        self.failure = "✗"
        self.wrong = "ω"
        self.compilation = "ϲ"
        self.execution = "ϵ"
        self.unequal = "├"
        self.equalbar = "│"
        self.hbar = "─"
        self.vbar = "│"
        self.whitespace = "\u2E31"  # interpunct
        self.newline = "\u21B5"  # carriage return
        self.cfill = "_"
        self.tab = "    "
        self.arrow_up = "↑"

        self.check = "✓"  
        self.uncheck = "✗"
        self.opcheck = "ⴲ"
        self.opuncheck = "ⵔ"


    def set_colors(self):
        self.opening = colour("b", self.opening)
        self.neutral = colour("b", self.neutral)
        self.success = colour("g", self.success)
        self.failure = colour("r", self.failure)
        self.wrong = colour("r", self.wrong)
        self.compilation = colour("y", self.compilation)
        self.execution = colour("y", self.execution)
        self.unequal = colour("r", self.unequal)
        self.equalbar = colour("g", self.equalbar)


symbols = __Symbols()

def green(text):
    return colour("g", text)


def red(text):
    return colour("r", text)


def yellow(text):
    return colour("y", text)


def cyan(text):
    return colour("c", text)


def bold(color: str, text: str) -> str:
    return colour(color, text, "bold")


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
    def centralize(
        text,
        sep=" ",
        left_border: Optional[str] = None,
        right_border: Optional[str] = None,
    ) -> str:
        if left_border is None:
            left_border = sep
        if right_border is None:
            right_border = sep
        term_width = Report.get_terminal_size()

        size = Color.len(text)
        pad = sep if size % 2 == 0 else ""
        tw = term_width - 2
        filler = sep * int(tw / 2 - size / 2)
        return left_border + pad + filler + text + filler + right_border
