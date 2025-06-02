import os

from tko.util.identifier import Identifier
from tko.util.pattern_loader import PatternLoader
from tko.enums.identifier_type import IdentifierType
from tko.run.unit import Unit
from tko.util.decoder import Decoder

class Writer:

    def __init__(self):
        pass

    @staticmethod
    def to_vpl(unit: Unit):
        text = "case=" + unit.case + "\n"
        text += "input=" + unit.inserted
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
        text += '\n' + unit.inserted
        text += "======== EXPECT\n"
        text += unit.get_expected()
        if unit.get_expected() != '' and unit.get_expected()[-1] != '\n':
            text += '\n'
        text += "<<<<<<<< FINISH\n\n"
        return text

    @staticmethod
    def save_dir_files(folder: str, pattern_loader: PatternLoader, label: str, unit: Unit) -> None:
        file_source = pattern_loader.make_file_source(label)
        with open(os.path.join(folder, file_source.input_file), "w", encoding="utf-8") as f:
            f.write(unit.inserted)
        with open(os.path.join(folder, file_source.output_file), "w", encoding="utf-8") as f:
            f.write(unit.get_expected())

    @staticmethod
    def save_target(target: str, unit_list: list[Unit], quiet: bool) -> bool:
        def save_dir(_target: str, _unit_list: list[Unit]):
            folder = _target
            pattern_loader = PatternLoader()
            number = 0
            for unit in _unit_list:
                Writer.save_dir_files(folder, pattern_loader, str(number).zfill(2), unit)
                number += 1

        def save_file(_target: str, _unit_list: list[Unit]):
            if _target.endswith(".tio"):
                _new = "\n".join([Writer.to_tio(unit) for unit in _unit_list])
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
                    print("file " + _target + " wrote")
                return True

        target_type = Identifier.get_type(target)
        if target_type == IdentifierType.OBI:
            save_dir(target, unit_list)
        elif target_type == IdentifierType.TIO or target_type == IdentifierType.VPL:
            save_file(target, unit_list)
        else:
            print("fail: target " + target + " do not supported for build operation\n")
            return False
        return True
