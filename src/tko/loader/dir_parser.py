from tko.run.unit import Unit
from tko.util.decoder import Decoder
from tko.util.pattern_loader import PatternLoader


import os
from pathlib import Path


class DirParser:
    @staticmethod
    def parse_dir(folder: Path) -> list[Unit]:  # Updated return type to list[Unit]
        pattern_loader = PatternLoader()
        files = sorted(os.listdir(folder))
        matches = pattern_loader.get_file_sources(files)

        unit_list: list[Unit] = []  # Updated type to list[Unit]
        try:
            for m in matches:
                unit = Unit()
                unit.source = folder / m.label
                unit.grade = 100
                input_file = os.path.join(folder, m.input_file)
                value = Decoder.load(input_file)
                unit.input = value + ("" if value.endswith("\n") else "\n")
                output_file = os.path.join(folder, m.output_file)
                value = Decoder.load(output_file)
                unit.set_expected(value + ("" if value.endswith("\n") else "\n"))
                unit_list.append(unit)
        except FileNotFoundError as e:
            print(str(e))
        return unit_list