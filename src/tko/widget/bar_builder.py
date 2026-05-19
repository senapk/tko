from tko.util.rtext import RText

class BarBuilder:
    def __init__(self) -> None:
        pass

    def build_bar(self, text: str, percent: float, length: int, fmt_true: str = "/kC",
                  fmt_false: str = "/kY") -> RText:
        if length > len(text):
            prefix = (length - len(text)) // 2
            suffix = length - len(text) - prefix
            text = " " * prefix + text + " " * suffix
        elif length < len(text):
            text = text[:length]

        full_line: str = text
        done_len: int = round(percent * length)
        xp_bar = RText(full_line[:done_len], fmt_true) + RText(full_line[done_len:], fmt_false)
        return xp_bar
