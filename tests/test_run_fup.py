import unittest
from .compare import compare_text

class Test:
    folder = "tests/03_run/fup"

    def test_run_mixed_side(self, capsys):
        cmd = "-w 80 -m go solver.cpp cases.tio -as"
        compare_text(capsys, Test.folder, "out1", cmd)
        cmd = "-w 80 -m go solver.cpp cases.tio -ad"
        compare_text(capsys, Test.folder, "out2", cmd)
        cmd = "-w 80 -m go solver.py cases.tio -d"
        compare_text(capsys, Test.folder, "out3", cmd)
        cmd = "-w 80 -m go solver.py cases.tio -s"
        compare_text(capsys, Test.folder, "out4", cmd)
        cmd = "-w 80 -m go solver.py cases.tio -a"
        compare_text(capsys, Test.folder, "out5", cmd)


if __name__ == '__main__':
    unittest.main()
