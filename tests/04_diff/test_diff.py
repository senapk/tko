import os
from pathlib import Path
import pytest
from tko.util.compare import Compare

class Test:
    @classmethod
    def setup_method(cls) -> None:
        os.chdir(Path(__file__).parent)
                
    def test_run_mixed_1(self, capsys: pytest.CaptureFixture[str]) -> None:
        Compare.text(capsys, "out1", "-w 80 -m run cases.tio solver.py --diff-mode side")


    def test_run_mixed_2(self, capsys: pytest.CaptureFixture[str]) -> None:
        Compare.text(capsys, "out2", "-w 80 -m run cases.tio solver.py --diff-mode down")
