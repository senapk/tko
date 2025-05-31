import os
from pathlib import Path
import pytest
from tko.__main__ import execute, Parser #type: ignore
from tko.util.compare import Compare # type: ignore

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)

    def test_run_1(self, capsys: pytest.CaptureFixture[str]):
        cmd = ["-m", "run", "solver.yaml", "cases.tio"]
        Compare.list(capsys, "out1", cmd)

    def test_run_2(self, capsys: pytest.CaptureFixture[str]):
        cmd = ["-m", "run", "solver.yaml", "wrong.tio", "-s"]
        Compare.list(capsys, "out2", cmd)
