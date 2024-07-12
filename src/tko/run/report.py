from typing import Optional, Union
import shutil
from ..util.term_color import Color
from ..util.ftext import FF, TK
from icecream import ic


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
        ftext: Union[FF, str],
        sep: Optional[Union[str, TK]] = TK(" "),
        left_border: Optional[Union[str, TK]] = None,
        right_border: Optional[Union[str, TK]] = None,
    ) -> FF:
        
        if isinstance(ftext, str) or isinstance(ftext, TK):
            ftext = FF() + ftext
        if sep is None:
            sep = TK(" ")
        elif isinstance(sep, str):
            sep = TK(sep)
        if left_border is None:
            left_border = sep
        if right_border is None:
            right_border = sep
        term_width = Report.get_terminal_size()

        size = len(ftext)
        pad = sep if size % 2 == 0 else TK("")
        tw = term_width - 2
        filler = TK(sep.text * (int(tw / 2 - size / 2)), sep.fmt)
        return FF() + left_border + pad + filler + ftext + filler + right_border
