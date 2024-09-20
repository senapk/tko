import unittest
import os

from .compare import compare_list, compare_text


class Test:
    folder = "tests/03_run/sql"

    def test_run_1(self, capsys):
        cmd_run = "cat create.sql solver.sql | sqlite3"
        cmd = ["-m", "test", "--cmd", cmd_run, "cases.tio"]
        compare_list(capsys, Test.folder, "out1", cmd)


    def test_run_2(self, capsys):
        compare_text(capsys, Test.folder, "out2", "-w 80 -m test create.sql student.sql")
    

if __name__ == '__main__':
    unittest.main()
