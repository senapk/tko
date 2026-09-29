import os
from pathlib import Path
import pytest
from tko.util.compare import Compare

class Test:
    @classmethod
    def setup_method(cls) -> None:
        os.chdir(Path(__file__).parent)

    def test_run_mixed_side(self, capsys: pytest.CaptureFixture[str]) -> None:
        cmd = "-w 80 -m run solver.cpp cases.tio --all --side"
        output = Compare.run(cmd)
        assert output.lower().count("runtime exception") == 3

    def test_run_side_0(self, capsys: pytest.CaptureFixture[str]) -> None:
        cmd = "-w 80 -m run solver.py cases.tio --down"
        Compare.text(capsys, "out3", cmd)
        
    def test_run_side_1(self, capsys: pytest.CaptureFixture[str]) -> None:
        cmd = "-w 80 -m run solver.py cases.tio --side"
        Compare.text(capsys, "out4", cmd)

    def test_run_side_2(self, capsys: pytest.CaptureFixture[str]) -> None:
        cmd = "-w 80 -m run solver.py cases.tio --all --down"
        Compare.text(capsys, "out5", cmd)

    def test_run_side_5(self, capsys: pytest.CaptureFixture[str]) -> None:
        cmd = "-w 80 -m run solver.cpp cases.tio --all --down"
        output = Compare.run(cmd)
        assert output.lower().count("runtime exception") == 3
