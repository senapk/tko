import os
from pathlib import Path

from tko.feno.filter import CodeFilter
from tko.i18n import Msg, t
from tko.util.raw_terminal import RawTerminal
from tko.util.rtext import RText


_RUN_FILTER_MODE_BANNER = Msg(
    pt=" Entrando no modo de filtragem ",
    en=" Entering filter mode ",
)


class TkoFilterMode:
    @staticmethod
    def deep_copy_and_change_dir():
        filter_path = (Path.home() / ".tko_filter").resolve()
        CodeFilter.cf_recursive(Path(".").resolve(), filter_path, force=True)
        os.chdir(filter_path)


class FilterModeService:
    @staticmethod
    def apply(target_list: list[Path]) -> list[Path]:
        print(RText(t(_RUN_FILTER_MODE_BANNER)).center(RawTerminal.get_terminal_size(), "═"))

        TkoFilterMode.deep_copy_and_change_dir()
        new_target_list: list[Path] = []
        for target in target_list:
            resolved = target.resolve()
            if resolved.exists():
                new_target_list.append(resolved)
        return new_target_list