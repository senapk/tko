from typing import Optional, Union
import shutil
from .text import Text, Token


class RawTerminal:
    __term_width: Optional[int] = None

    def __init__(self):
        pass

    @staticmethod
    def __get_terminal_size() -> int:
        return shutil.get_terminal_size().columns

    @staticmethod
    def get_terminal_size():
        if RawTerminal.__term_width is None:
            return RawTerminal.__get_terminal_size()
        return RawTerminal.__term_width

    @staticmethod
    def set_terminal_size(value: int):
        RawTerminal.__term_width = value

    @staticmethod
    def centralize(text: Text | str, filler: Token | str = Token(" ")):
        if isinstance(filler, str):
            filler2: Token = Token(filler)
        else:
            filler2 = filler

        if isinstance(text, str):
            text2: Text = Text().add(text)
        else:
            text2 = text
        width = RawTerminal.get_terminal_size()
        return text2.center(width, filler2)
    