from .text import Token

class __Symbols:

    def __init__(self):
        self.downloaded = Token("▼")
        self.to_download = Token("▽")
        self.cant_download = Token("◉")
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

        self.whitespace = Token("·")
        # self.whitespace = Token("␣")
        
        # self.newline = Token("¶")
        self.newline = Token("↲")
        # self.newline = Token("⏎")

        self.cfill = Token("_")
        self.tab = Token("    ")
        self.arrow_up = Token("↑")

        self.check = Token("✓")
        self.uncheck = Token("✗")
        # self.opcheck = Token("ⴲ")
        # self.opuncheck = Token("ⵔ")
        self.infinity = Token("∞")
        self.locked_free = Token("⇉")
        self.locked_locked = Token("⇟")
        self.left_toggle = Token("━─")
        self.right_toggle = Token("─━")
        self.timer = Token("⏰") # ⌛⏰
        self.diff_down = Token("⇕")
        self.diff_left = Token("⇔")
        self.sharpR = Token("")
        self.sharpL = Token("")
        self.action = Token("◎", "b")

        self.emoji_vazio = Token("✗", "r") #"❌"
        self.emoji_confiante = Token("●", "g")#"😎"
        self.emoji_capaz     = Token("◕", "y")#"😌"
        self.emoji_inseguro  = Token("◑", "m")#"😬"
        self.emoji_confuso   = Token("◔", "r")#"😕"

        self.emoji_alone = Token("A", "g")#"💖" # "✋"
        self.emoji_dicas = Token("B", "y") # "💡"
        self.emoji_codes = Token("C", "m")#"💚" #"🤝"
        self.emoji_guide = Token("D", "r")#"💙" # "🧭"
        self.cursor = Token("┊")

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
