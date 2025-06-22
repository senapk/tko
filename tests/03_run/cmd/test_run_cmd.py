import os
from pathlib import Path
import pytest
from tko.util.compare import Compare

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)

    def test_run_cmd(self, capsys: pytest.CaptureFixture[str]):
        cmd2 = ["-w", "50", "-m", "run", "solver.yaml", "cases.tio"]
        Compare.list(capsys, "out1", cmd2)
