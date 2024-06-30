from typing import Optional
import shutil
from ..util.term_color import Color

class Report:
    __term_width: Optional[int] = None

    def __init__(self):
        pass

    @staticmethod
    def update_terminal_size():
        term_width = shutil.get_terminal_size().columns
        if term_width % 2 == 0:
            term_width -= 1
        Report.__term_width = term_width

    @staticmethod
    def get_terminal_size():
        if Report.__term_width is None:
            Report.update_terminal_size()

        return Report.__term_width

    @staticmethod
    def set_terminal_size(value: int):
        if value % 2 == 0:
            value -= 1
        Report.__term_width = value

    @staticmethod
    def centralize(
        text,
        sep=" ",
        left_border: Optional[str] = None,
        right_border: Optional[str] = None,
    ) -> str:
        if left_border is None:
            left_border = sep
        if right_border is None:
            right_border = sep
        term_width = Report.get_terminal_size()

        size = Color.len(text)
        pad = sep if size % 2 == 0 else ""
        tw = term_width - 2
        filler = sep * int(tw / 2 - size / 2)
        return left_border + pad + filler + text + filler + right_border
