from __future__ import annotations

from pathlib import Path

from tko.loader.loader import Loader
from tko.run.unit import Unit


class TestDiscovery:
    """Descobre casos de teste sem conhecer ou executar uma solução."""

    @staticmethod
    def sources(target: Path) -> list[Path]:
        if target.is_file():
            return [target] if target.suffix in Loader.SOURCES_EXTENSIONS else []
        if not target.is_dir():
            raise FileNotFoundError(target)

        output: list[Path] = []
        for path in sorted(target.rglob("*")):
            if any(part in {".git", ".tko", ".cache", "__pycache__"} for part in path.parts):
                continue
            if path.is_file() and path.suffix in Loader.SOURCES_EXTENSIONS:
                output.append(path)
        for folder in sorted({path.parent for path in target.rglob("*.in")} | {path.parent for path in target.rglob("*.sol")}):
            if not any(part in {".git", ".tko", ".cache", "__pycache__"} for part in folder.parts):
                output.append(folder)
        return output

    @classmethod
    def discover(cls, target: Path) -> list[Unit]:
        units: list[Unit] = []
        seen_inputs: set[str] = set()
        for source in cls.sources(target):
            for unit in Loader.parse_source(source):
                input_data = unit.get_input()
                if not input_data or input_data in seen_inputs:
                    continue
                seen_inputs.add(input_data)
                units.append(unit)
        for index, unit in enumerate(units):
            unit.index = index
        return units
