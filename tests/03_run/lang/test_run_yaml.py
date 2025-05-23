import unittest
import os
from pathlib import Path

from tko.__main__ import execute, Parser #type: ignore
from tko.util.compare import Compare # type: ignore

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)

    def test_run_mixed_side(self, capsys):
        cmd = "-w 80 -m run solver.yaml cases.tio -as"
        Compare.text(capsys, "out1", cmd)


if __name__ == '__main__':
    unittest.main()
