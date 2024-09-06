from .flags import Flag
from ..util.sentence import Sentence, Token
from ..settings.app_settings import AppSettings

class Border:
    def __init__(self, app: AppSettings):
        self.app = app

    def has_borders(self):
        return self.app._borders

    def border_round(self, color: str, data: str):
        return Sentence().add(self.roundL(color)).addf(color, data).add(self.roundR(color))

    def border_sharp(self, color: str, data: str):
        return Sentence().add(self.sharpL(color)).addf(color, data).add(self.sharpR(color))

    def roundL(self, color: str) -> Token:
        return Token("", color.lower()) if self.has_borders() else Token(" ", color)

    def roundR(self, color: str) -> Token:
        return Token("", color.lower()) if self.has_borders() else Token(" ", color)

    def sharpL(self, color: str) -> Token:
        return Token("", color.lower()) if self.has_borders() else Token(" ", color)

    def sharpR(self, color: str):
        return Token("", color.lower()) if self.has_borders() else Token(" ", color)

    def build_bar(self, text: str, percent: float, length: int, fmt_true: str = "/kC",
                  fmt_false: str = "/kY", round=True) -> Sentence:
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

    def get_flag_sentence(self, flag: Flag, pad: int = 0, button_mode: bool = True) -> Sentence:
        char = flag.get_char()
        text = flag.get_name()
        # if flag.is_true():
        #     text = text.upper()
        # else:
        #     text = text.lower()

        color = "G" if flag.is_true() else "Y"
        if not button_mode:
            color = color.lower()
        extra = Sentence()
        filler = "+" if flag.is_true() else "-"
        if pad > 0:
            extra.addf(color, (pad - len(text)) * filler)

        mid = Sentence().addf(color, text).add(extra).addf(color, f"[{char}]")
        if button_mode:
            middle = Sentence().add(self.sharpL(color)).add(mid).add(self.sharpR(color))
        else:
            middle = Sentence().add(" ").add(mid).add(" ")
        return middle
