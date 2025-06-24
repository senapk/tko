from tko.enums.diff_mode import DiffMode
from tko.util.text import Text
from typing import Any
import curses


class AppSettings:

    def __init__(self):
        self.diff_mode = DiffMode.SIDE.value
        self.show_hidden = False
        self.use_images = True
        self.use_borders = False
        self.editor = "code"
        self.timeout = 2
        self.key_left: int = curses.KEY_LEFT
        self.key_right: int = curses.KEY_RIGHT
        self.key_up: int = curses.KEY_UP
        self.key_down: int = curses.KEY_DOWN

    def set_key_left(self, key: int):
        self.key_left = key
        return self

    def set_key_right(self, key: int):
        self.key_right = key
        return self

    def set_key_up(self, key: int):
        self.key_up = key
        return self

    def set_key_down(self, key: int):
        self.key_down = key
        return self

    def get_key_left(self) -> int:
        return self.key_left

    def get_key_right(self) -> int:
        return self.key_right

    def get_key_up(self) -> int:
        return self.key_up

    def get_key_down(self) -> int:
        return self.key_down

    def to_dict(self):
        return self.__dict__

    def from_dict(self, attr_dict: dict[str, Any]):
        for key, value in attr_dict.items():
            if hasattr(self, key) and type(getattr(self, key)) == type(value):
                setattr(self, key, value)
        return self

    def toggle_diff(self):
        if self.diff_mode == DiffMode.SIDE.value:
            self.diff_mode = DiffMode.DOWN.value
        else:
            self.diff_mode = DiffMode.SIDE.value

    def toggle_borders(self):
        self.use_borders = not self.use_borders

    def toggle_images(self):
        self.use_images = not self.use_images

    def toggle_hidden(self):
        self.show_hidden = not self.show_hidden

    def set_diff_mode(self, diff_mode: DiffMode):
        self.diff_mode = diff_mode.value
        return self

    def set_show_hidden(self, show_hidden: bool):
        self.show_hidden = show_hidden
        return self

    def set_use_borders(self, borders: bool):
        self.use_borders = borders
        return self

    def set_use_images(self, images: bool):
        self.use_images = images
        return self

    def set_editor(self, editor: str):
        self.editor = editor
        return self

    def set_timeout(self, timeout: int):
        self.timeout = timeout
        return self

    def get_diff_mode(self) -> DiffMode:
        if self.diff_mode == DiffMode.SIDE.value:
            return DiffMode.SIDE
        return DiffMode.DOWN

    # def get_lang_default(self) -> str:
    #     return self._lang_default

    # def get_last_rep(self) -> str:
    #     return self._last_rep

    def get_show_hidden(self) -> bool:
        return self.show_hidden

    def get_use_images(self) -> bool:
        return self.use_images

    def get_use_borders(self) -> bool:
        return self.use_borders

    def get_editor(self) -> str:
        return self.editor

    def get_timeout(self) -> int:
        return self.timeout

    def __str__(self):
        output: list[str] = [str(Text.format("{g}", "Configurações globais:")),
                             "- Diff    : {}".format(str(self.get_diff_mode().value)),
                             "- Editor  : {}".format(self.get_editor()),
                             "- Bordas  : {}".format(self.get_use_borders()),
                             "- Images  : {}".format(self.get_use_images()),
                             "- Timeout : {}".format(self.get_timeout())]
        return "\n".join(output)