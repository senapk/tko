import os
from pathlib import Path
import pytest
from tko.util.compare import Compare # type: ignore

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)

    def test_run_1(self, capsys: pytest.CaptureFixture[str]):
        cmd = ["-w", "80", "-m", "run", "solver.mk", "cases.tio"]
        Compare.list(capsys, "out1", cmd)

    def test_run_2(self, capsys: pytest.CaptureFixture[str]):
        cmd = ["-w", "80", "-m", "run", "solver.mk", "wrong.tio", "-s"]
        Compare.list(capsys, "out2", cmd)
