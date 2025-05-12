import unittest
import os
from pathlib import Path

from tko.__main__ import exec, Parser #type: ignore
from tko.util.compare import Compare # type: ignore

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)

    # def test_run_mixed_1(self, capsys):
    #     Compare.text(capsys, "out1", "-w 80 -m exec runtime.cpp cases.tio -ad")

    # def test_run_mixed_2(self, capsys):
    #     Compare.text(capsys, "-w 80 -m exec runtime.cpp", "out2")

    def test_run_mixed_3(self, capsys):
        Compare.text(capsys, "out2", "-w 80 -m exec exception.py -d")

    # def test_run_mixed_4(self, capsys):
    #     Compare.text(capsys, "out3", "-w 80 -m exec exception.cpp cases.tio -d")

    # def test_run_mixed_5(self, capsys):
    #     Compare.text(capsys, "out4", "-w 80 -m exec exception.py cases.tio -s")

if __name__ == '__main__':
    unittest.main()
