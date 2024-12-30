import unittest
import os
from pathlib import Path

from rota.__main__ import exec, Parser #type: ignore
from rota.util.compare import Compare # type: ignore

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)

    def test_run_cmd(self, capsys):
        cmd2 = ["-w", "50", "-m", "test", "solver.yaml", "cases.tio"]
        Compare.list(capsys, "out1", cmd2)


if __name__ == '__main__':
    unittest.main()
