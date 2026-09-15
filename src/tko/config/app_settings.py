from __future__ import annotations
from dataclasses import dataclass, asdict
import enum
from typing import Any

from tko.enums.diff_mode import DiffMode
from tko.util.rt import RT


class ToggleOption(enum.Enum):
    IMAGES = "use_images"

@dataclass
class AppSettings:
    _ui_language: str = "pt-BR"
    theme: str = "tko-dark"
    diff_mode: DiffMode = DiffMode.SIDE
    use_images: bool = True
    editor: str = "code"
    timeout: int = 2
    last_tko_check_update: str = ""
    last_version: str = ""
    panel_size_percent: float = 60.0

    @property
    def ui_language(self) -> str:
        return self._ui_language
    
    @ui_language.setter
    def ui_language(self, value: str) -> None:
        if value.lower() not in ["pt", "pt-br", "en"]:
            self._ui_language = "pt-BR"
        elif value.lower() in ["pt", "pt-br"]:
            self._ui_language = "pt-BR"
        else:
            self._ui_language = value

    def set_theme(self, value: str) -> None:
        self.theme = value if value in {"tko-dark", "tko-light"} else "tko-dark"
            
    # -------- toggles --------
    def toggle(self, attr: ToggleOption) -> None:
        if hasattr(self, attr.value):
            setattr(self, attr.value, not getattr(self, attr.value))

    def toggle_diff(self) -> None:
        self.diff_mode = DiffMode.DOWN if self.diff_mode == DiffMode.SIDE else DiffMode.SIDE

    # -------- serialization --------
    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["diff_mode"] = self.diff_mode.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppSettings:
        obj = cls()

        for key, value in data.items():
            if key == "ui_language":
                obj.ui_language = value
            elif key == "theme" and isinstance(value, str):
                obj.set_theme(value)
            elif key == "diff_mode":
                obj.diff_mode = DiffMode(value)
            elif hasattr(obj, key):
                setattr(obj, key, value)

        return obj

    # -------- display --------
    def __str__(self) -> str:
        output = [
            str(RT("Configurações globais:", "g")),
            f"- Language    : {self.ui_language}",
            f"- Theme       : {self.theme}",
            f"- Diff        : {self.diff_mode.value}",
            f"- Editor      : {self.editor}",
            f"- Images      : {self.use_images}",
            f"- Timeout     : {self.timeout}",
        ]
        return "\n".join(output)
