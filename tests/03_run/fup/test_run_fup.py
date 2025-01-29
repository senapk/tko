import unittest
import os
from pathlib import Path

from tko.__main__ import exec, Parser #type: ignore
from tko.util.compare import Compare # type: ignore

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)

    def test_run_mixed_side(self, capsys):
        cmd = "-w 80 -m test solver.cpp cases.tio -as"
        Compare.text(capsys, "out1", cmd)

    def test_run_side_0(self, capsys):
        cmd = "-w 80 -m test solver.py cases.tio -d"
        Compare.text(capsys, "out3", cmd)
        
    def test_run_side_1(self, capsys):
        cmd = "-w 80 -m test solver.py cases.tio -s"
        Compare.text(capsys, "out4", cmd)

    def test_run_side_2(self, capsys):
        cmd = "-w 80 -m test solver.py cases.tio -ad"
        Compare.text(capsys, "out5", cmd)

    def test_run_side_5(self, capsys):
        cmd = "-w 80 -m test solver.cpp cases.tio -ad"
        Compare.text(capsys, "out2", cmd)

if __name__ == '__main__':
    unittest.main()
