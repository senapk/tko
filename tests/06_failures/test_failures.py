import unittest
import os
from pathlib import Path

from tko.__main__ import execute, Parser #type: ignore
from tko.util.compare import Compare # type: ignore

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)

    def test_all(self, capsys):
        Compare.text(capsys, "out1", "-w 80 -m run cases.tio draft.ts -ad")
        Compare.text(capsys, "out2", "-w 80 -m run cases.tio draft.ts -d")
        Compare.text(capsys, "out3", "-w 80 -m run cases.tio draft.ts -qd")

if __name__ == '__main__':
    unittest.main()
