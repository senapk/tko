from tko.util.rt import RT

class BarBuilder:
    def __init__(self) -> None:
        pass

    def build_bar(self, text: str, percent: float, length: int, fmt_true: str = "/kC",
                  fmt_false: str = "/kY") -> RT:
        if length > len(text):
            prefix = (length - len(text)) // 2
            suffix = length - len(text) - prefix
            text = " " * prefix + text + " " * suffix
        elif length < len(text):
            text = text[:length]

        full_line: str = text
        done_len: int = round(percent * length)
        xp_bar = RT(full_line[:done_len], fmt_true) + RT(full_line[done_len:], fmt_false)
        return xp_bar
