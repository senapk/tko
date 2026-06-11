from loguru import logger
import os

from tko.util.pattern_loader import PatternLoader
from tko.loader.toml_parser import TomlParser
from tko.run.unit import Unit
from tko.util.decoder import Decoder
from tko.i18n import Msg, t
from pathlib import Path
from tko.util.console import Console




_WRITER_NO_CHANGES_TEST_FILE = Msg(
    pt="no changes in test file",
    en="no changes in test file",
)
_WRITER_FILE_WROTE = Msg(
    pt="file {path} wrote",
    en="file {path} wrote",
)
_WRITER_TARGET_NOT_SUPPORTED_BUILD = Msg(
    pt="fail: target {target} do not supported for build operation",
    en="fail: target {target} do not supported for build operation",
)


class Writer:

    def __init__(self):
        pass

    @staticmethod
    def to_vpl(unit: Unit):
        text = "case=" + unit.case + "\n"
        text += "input=" + unit.input
        text += "output=\"" + unit.get_expected() + "\"\n"
        if unit.grade is None:
            text += "\n"
        else:
            text += "grade reduction=" + str(unit.grade).zfill(3) + "%\n"
        return text


    @staticmethod
    def to_tio(unit: Unit):
        text  = ">>>>>>>> INSERT"
        if unit.case != '':
            text += " " + unit.case
        if unit.grade is not None:
            text += " " + str(unit.grade) + "%"
        text += '\n' + unit.input
        text += "======== EXPECT\n"
        text += unit.get_expected()
        if unit.get_expected() != '' and unit.get_expected()[-1] != '\n':
            text += '\n'
        text += "<<<<<<<< FINISH\n\n"
        return text

    @staticmethod
    def save_dir_files(folder: Path, pattern_loader: PatternLoader, label: str, unit: Unit) -> None:
        file_source = pattern_loader.make_file_source(label)
        with open(os.path.join(folder, file_source.input_file), "w", encoding="utf-8") as f:
            f.write(unit.input)
        with open(os.path.join(folder, file_source.output_file), "w", encoding="utf-8") as f:
            f.write(unit.get_expected())

    @staticmethod
    def save_target(target: Path, unit_list: list[Unit], quiet: bool) -> bool:
        def save_dir(_target: Path, _unit_list: list[Unit]):
            folder = _target
            pattern_loader = PatternLoader()
            number = 0
            for unit in _unit_list:
                Writer.save_dir_files(folder, pattern_loader, str(number).zfill(2), unit)
                number += 1

        def save_file(_target: Path, _unit_list: list[Unit]):
            if _target.suffix == ".tio":
                _new = "\n".join([Writer.to_tio(unit) for unit in _unit_list])
            elif _target.suffix == ".toml":
                _new = "\n".join([TomlParser.data_to_toml_test(unit.case, unit.get_input(), unit.get_expected()) for unit in _unit_list])
            else:
                _new = "\n".join([Writer.to_vpl(unit) for unit in _unit_list])

            file_exists = os.path.isfile(_target)

            if file_exists:
                _old = Decoder.load(_target)
                if _old == _new:
                    if not quiet:
                        Console.print(t(_WRITER_NO_CHANGES_TEST_FILE))
                    return False

            with open(_target, "w", encoding="utf-8") as f:
                f.write(_new)
                if not quiet:
                    Console.print(t(_WRITER_FILE_WROTE, path=_target))
                return True

        
        if target.is_dir():
            save_dir(target, unit_list)
        elif target.suffix in [".tio", ".vpl", ".toml"]:
            save_file(target, unit_list)
        else:
            logger.error(t(_WRITER_TARGET_NOT_SUPPORTED_BUILD, target=target))
            return False
        return True
