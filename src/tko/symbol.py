from .colored import Colored, Color

asc2only: bool = False


class Symbol:
    opening = "=>"
    neutral = ""
    success = ""
    failure = ""
    wrong = ""
    compilation = ""
    execution = ""
    unequal = ""
    equalbar= ""
    hbar = "─"
    vbar = "│"
    whitespace = "\u2E31"  # interpunct
    newline = "\u21B5"  # carriage return
    cfill = "_"
    tab = "    "

    def __init__(self):
        pass

    @staticmethod
    def initialize(asc2only: bool):
        Symbol.neutral = "." if asc2only else "»"  # u"\u2610"  # ☐
        Symbol.success = "S" if asc2only else "✓"
        Symbol.failure = "X" if asc2only else "✗"
        Symbol.wrong = "W" if asc2only else "ω"
        Symbol.compilation = "C" if asc2only else "ϲ"
        Symbol.execution = "E" if asc2only else "ϵ"
        Symbol.unequal = "#" if asc2only else "≠"
        Symbol.equalbar = "|" if asc2only else "│"

        Symbol.opening = Colored.paint(Symbol.opening, Color.BLUE)
        Symbol.neutral = Colored.paint(Symbol.neutral, Color.BLUE)

        Symbol.success = Colored.paint(Symbol.success, Color.GREEN)
        Symbol.failure = Colored.paint(Symbol.failure, Color.RED)
        
        # Symbol.wrong       = Colored.paint(Symbol.wrong,       Color.RED)
        Symbol.compilation = Colored.paint(Symbol.compilation, Color.YELLOW)
        Symbol.execution = Colored.paint(Symbol.execution,   Color.YELLOW)
        Symbol.unequal = Colored.paint(Symbol.unequal,     Color.RED)
        Symbol.equalbar = Colored.paint(Symbol.equalbar,    Color.GREEN)


Symbol.initialize(asc2only)  # inicalizacao estatica
