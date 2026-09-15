import os
from pathlib import Path
import pytest
from tko.util.compare import Compare

class Test:
    @classmethod
    def setup_method(cls) -> None:
        os.chdir(Path(__file__).parent)

    def test_run_mixed_side(self, capsys: pytest.CaptureFixture[str]) -> None:
        cmd = "-w 80 -m run solver.cpp cases.tio --failures all --diff-mode side"
        output = Compare.run(cmd)
        assert output.lower().count("runtime exception") == 3

    def test_run_side_0(self, capsys: pytest.CaptureFixture[str]) -> None:
        cmd = "-w 80 -m run solver.py cases.tio --diff-mode down"
        Compare.text(capsys, "out3", cmd)
        
    def test_run_side_1(self, capsys: pytest.CaptureFixture[str]) -> None:
        cmd = "-w 80 -m run solver.py cases.tio --diff-mode side"
        Compare.text(capsys, "out4", cmd)

    def test_run_side_2(self, capsys: pytest.CaptureFixture[str]) -> None:
        cmd = "-w 80 -m run solver.py cases.tio --failures all --diff-mode down"
        Compare.text(capsys, "out5", cmd)

    def test_run_side_5(self, capsys: pytest.CaptureFixture[str]) -> None:
        cmd = "-w 80 -m run solver.cpp cases.tio --failures all --diff-mode down"
        output = Compare.run(cmd)
        assert output.lower().count("runtime exception") == 3
