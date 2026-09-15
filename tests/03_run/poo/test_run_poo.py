import os
from pathlib import Path
import pytest
from tko.util.compare import Compare

class Test:
    @classmethod
    def setup_method(cls) -> None:
        os.chdir(Path(__file__).parent)
            
#    def test_run_mixed_1(self, capsys: pytest.CaptureFixture[str]) -> None:
#        Compare.text(capsys, "out1", "-w 80 -m run draft.ts cases.tio --diff-mode side")

    def test_run_mixed_2(self, capsys: pytest.CaptureFixture[str]) -> None:
        Compare.text(capsys, "out2", "-w 80 -m run solver.cpp cases.tio --diff-mode side")

#    def test_run_mixed_3(self, capsys: pytest.CaptureFixture[str]) -> None:
#        Compare.text(capsys, "out3", "-w 80 -m run draft.ts cases.tio --diff-mode down")
