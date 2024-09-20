import unittest
import os

from .compare import compare_list

class Test:
    folder = "tests/03_run/cmd"

    def test_run_cmd(self, capsys):
        cmd = "g++ solver.cpp -o solver.out && ./solver.out"
        cmd2 = ["-w", "50", "-m", "test", "--cmd", cmd, "cases.tio"]
        compare_list(capsys, Test.folder, "out1", cmd2)


    def test_run_makefile(self, capsys):
        cmd = "make -s solver.out && ./solver.out"
        cmd2 = ["-w", "50", "-m", "test", "--cmd", cmd, "cases.tio"]
        compare_list(capsys, Test.folder, "out2", cmd2)



if __name__ == '__main__':
    unittest.main()
