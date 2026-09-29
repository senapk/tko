import os
from pathlib import Path
from tko.util.compare import Compare
import pytest

class Test:
    @classmethod
    def setup_method(cls) -> None:
        os.chdir(Path(__file__).parent)

    def test_cio_1(self, capsys: pytest.CaptureFixture[str]) -> None:
        Compare.text(capsys, "out2", "-w 50 -m run _calc.tio --down")
        Compare.text(capsys, "out3", "-w 50 -m run _calc.tio empty.py --down")

    def test_cio_2(self, capsys: pytest.CaptureFixture[str]) -> None:
        Compare.text(capsys, "out5", "-w 50 -m run _calc2.tio --down")
        Compare.text(capsys, "out6", "-w 50 -m run _calc2.tio empty.py --down")

