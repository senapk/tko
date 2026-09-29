import os
from pathlib import Path
import pytest
from tko.util.compare import Compare

class Test:
    @classmethod
    def setup_method(cls) -> None:
        os.chdir(Path(__file__).parent)

    def test_all(self, capsys: pytest.CaptureFixture[str]) -> None:
        Compare.text(capsys, "out1", "-w 80 -m run cases.tio draft.ts --all --down")
        Compare.text(capsys, "out2", "-w 80 -m run cases.tio draft.ts --down")
        Compare.text(capsys, "out3", "-w 80 -m run cases.tio draft.ts --compact --none --down")
