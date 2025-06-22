from __future__ import annotations
import argparse
import os
from tko.run.diff_builder_down import DiffBuilderDown
from tko.run.diff_builder_side import DiffBuilderSide
from tko.enums.diff_mode import DiffMode
from tko.util.raw_terminal import RawTerminal
from tko.run.unit import Unit


def cmd_diff(args: argparse.Namespace) -> None:
    target_a: str = args.target_a
    target_b: str = args.target_b
    diff_mode = DiffMode.SIDE if args.side else DiffMode.DOWN
    if args.path:
        if os.path.isfile(target_a):
            content_a = open(target_a, 'r', encoding='utf-8').read()
        else:
            content_a = "File not found: " + target_a
        if os.path.isfile(target_b):
            content_b = open(target_b, 'r', encoding='utf-8').read()
        else:
            content_b = "File not found: " + target_b
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
        print(line)