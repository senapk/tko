from .ftext import TK

class __Symbols:
    def __init__(self):
        self.opening = TK()
        self.neutral = TK()
        self.success = TK()
        self.failure = TK()
        self.wrong = TK()
        self.compilation = TK()
        self.execution = TK()
        self.unequal = TK()
        self.equalbar = TK()
        self.hbar = TK()
        self.vbar = TK()
        self.whitespace = TK()  # interpunct
        self.newline = TK()  # carriage return
        self.cfill = TK()
        self.tab = TK()
        self.arrow_up = TK()
        self.check = TK()  
        self.uncheck = TK()
        self.opcheck = TK()
        self.opuncheck = TK()

        self.ascii = False
        self.set_unicode()

    def get_mode(self) -> str:
        return "ASCII" if self.ascii else "UTF-8"

    def set_ascii(self):
        self.ascii = True

        self.opening = TK("=> ")
        self.neutral = TK(".")
        self.success = TK("S")
        self.failure = TK("X")
        self.wrong = TK("W")
        self.compilation = TK("C")
        self.execution = TK("E")
        self.unequal = TK("#")
        self.equalbar = TK("|")
        self.hbar = TK("─")
        self.vbar = TK("│")
        self.whitespace = TK("\u2E31")  # interpunct
        self.newline = TK("\u21B5")  # carriage return
        self.cfill = TK("_")
        self.tab = TK("    ")
        self.arrow_up = TK("A")

        self.check = TK("x")
        self.uncheck = TK(".")
        self.opcheck = TK("█")
        self.opuncheck = TK("▒")

    def set_unicode(self):
        self.ascii = False

        self.opening = TK("=> ")
        self.neutral = TK("»")
        self.success = TK("✓")
        self.failure = TK("✗")
        self.wrong = TK("ω")
        self.compilation = TK("ϲ")
        self.execution = TK("ϵ")
        self.unequal = TK("├")
        self.equalbar = TK("│")
        self.hbar = TK("─")
        self.vbar = TK("│")
        self.whitespace = TK("\u2E31")
        self.newline = TK("\u21B5")
        self.cfill = TK("_")
        self.tab = TK("    ")
        self.arrow_up = TK("↑")

        self.check = TK("✓")
        self.uncheck = TK("✗")
        self.opcheck = TK("ⴲ")
        self.opuncheck = TK("ⵔ")


    def set_colors(self):
        self.opening.fmt = "b"
        self.neutral.fmt = "b"
        self.success.fmt = "g"
        self.failure.fmt = "r"
        self.wrong.fmt = "r"
        self.compilation.fmt = "y"
        self.execution.fmt = "y"
        self.unequal.fmt = "r"
        self.equalbar.fmt = "g"


symbols = __Symbols()
