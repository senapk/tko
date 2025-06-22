from typing import Callable
import curses
import os

FN_VOID = Callable[[], None]

class InputManager:
    backspace_list: list[int] = [8, 127, 263, curses.KEY_BACKSPACE]
    a = 97
    d = 100
    tab = 9
    special_double_key = 195
    cedilha = 167
    esc = 27
    plus = 465
    minus = 464
    delete = 330

    def __init__(self):
        # stores a function than can return another function
        self.calls: dict[int, Callable[[], FN_VOID] | Callable[[], None]] = {}

    def add_int(self, _key: int, fn: Callable[[], None]):
        if _key in self.calls.keys():
            raise ValueError(f"Chave duplicada {chr(_key)}")
        self.calls[_key] = fn

    def add_str(self, str_key: str, fn: Callable[[], None]):
        if str_key != "":
            self.add_int(ord(str_key), fn)

    def has_str_key(self, key: str) -> bool:
        return ord(key) in self.calls
    
    def has_int_key(self, key: int) -> bool:
        return key in self.calls
    
    def exec_call(self, key: int):
        return self.calls[key]()

    @staticmethod
    def fix_esc_delay():
        if hasattr(curses, "set_escdelay"):
            curses.set_escdelay(25)
        else:
            os.environ.setdefault('ESCDELAY', '25')

    @staticmethod
    def fix_cedilha(scr: curses.window, value: int) -> int:
        if value == InputManager.special_double_key:
            value = scr.getch()
            if value == InputManager.cedilha: #ç
                value = ord("c")
        return value