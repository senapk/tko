import os

from tko.util.identifier import Identifier
from tko.util.pattern_loader import PatternLoader
from tko.enums.identifier_type import IdentifierType
from tko.loader.toml_parser import TomlParser
from tko.run.unit import Unit
from tko.util.decoder import Decoder
from pathlib import Path
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
                _new = "\n".join([TomlParser.to_toml(unit.case, unit.get_input(), unit.get_expected()) for unit in _unit_list])
            else:
                _new = "\n".join([Writer.to_vpl(unit) for unit in _unit_list])

            file_exists = os.path.isfile(_target)

            if file_exists:
                _old = Decoder.load(_target)
                if _old == _new:
                    if not quiet:
                        print("no changes in test file")
                    return False

            with open(_target, "w", encoding="utf-8") as f:
                f.write(_new)
                if not quiet:
                    print("file " + str(_target) + " wrote")
                return True

        target_type = Identifier.get_type(str(target))
        if target_type == IdentifierType.OBI:
            save_dir(target, unit_list)
        elif target_type in [IdentifierType.TIO, IdentifierType.VPL, IdentifierType.TOML]:
            save_file(target, unit_list)
        else:
            print("fail: target " + str(target) + " do not supported for build operation\n")
            return False
        return True
