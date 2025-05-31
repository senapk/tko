import os
import pytest
from pathlib import Path

from tko.__main__ import execute, Parser #type: ignore
from tko.util.compare import Compare # type: ignore

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)

    def test_run_mixed_5(self, capsys: pytest.CaptureFixture[str]):
        Compare.text(capsys,  "out5", "-w 80 -m run cases.tio")
    def test_run_mixed_6(self, capsys: pytest.CaptureFixture[str]):
        Compare.text(capsys,  "out6", "-w 80 -m run solver.py")
    def test_run_mixed_7(self, capsys: pytest.CaptureFixture[str]):
        Compare.text(capsys,  "out7", "-w 80 -m run solver.py cases_empty.tio")
    def test_run_mixed_8(self, capsys: pytest.CaptureFixture[str]):
        Compare.text(capsys,  "out8", "-w 80 -m run solver.py cases.tio -s")
        
