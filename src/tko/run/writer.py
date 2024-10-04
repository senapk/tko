from typing import List
import os

from ..util.identifier import Identifier

from ..util.pattern import PatternLoader
from ..util.consts import IdentifierType
from .unit import Unit


class Writer:

    def __init__(self):
        pass

    @staticmethod
    def to_vpl(unit: Unit):
        text = "case=" + unit.case + "\n"
        text += "input=" + unit.input
        text += "output=\"" + unit.expected + "\"\n"
        if unit.grade is None:
            text += "\n"
        else:
            text += "grade reduction=" + str(unit.grade).zfill(3) + "%\n"
        return text

    @staticmethod
    def to_tio(unit: Unit):
        text = "#INPUT"
        if unit.case != '':
            text += " " + unit.case
        if unit.grade is not None:
            text += " " + str(unit.grade) + "%"
        text += '\n' + unit.input
        text += "#OUTPUT\n"
        text += unit.expected
        if unit.expected != '' and unit.expected[-1] != '\n':
            text += '\n'
        text += "#END\n"
        return text

    @staticmethod
    def save_dir_files(folder: str, pattern_loader: PatternLoader, label: str, unit: Unit) -> None:
        file_source = pattern_loader.make_file_source(label)
        with open(os.path.join(folder, file_source.input_file), "w") as f:
            f.write(unit.input)
        with open(os.path.join(folder, file_source.output_file), "w") as f:
            f.write(unit.expected)

    @staticmethod
    def save_target(target: str, unit_list: List[Unit], force: bool = False):
        def ask_overwrite(file):
            print("file " + file + " found. Overwrite? (y/n):")
            resp = input()
            if resp.lower() == 'y':
                print("overwrite allowed")
                return True
            print("overwrite denied\n")
            return False

        def save_dir(_target: str, _unit_list):
            folder = _target
            pattern_loader = PatternLoader()
            number = 0
            for unit in _unit_list:
                Writer.save_dir_files(folder, pattern_loader, str(number).zfill(2), unit)
                number += 1

        def save_file(_target, _unit_list):
            if _target.endswith(".tio"):
                _new = "\n".join([Writer.to_tio(unit) for unit in _unit_list])
            else:
                _new = "\n".join([Writer.to_vpl(unit) for unit in _unit_list])

            file_exists = os.path.isfile(_target)

            if file_exists:
                _old = open(_target).read()
                if _old == _new:
                    print("no changes in test file")
                    return

            if not file_exists or (file_exists and (force or ask_overwrite(_target))):
                with open(_target, "w") as f:
                    f.write(_new)

                    if not force:
                        print("file " + _target + " wrote")

        target_type = Identifier.get_type(target)
        if target_type == IdentifierType.OBI:
            save_dir(target, unit_list)
        elif target_type == IdentifierType.TIO or target_type == IdentifierType.VPL:
            save_file(target, unit_list)
        else:
            print("fail: target " + target + " do not supported for build operation\n")
