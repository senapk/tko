import unittest
from .compare import compare_text

class Test:
    folder = "tests/03_run/fup"

    def test_run_mixed_side(self, capsys):
        cmd = "-w 80 -m test solver.cpp cases.tio -as"
        compare_text(capsys, Test.folder, "out1", cmd)

    def test_run_side_0(self, capsys):
        cmd = "-w 80 -m test solver.py cases.tio -d"
        compare_text(capsys, Test.folder, "out3", cmd)
        
    def test_run_side_1(self, capsys):
        cmd = "-w 80 -m test solver.py cases.tio -s"
        compare_text(capsys, Test.folder, "out4", cmd)

    def test_run_side_2(self, capsys):
        cmd = "-w 80 -m test solver.py cases.tio -a"
        compare_text(capsys, Test.folder, "out5", cmd)

    def test_run_side_5(self, capsys):
        cmd = "-w 80 -m test solver.cpp cases.tio -ad"
        compare_text(capsys, Test.folder, "out2", cmd)

if __name__ == '__main__':
    unittest.main()
