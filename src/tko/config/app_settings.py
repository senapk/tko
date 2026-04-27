from __future__ import annotations
from dataclasses import dataclass, field, asdict
import enum
from typing import Any
import curses

from tko.enums.diff_mode import DiffMode
from tko.util.text import Text


class ToggleOption(enum.Enum):
    BORDERS = "use_borders"
    IMAGES = "use_images"

class AppKeys(enum.Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    PG_UP = "pg_up"
    PG_DOWN = "pg_down"
    BACKSPACE = "backspace"
    ESC = "esc"

@dataclass
class AppSettings:
    diff_mode: DiffMode = DiffMode.SIDE
    use_images: bool = True
    use_borders: bool = False
    editor: str = "code"
    timeout: int = 2
    last_tko_check_update: str = ""
    last_version: str = ""
    panel_size_percent: float = 60.0

    keys: dict[AppKeys, int] = field(default_factory=lambda: {
        AppKeys.LEFT: curses.KEY_LEFT,
        AppKeys.RIGHT: curses.KEY_RIGHT,
        AppKeys.UP: curses.KEY_UP,
        AppKeys.DOWN: curses.KEY_DOWN,
        AppKeys.PG_UP: curses.KEY_PPAGE,
        AppKeys.PG_DOWN: curses.KEY_NPAGE,
        AppKeys.BACKSPACE: curses.KEY_BACKSPACE,
        AppKeys.ESC: 27,
    })

    # -------- toggles --------
    def toggle(self, attr: ToggleOption) -> None:
        if hasattr(self, attr.value):
            setattr(self, attr.value, not getattr(self, attr.value))

    def toggle_diff(self) -> None:
        self.diff_mode = DiffMode.DOWN if self.diff_mode == DiffMode.SIDE else DiffMode.SIDE

    # -------- keys --------
    def set_key(self, action: AppKeys, key_code: int) -> None:
        self.keys[action] = key_code

    def get_key(self, action: AppKeys) -> int:
        return self.keys.get(action, 0)

    # -------- serialization --------
    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["diff_mode"] = self.diff_mode.value
        data["keys"] = {k.value: v for k, v in self.keys.items()}
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppSettings":
        obj = cls()

        for key, value in data.items():
            if key == "diff_mode":
                obj.diff_mode = DiffMode(value)
            elif key == "keys":
                obj.keys = {AppKeys(k): v for k, v in value.items()}
            elif hasattr(obj, key):
                setattr(obj, key, value)

        return obj

    # -------- display --------
    def __str__(self) -> str:
        output = [
            str(Text.format("{g}", "Configurações globais:")),
            f"- Diff    : {self.diff_mode.value}",
            f"- Editor  : {self.editor}",
            f"- Bordas  : {self.use_borders}",
            f"- Images  : {self.use_images}",
            f"- Timeout : {self.timeout}",
        ]
        return "\n".join(output)