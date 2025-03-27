from .text import Token

class __Symbols:

    def __init__(self):
        self.set_unicode()
        # self.set_ascii()

    def set_unicode(self):
        self.task_downloaded = Token("▼", "g")
        self.task_to_download = Token("▲")
        self.task_local = Token("▶", "g")
        self.task_to_visit = Token("◉", "b")
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

        self.whitespace = Token("·") #Token("␣")
        self.newline = Token("↲")

        self.cfill = Token("_")
        self.tab = Token("    ")
        self.arrow_up = Token("↑")

        self.check = Token("✓")
        self.uncheck = Token("✗")

        self.infinity = Token("∞")
        self.locked_free = Token("⇉")
        self.locked_locked = Token("⇟")
        self.left_toggle = Token("━─")
        self.right_toggle = Token("─━")
        self.timer = Token("⏳") #⏰
        self.diff_down = Token("↓")
        self.diff_left = Token("→")
        self.sharpR = Token("")
        self.sharpL = Token("")
        self.action = Token("◎", "b")

        # self.emoji_confiante = Token("●", "g")
        # self.emoji_capaz     = Token("◕", "y")
        # self.emoji_inseguro  = Token("◑", "m")
        # self.emoji_confuso   = Token("◔", "r")
        # self.emoji_nao_fiz   = Token("ⵔ")

        # self.emoji_confiante = Token("■", "g")
        # self.emoji_capaz     = Token("◨", "y")
        # self.emoji_inseguro  = Token("◧", "m")
        # self.emoji_confuso   = Token("◱", "r")
        # self.emoji_nao_fiz   = Token("□")

        self.autonomy_a = Token("▇", "g")
        self.autonomy_b = Token("▆", "y")
        self.autonomy_c = Token("▅", "m")
        self.autonomy_d = Token("▄", "r")
        self.autonomy_e = Token("▂", "c")
        self.autonomy_x = Token("▁", "")
        self.autonomy_list = [self.autonomy_x, self.autonomy_e, self.autonomy_d, self.autonomy_c, self.autonomy_b, self.autonomy_a]

        self.approach_a = Token("A", "g")
        self.approach_b = Token("B", "y")
        self.approach_c = Token("C", "m")
        self.approach_d = Token("D", "r")
        self.approach_e = Token("E", "c")
        self.approach_x = Token("x", "")
        self.approach_list = [self.approach_x, self.approach_e, self.approach_d, self.approach_c, self.approach_b, self.approach_a]
        
        self.cursor = Token("┊")

    # def set_ascii(self):
    #     self.task_downloaded = Token("D", "g")
    #     self.task_to_download = Token("X")
    #     self.task_local = Token(">", "g")
    #     self.task_to_visit = Token("◉", "b")
    #     self.whitespace = Token("¨")
    #     self.newline = Token("~")

    #     self.cfill = Token("_")
    #     self.tab = Token("    ")
    #     self.arrow_up = Token("|")

    #     self.check = Token("A")
    #     self.uncheck = Token("0")

    #     self.infinity = Token("0")
    #     self.locked_free = Token(">")
    #     self.locked_locked = Token("v")
    #     self.left_toggle = Token("━─")
    #     self.right_toggle = Token("─━")
    #     self.timer = Token("l")
    #     self.diff_down = Token("|")
    #     self.diff_left = Token("─")
    #     self.sharpR = Token("")
    #     self.sharpL = Token("")
    #     self.action = Token("◎", "b")

    #     self.emoji_vazio = Token("✗", "r")
    #     self.emoji_confiante = Token("A", "g")
    #     self.emoji_capaz     = Token("B", "y")
    #     self.emoji_inseguro  = Token("C", "m")
    #     self.emoji_confuso   = Token("D", "r")
    #     self.emoji_nao_fiz   = Token("E")

    #     self.emoji_alone = Token("A", "g")
    #     self.emoji_dicas = Token("B", "y")
    #     self.emoji_codes = Token("C", "m")
    #     self.emoji_guide = Token("D", "r")
    #     self.cursor = Token("|")

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
