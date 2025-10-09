import os
from pathlib import Path
import pytest
from tko.__main__ import execute, Parser #type: ignore
from tko.util.compare import Compare # type: ignore

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)
            
#    def test_run_mixed_1(self, capsys: pytest.CaptureFixture[str]):
#        Compare.text(capsys, "out1", "-w 80 -m run draft.ts cases.tio -s")

    def test_run_mixed_2(self, capsys: pytest.CaptureFixture[str]):
        Compare.text(capsys, "out2", "-w 80 -m run solver.cpp cases.tio -s")

#    def test_run_mixed_3(self, capsys: pytest.CaptureFixture[str]):
#        Compare.text(capsys, "out3", "-w 80 -m run draft.ts cases.tio -d")
