from .flags import Flag
from ..util.sentence import Sentence, Token
from ..settings.settings import Settings

class Style:

    @staticmethod
    def has_borders():
        return Settings().app.is_nerdfonts()
    
    @staticmethod
    def has_colors():
        return Settings().app.is_colored()

    @staticmethod
    def border_round(color: str, data: str):
        return Sentence().add(Style.roundL(color)).addf(color, data).add(Style.roundR(color))

    @staticmethod
    def border_sharp(color: str, data: str):
        return Sentence().add(Style.sharpL(color)).addf(color, data).add(Style.sharpR(color))

    @staticmethod
    def roundL(color: str) -> Token:
        return Token("", color.lower()) if Style.has_borders() else Token(" ", color)

    @staticmethod
    def roundR(color: str) -> Token:
        return Token("", color.lower()) if Style.has_borders() else Token(" ", color)

    @staticmethod
    def sharpL(color: str) -> Token:
        return Token("", color.lower()) if Style.has_borders() else Token(" ", color)


    @staticmethod
    def sharpR(color: str):
        return Token("", color.lower()) if Style.has_borders() else Token(" ", color)

    @staticmethod
    def focus():
        return "W" if not Style.has_colors() else "B"
    @staticmethod
    def prog_done():
        return "g" if not Style.has_colors() else "g"
    @staticmethod
    def prog_todo():
        return "" if not Style.has_colors() else "y"
    @staticmethod
    def flag_on():
        return "W" if not Style.has_colors() else "G"
    @staticmethod
    def flag_off():
        return "W" if not Style.has_colors() else "Y"

    @staticmethod
    def skill_done():
        return "kW" if not Style.has_colors() else "C"
    @staticmethod
    def skill_todo():
        return "wK" if not Style.has_colors() else "M"
    @staticmethod
    def main_done():
        return "kW" if not Style.has_colors() else "G"
    @staticmethod
    def main_todo():
        return "wK" if not Style.has_colors() else "R"
    
    @staticmethod
    def skills():
        return "c"

    @staticmethod
    def new():
        return "g"

    nothing = "m"
    started = "r"
    required = "y"
    complete = "g"

    shell = "r" # extern shell cmds
    htext = ""
    check = "g"
    uncheck = "y"
    param = "c"

    @staticmethod
    def build_bar(text: str, percent: float, length: int, fmt_true: str = "/kC",
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
            xp_bar.data[0] = Style.roundL(xp_bar.data[0].fmt)
            xp_bar.data[-1] = Style.roundR(xp_bar.data[-1].fmt)
        return xp_bar

    @staticmethod
    def get_flag_sentence(flag: Flag, pad: int = 0) -> Sentence:
        if not flag.is_bool():
            name = Sentence().addf(flag.get_value(), f"{flag._name}".ljust(pad))
            value = Sentence().add(f"[{flag.get_char()}]").add(name).add(f"{flag.get_value()}".rjust(2))
            return value
            
        char = flag.get_char()
        text = flag.get_name()
        color = "G" if flag.is_true() else "Y"
        textc = ""
        extra = Sentence()
        if not Style.has_colors():
            color = "W" if flag.is_true() else "K"
            textc = "k" if flag.is_true() else "w"
        if pad > 0:
            extra.addf(color, (pad - len(text)) * " ")
        mid = Sentence().addf(color + textc, text).add(extra).addf(color, f"[{char}]")
        # if flag.is_true():
        #     middle = Sentence().addf(color.lower(), Style.roundL()).add(mid).addf(color.lower(), Style.roundR())
        # else:
        middle = Sentence().add(Style.sharpL(color)).add(mid).add(Style.sharpR(color))
        return middle