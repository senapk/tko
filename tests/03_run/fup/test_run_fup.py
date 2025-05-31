import os
from pathlib import Path
import pytest
from tko.__main__ import execute, Parser #type: ignore
from tko.util.compare import Compare # type: ignore

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)

    def test_run_mixed_side(self, capsys: pytest.CaptureFixture[str]):
        cmd = "-w 80 -m run solver.cpp cases.tio -as"
        Compare.text(capsys, "out1", cmd)

    def test_run_side_0(self, capsys: pytest.CaptureFixture[str]):
        cmd = "-w 80 -m run solver.py cases.tio -d"
        Compare.text(capsys, "out3", cmd)
        
    def test_run_side_1(self, capsys: pytest.CaptureFixture[str]):
        cmd = "-w 80 -m run solver.py cases.tio -s"
        Compare.text(capsys, "out4", cmd)

    def test_run_side_2(self, capsys: pytest.CaptureFixture[str]):
        cmd = "-w 80 -m run solver.py cases.tio -ad"
        Compare.text(capsys, "out5", cmd)

    def test_run_side_5(self, capsys: pytest.CaptureFixture[str]):
        cmd = "-w 80 -m run solver.cpp cases.tio -ad"
        Compare.text(capsys, "out2", cmd)
