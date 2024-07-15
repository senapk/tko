from typing import Optional, Union
import shutil
from ..util.term_color import Color
from ..util.ftext import Sentence, Token


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
        ftext: Union[Sentence, str],
        sep: Optional[Union[str, Token]] = Token(" "),
        left_border: Optional[Union[str, Token]] = None,
        right_border: Optional[Union[str, Token]] = None,
    ) -> Sentence:
        
        if isinstance(ftext, str) or isinstance(ftext, Token):
            ftext = Sentence() + ftext
        if sep is None:
            sep = Token(" ")
        elif isinstance(sep, str):
            sep = Token(sep)
        if left_border is None:
            left_border = sep
        if right_border is None:
            right_border = sep
        term_width = Report.get_terminal_size()

        size = len(ftext)
        pad = sep if size % 2 == 0 else Token("")
        tw = term_width - 2
        filler = Token(sep.text * (int(tw / 2 - size / 2)), sep.fmt)
        return Sentence() + left_border + pad + filler + ftext + filler + right_border
