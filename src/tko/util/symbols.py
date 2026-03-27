from tko.util.text import Text

class __Symbols:

    def __init__(self):
        # self.task_downloaded = Text.Token("▼", "g")
        # self.task_to_download = Text.Token("▲")
        # self.task_local = Text.Token("▶", "g")
        
        self.opening = Text.Token("▶")
        self.up_triangle_filled = Text.Token("▲")
        self.up_triangle_void = Text.Token("△")
        self.down_triangle_filled = Text.Token("▼")
        self.down_triangle_void = Text.Token("▽")
        self.right_triangle_filled = Text.Token("▶")
        self.right_triangle_void = Text.Token("▷")
        self.left_triangle_filled = Text.Token("◀")
        self.left_triangle_void = Text.Token("◁")
        self.neutral = Text.Token("»")
        self.success = Text.Token("✓")
        self.failure = Text.Token("✗")
        self.wrong = Text.Token("ω")
        self.compilation = Text.Token("ϲ")
        self.execution = Text.Token("ϵ")
        self.unequal = Text.Token("├")
        self.equalbar = Text.Token("│")
        self.hbar = Text.Token("─")
        self.vbar = Text.Token("│")

        self.execution_result: dict[str, Text.Token] = {
            "untested": self.neutral,
            "success": self.success,
            "wrong_output": self.wrong,
            "compilation_error": self.compilation,
            "execution_error": self.execution,
        }

        self.middle_dot = Text.Token("·") #Text.Token("␣")
        self.newline = Text.Token("↲")

        self.circle_filled = Text.Token("●")
        self.circle_open = Text.Token("○")

        self.square_filled = Text.Token("■")
        self.square_void = Text.Token("□")
    
        self.rounded_square_filled = Text.Token("▣")
        self.rounded_square_void = Text.Token("▢")

        self.diamond_filled = Text.Token("◆")
        self.diamond_void = Text.Token("◇")

        self.star_filled = Text.Token("★")
        self.star_void = Text.Token("☆")

        self.mark_filled = Text.Token("✦", "g")
        self.mark_void = Text.Token("✧", "y")

        self.task_zero = Text.Token("⊘")
        self.task_part = Text.Token("≈")
        self.task_free = Text.Token("=")
        self.task_reload = Text.Token("↺")


        self.task_edit = Text.Token("✎")
        self.task_view = Text.Token("↗")

        self.cfill = Text.Token("_")
        self.tab = Text.Token("    ")

        self.arrow_up = Text.Token("↑")
        self.arrow_down = Text.Token("↓")
        self.arrow_right = Text.Token("→")
        self.arrow_left = Text.Token("←")

        self.check = Text.Token("✓")
        self.uncheck = Text.Token("✗")

        self.infinity = Text.Token("∞")
        self.locked_free = Text.Token("⇉")
        self.locked_locked = Text.Token("⇟")

        self.left_toggle = Text.Token("━─")
        self.right_toggle = Text.Token("─━")


        self.sharp_right = Text.Token("")
        self.sharp_left = Text.Token("")
        self.action = Text.Token("◎", "b")

        # self.emoji_confiante = Text.Token("●", "g")
        # self.emoji_capaz     = Text.Token("◕", "y")
        # self.emoji_inseguro  = Text.Token("◑", "m")
        # self.emoji_confuso   = Text.Token("◔", "r")
        # self.emoji_nao_fiz   = Text.Token("ⵔ")

        # self.emoji_confiante = Text.Token("■", "g")
        # self.emoji_capaz     = Text.Token("◨", "y")
        # self.emoji_inseguro  = Text.Token("◧", "m")
        # self.emoji_confuso   = Text.Token("◱", "r")
        # self.emoji_nao_fiz   = Text.Token("□")

        self.edge_a = Text.Token("▇", "g")
        self.edge_b = Text.Token("▆", "y")
        self.edge_c = Text.Token("▅", "m")
        self.edge_d = Text.Token("▄", "r")
        self.edge_e = Text.Token("▃", "c")
        self.edge_x = Text.Token("▂", "")
        self.edge_list = [self.edge_x, self.edge_e, self.edge_d, self.edge_c, self.edge_b, self.edge_a]

        self.flow_s = Text.Token("S", "b")
        self.flow_a = Text.Token("A", "g")
        self.flow_b = Text.Token("P", "y")
        self.flow_c = Text.Token("G", "y")
        self.flow_d = Text.Token("I", "y")
        self.flow_e = Text.Token("H", "y")
        self.flow_x = Text.Token("x", "")
        self.flow_list = [self.flow_x, self.flow_e, self.flow_d, self.flow_c, self.flow_b, self.flow_a, self.flow_s]
        
        self.cool_a = Text.Token("5", "g")
        self.cool_b = Text.Token("4", "y")
        self.cool_c = Text.Token("3", "m")
        self.cool_d = Text.Token("2", "r")
        self.cool_e = Text.Token("1", "c")
        self.cool_x = Text.Token("x", "")
        self.cool_list = [self.cool_x, self.cool_e, self.cool_d, self.cool_c, self.cool_b, self.cool_a]

        self.cursor = Text.Token("┊")

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
