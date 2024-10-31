import unittest
import os
from pathlib import Path

from tko.__main__ import exec, Parser #type: ignore
from tko.util.compare import Compare # type: ignore

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)

    def test_run_1(self, capsys):
        cmd = ["-m", "test", "solver.sh", "cases.tio"]
        Compare.list(capsys, "out1", cmd)

    def test_run_2(self, capsys):
        cmd = ["-m", "test", "solver.sh", "wrong.tio"]
        Compare.list(capsys, "out2", cmd)


if __name__ == '__main__':
    unittest.main()
