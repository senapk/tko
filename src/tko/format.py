import shutil

from typing import Optional


class Color:
    enabled = False
    __terminal_styles = {
        '.': '\033[0m', # Reset
        '*': '\033[1m', # Bold
        '/': '\033[3m', # Italic
        '_': '\033[4m', # Underline
        
        'k': '\033[30m', # Black
        'r': '\033[31m', # Red
        'g': '\033[32m', # Green
        'y': '\033[33m', # Yellow
        'b': '\033[34m', # Blue
        'm': '\033[35m', # Magenta
        'c': '\033[36m', # Cyan
        'w': '\033[37m', # White

        'K': '\033[90m', # Bright black
        'R': '\033[91m', # Bright red
        'G': '\033[92m', # Bright green
        'Y': '\033[93m', # Bright yellow
        'B': '\033[94m', # Bright blue
        'M': '\033[95m', # Bright magenta
        'C': '\033[96m', # Bright cyan
        'W': '\033[97m',

        '#k': '\033[40m', # Background black
        '#r': '\033[41m', # Background red
        '#g': '\033[42m', # Background green
        '#y': '\033[43m', # Background yellow
        '#b': '\033[44m', # Background blue
        '#m': '\033[45m', # Background magenta
        '#c': '\033[46m', # Background cyan
        '#w': '\033[47m', # Background white

        '#K': '\033[100m', # Background bright black
        '#R': '\033[101m', # Background bright red
        '#G': '\033[102m', # Background bright green
        '#Y': '\033[103m', # Background bright yellow
        '#B': '\033[104m', # Background bright blue
        '#M': '\033[105m', # Background bright magenta
        '#C': '\033[106m', # Background bright cyan
        '#W': '\033[107m'  # Background bright white
    }
    __replacements = {
        'black': 'k',
        'red': 'r',
        'green': 'g',
        'yellow': 'y',
        'blue': 'b',
        'magenta': 'm',
        'cyan': 'c',
        'white': 'w',
        'bright_black': 'K',
        'bright_red': 'R',
        'bright_green': 'G',
        'bright_yellow': 'Y',
        'bright_blue': 'B',
        'bright_magenta': 'M',
        'bright_cyan': 'C',
        'bright_white': 'W', 
        'reset': '.',
        'bold': '*',
        'italic': '/',
        'underline': '_',
    }

    @staticmethod
    def get_style(modifier: str):
        if modifier in Color.__replacements:
            modifier = Color.__replacements[modifier]
        if modifier in Color.__terminal_styles:
            return Color.__terminal_styles[modifier]
        print(f'Unknown modifier: {modifier}')
        return ''

    @staticmethod
    def ljust(text: str, width: int) -> str:
        return text + " " * (width - Color.len(text))

    @staticmethod
    def center(text: str, width: int, filler: str) -> str:
        before = filler * ((width - Color.len(text)) // 2)
        after = filler * ((width - Color.len(text) + 1) // 2)
        return before + text + after

    @staticmethod
    def remove_colors(text: str) -> str:
        for color in Color.__terminal_styles.values():
            text = text.replace(color, "")
        return text

    @staticmethod
    def len(text):
        return len(Color.remove_colors(text))


def colour(modifiers: str, text: str) -> str:
    if not Color.enabled:
        return text
    mod = modifiers.split(',')
    output = ''
    for m in [v for v in mod if v != '']:
        val = Color.get_style(m.strip())
        if val != '':
            output += val
    output += text + Color.get_style('reset')
    return output

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
        self.opcheck = "█"
        self.opuncheck = "▒"

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

def green(text: str):
    return colour("g", text)

def red(text: str):
    return colour("r", text)

def yellow(text: str):
    return colour("y", text)

def magenta(text: str):
    return colour("m", text)

def cyan(text: str):
    return colour("c", text)


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
