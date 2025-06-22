from tko.play.flags import Flag
from tko.util.text import Text
from tko.settings.app_settings import AppSettings
from tko.util.symbols import symbols


class Border:
    def __init__(self, app: AppSettings):
        self.app = app

    def has_borders(self):
        return self.app.get_use_borders()

    def border(self, color: str, data: str):
        return Text().add(self.round_l(color)).addf(color, data).add(self.round_r(color))

    def border_sharp(self, color: str, data: str):
        return Text().add(self.sharp_l(color)).addf(color, data).add(self.sharp_r(color))

    def round_l(self, color: str) -> Text.Token:
        return Text.Token("", color.lower()) if self.has_borders() else Text.Token(" ", color)

    def round_r(self, color: str) -> Text.Token:
        return Text.Token("", color.lower()) if self.has_borders() else Text.Token(" ", color)

    def sharp_l(self, color: str) -> Text.Token:
        return Text.Token("", color.lower()) if self.has_borders() else Text.Token(" ", color)

    def sharp_r(self, color: str):
        return Text.Token("", color.lower()) if self.has_borders() else Text.Token(" ", color)

    def build_bar(self, text: str, percent: float, length: int, fmt_true: str = "/kC",
                  fmt_false: str = "/kY", round: bool = True) -> Text:
        if round and (len(text) >= length - 2):
            text = " " + text

        if length > len(text):
            prefix = (length - len(text)) // 2
            suffix = length - len(text) - prefix
            text = " " * prefix + text + " " * suffix
        elif length < len(text):
            text = text[:length]

        full_line = text
        done_len = int(percent * length)
        xp_bar = Text.Token(full_line[:done_len], fmt_true) + Text.Token(full_line[done_len:], fmt_false)

        if round:
            xp_bar.data[0] = self.round_l(xp_bar.data[0].fmt)
            xp_bar.data[-1] = self.round_r(xp_bar.data[-1].fmt)
        return xp_bar

    def get_flag_sentence(self, flag: Flag, pad: int = 0, button_mode: bool = True, include_symbol: bool = True,
                          include_key: bool = True) -> Text:
        char = flag.get_keycode()
        text = flag.get_name()
        color = "M"
        symbol = symbols.neutral
        if len(flag.get_values()) > 0:
            color = "G" if flag else "Y"
            symbol = symbols.success if flag else symbols.failure
        if not button_mode:
            color = color.lower()
        extra = Text()
        filler = " "
        if pad > 2:
            extra.addf(color, (pad - 2 - len(text)) * filler)

        mid = Text()
        if include_symbol:
            mid.addf(color, symbol.text).addf(color, " ")
        mid.addf(color, text)
        if include_key:
            mid.add(extra).addf(color, f"[{char}]")
        if button_mode:
            middle = Text().add(self.round_l(color)).add(mid).add(self.round_r(color))
        else:
            middle = Text().add(" ").add(mid).add(" ")
        return middle
