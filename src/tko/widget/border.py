from tko.util.rtext import RText
from tko.config.app_settings import AppSettings
from tko.util.symbols import Symbols


class Border:
    def __init__(self, app: AppSettings):
        self.app = app

    def has_borders(self):
        return self.app.use_borders

    def border(self, color: str, data: str):
        return self.round_l(color) + RText(data, color) + self.round_r(color)

    def border_sharp(self, color: str, data: str):
        return self.sharp_l(color) + RText(data, color) + self.sharp_r(color)

    def round_l(self, color: str) -> RText:
        color = color if color != "X" else ""
        return RText(Symbols.round_left, color.lower()) if self.has_borders() else RText(" ", color)

    def round_r(self, color: str) -> RText:
        color = color if color != "X" else ""
        return RText(Symbols.round_right, color.lower()) if self.has_borders() else RText(" ", color)

    def sharp_l(self, color: str) -> RText:
        color = color if color != "X" else ""
        return RText(Symbols.sharp_left, color.lower()) if self.has_borders() else RText(" ", color)

    def sharp_r(self, color: str):
        color = color if color != "X" else ""
        return RText(Symbols.sharp_right, color.lower()) if self.has_borders() else RText(" ", color)

    def build_bar(self, text: str, percent: float, length: int, fmt_true: str = "/kC",
                  fmt_false: str = "/kY", rounded: bool = True) -> RText:
        if rounded and (len(text) >= length - 2):
            text = " " + text

        if length > len(text):
            prefix = (length - len(text)) // 2
            suffix = length - len(text) - prefix
            text = " " * prefix + text + " " * suffix
        elif length < len(text):
            text = text[:length]

        full_line: str = text
        done_len: int = round(percent * length)
        xp_bar = RText(full_line[:done_len], fmt_true) + RText(full_line[done_len:], fmt_false)

        if rounded and length == 1:
            first_style = xp_bar[0].runs[0][0] if xp_bar[0].runs else ""
            xp_bar = self.round_l(first_style)
        elif rounded and length > 1:
            first_style = xp_bar[0].runs[0][0] if xp_bar[0].runs else ""
            last_style = xp_bar[-1].runs[0][0] if xp_bar[-1].runs else ""
            middle = xp_bar.slice(1, max(1, len(xp_bar) - 1))
            xp_bar = self.round_l(first_style) + middle + self.round_r(last_style)
        return xp_bar
