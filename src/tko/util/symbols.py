from .term_color import colour

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
        self.uncheck = "."
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
