import os
from pathlib import Path
import pytest
from tko.util.compare import Compare

class Test:
    @classmethod
    def setup_method(cls) -> None:
        os.chdir(Path(__file__).parent)

    # def test_run_mixed_1(self, capsys: pytest.CaptureFixture[str]) -> None:
    #     Compare.text(capsys, "out1", "-w 80 -m run runtime.cpp cases.tio --all --down")

    # def test_run_mixed_2(self, capsys: pytest.CaptureFixture[str]) -> None:
    #     Compare.text(capsys, "-w 80 -m run runtime.cpp", "out2")

    def test_run_mixed_3(self, capsys: pytest.CaptureFixture[str]) -> None:
        output = Compare.run("-w 80 -m run exception.py --down")
        assert output.lower().count("runtime exception") == 0

    # def test_run_mixed_4(self, capsys: pytest.CaptureFixture[str]) -> None:
    #     Compare.text(capsys, "out3", "-w 80 -m run exception.cpp cases.tio --down")

    # def test_run_mixed_5(self, capsys: pytest.CaptureFixture[str]) -> None:
    #     Compare.text(capsys, "out4", "-w 80 -m run exception.py cases.tio --side")
