import unittest
import os
from pathlib import Path

from tko.__main__ import exec, Parser #type: ignore
from tko.util.compare import Compare # type: ignore

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)

    def test_run_mixed_5(self, capsys):
        Compare.text(capsys,  "out5", "-w 80 -m exec cases.tio")
    def test_run_mixed_6(self, capsys):
        Compare.text(capsys,  "out6", "-w 80 -m exec solver.py")
    def test_run_mixed_7(self, capsys):
        Compare.text(capsys,  "out7", "-w 80 -m exec solver.py cases_empty.tio")
    def test_run_mixed_8(self, capsys):
        Compare.text(capsys,  "out8", "-w 80 -m exec solver.py cases.tio -s")
        

if __name__ == '__main__':
    unittest.main()
