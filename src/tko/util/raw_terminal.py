import shutil
from tko.util.rt import RT

class RawTerminal:
    __term_width: None | int = None

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
    def centralize(text: RT | str, filler: RT | str = " "):
        if isinstance(text, str):
            text2: RT = RT(text)
        else:
            text2 = text
        width = RawTerminal.get_terminal_size()
        return text2.center(width, filler)
    