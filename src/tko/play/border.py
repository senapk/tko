from .flags import Flag
from ..util.text import Text, Token
from ..settings.app_settings import AppSettings
from tko.util.symbols import symbols

class Border:
    def __init__(self, app: AppSettings):
        self.app = app

    def has_borders(self):
        return self.app.get_use_borders()

    def border(self, color: str, data: str):
        return Text().add(self.roundL(color)).addf(color, data).add(self.roundR(color))

    def border_sharp(self, color: str, data: str):
        return Text().add(self.sharpL(color)).addf(color, data).add(self.sharpR(color))

    def roundL(self, color: str) -> Token:
        return Token("", color.lower()) if self.has_borders() else Token(" ", color)

    def roundR(self, color: str) -> Token:
        return Token("", color.lower()) if self.has_borders() else Token(" ", color)

    def sharpL(self, color: str) -> Token:
        return Token("", color.lower()) if self.has_borders() else Token(" ", color)

    def sharpR(self, color: str):
        return Token("", color.lower()) if self.has_borders() else Token(" ", color)

    def build_bar(self, text: str, percent: float, length: int, fmt_true: str = "/kC",
                  fmt_false: str = "/kY", round=True) -> Text:
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
        xp_bar = Token(full_line[:done_len], fmt_true) + Token(full_line[done_len:], fmt_false)
            
        if round:
            xp_bar.data[0] = self.roundL(xp_bar.data[0].fmt)
            xp_bar.data[-1] = self.roundR(xp_bar.data[-1].fmt)
        return xp_bar

    def get_flag_sentence(self, flag: Flag, pad: int = 0, button_mode: bool = True, include_symbol: bool = True, include_key: bool = True) -> Text:
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
            middle = Text().add(self.roundL(color)).add(mid).add(self.roundR(color))
        else:
            middle = Text().add(" ").add(mid).add(" ")
        return middle
