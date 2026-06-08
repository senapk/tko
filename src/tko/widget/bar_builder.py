from tko.util.rbuffer import RBuffer
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

    def build_progress_xp(self, obtained: float, target100: float, available: float, reference: float, length: int, styles: tuple[str, str, str]) -> RT:
        """
        Build a progress bar for XP, showing the obtained XP, the target 100% XP, and the available XP.
        obtained < target100 < available < reference
        reference is used to determine the total xp possible.
        ex: obtained = 50, target100 = 70, available = 100, reference = 200, lenght = 20
        The obtained will be showed using '-', target, available, reference using styles[0], styles[1], styles[2] respectively.
        """
        unit_value = reference / length
        obtained_len = round(obtained / unit_value)
        target100_len = round(target100 / unit_value)
        available_len = round(available / unit_value)
        text_obtained = "#" * obtained_len + " " * (length - obtained_len)
        styles_data = [styles[0]] * target100_len + [styles[1]] * (available_len - target100_len) + [styles[2]] * (length - available_len)
        rbuffer = RBuffer()
        for char, style in zip(text_obtained, styles_data):
            rbuffer += RT(char, style)
        return rbuffer.to_rt()