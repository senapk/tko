import os
from pathlib import Path
import pytest
from tko.util.compare import Compare

class Test:
    @classmethod
    def setup_method(cls) -> None:
        os.chdir(Path(__file__).parent)

    def test_run_mixed_side(self, capsys: pytest.CaptureFixture[str]) -> None:
        cmd = "-w 80 -m run main.cpp lib.cpp cases.tio --failures all --diff-mode side"
        Compare.text(capsys, "out1", cmd)
