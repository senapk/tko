import unittest
import os

from .compare import compare_text

class Test:
    folder = "tests/03_run/poo"
            
    def test_run_mixed_1(self, capsys):
        compare_text(capsys, Test.folder, "out1", "-w 80 -m test draft.ts cases.tio")

    def test_run_mixed_2(self, capsys):
        compare_text(capsys, Test.folder, "out2", "-w 80 -m test solver.cpp cases.tio -s")

    def test_run_mixed_3(self, capsys):
        compare_text(capsys, Test.folder, "out3", "-w 80 -m test draft.ts cases.tio -d")



if __name__ == '__main__':
    unittest.main()
