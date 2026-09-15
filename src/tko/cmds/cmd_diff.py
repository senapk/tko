from __future__ import annotations
from pathlib import Path
from tko.run.diff_builder_down import DiffBuilderDown
from tko.run.diff_builder_side import DiffBuilderSide
from tko.enums.diff_mode import DiffMode
from tko.util.raw_terminal import RawTerminal
from tko.run.unit import Unit
from tko.util.console import Console


def cmd_diff(target_a: str, target_b: str, diff_mode: DiffMode, is_path: bool) -> None:
    if is_path:
        content_a: str = Path(target_a).read_text(encoding="utf-8")
        content_b: str = Path(target_b).read_text(encoding="utf-8")
    else:
        content_a = target_a.replace('\\n', '\n')
        content_b = target_b.replace('\\n', '\n')
    unit: Unit = Unit()
    unit.set_expected(content_a)
    unit.set_received(content_b)
    if diff_mode == DiffMode.DOWN:
        diff_builder = DiffBuilderDown(RawTerminal.get_terminal_size(), unit).standalone_diff()
    else:
        diff_builder = DiffBuilderSide(RawTerminal.get_terminal_size(), unit).standalone_diff()
    for line in diff_builder.build_diff():
        Console.print(line)