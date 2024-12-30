import unittest
import os
from pathlib import Path

from rota.__main__ import exec, Parser #type: ignore
from rota.util.compare import Compare # type: ignore

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)

    def test_simple_list1(self, capsys):
        Compare.list(capsys, "out1", ["-m", "run", "cases.tio"])

    def test_simple_list2(self, capsys):
        Compare.list(capsys, "out2", ["-m", "run", "cases.tio", "cases2.tio"])

if __name__ == '__main__':
    unittest.main()
