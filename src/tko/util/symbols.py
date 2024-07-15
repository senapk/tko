from .ftext import Token

class __Symbols:
    def __init__(self):
        self.opening = Token()
        self.neutral = Token()
        self.success = Token()
        self.failure = Token()
        self.wrong = Token()
        self.compilation = Token()
        self.execution = Token()
        self.unequal = Token()
        self.equalbar = Token()
        self.hbar = Token()
        self.vbar = Token()
        self.whitespace = Token()  # interpunct
        self.newline = Token()  # carriage return
        self.cfill = Token()
        self.tab = Token()
        self.arrow_up = Token()
        self.check = Token()  
        self.uncheck = Token()
        self.opcheck = Token()
        self.opuncheck = Token()

        self.ascii = False
        self.set_unicode()

    def get_mode(self) -> str:
        return "ASCII" if self.ascii else "UTF-8"

    def set_ascii(self):
        self.ascii = True

        self.opening = Token("=> ")
        self.neutral = Token(".")
        self.success = Token("S")
        self.failure = Token("X")
        self.wrong = Token("W")
        self.compilation = Token("C")
        self.execution = Token("E")
        self.unequal = Token("#")
        self.equalbar = Token("|")
        self.hbar = Token("─")
        self.vbar = Token("│")
        self.whitespace = Token("\u2E31")  # interpunct
        self.newline = Token("\u21B5")  # carriage return
        self.cfill = Token("_")
        self.tab = Token("    ")
        self.arrow_up = Token("A")

        self.check = Token("x")
        self.uncheck = Token(".")
        self.opcheck = Token("█")
        self.opuncheck = Token("▒")

    def set_unicode(self):
        self.ascii = False

        self.opening = Token("=> ")
        self.neutral = Token("»")
        self.success = Token("✓")
        self.failure = Token("✗")
        self.wrong = Token("ω")
        self.compilation = Token("ϲ")
        self.execution = Token("ϵ")
        self.unequal = Token("├")
        self.equalbar = Token("│")
        self.hbar = Token("─")
        self.vbar = Token("│")
        self.whitespace = Token("\u2E31")
        self.newline = Token("\u21B5")
        self.cfill = Token("_")
        self.tab = Token("    ")
        self.arrow_up = Token("↑")

        self.check = Token("✓")
        self.uncheck = Token("✗")
        self.opcheck = Token("ⴲ")
        self.opuncheck = Token("ⵔ")


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
