from dataclasses import dataclass
from pathlib import Path


@dataclass
class WdirConfig:
    curses_mode: bool = False
    lang: str = ""
    autoload: bool = False
    autoload_folder: Path | None = None

    def set_curses(self, value: bool):
        self.curses_mode = value

    def set_lang(self, lang: str):
        if lang == "":
            return
        self.lang = lang

    def set_autoload_folder(self, folder: Path | None):
        self.autoload_folder = folder

    def set_autoload(self, value: bool):
        self.autoload = value