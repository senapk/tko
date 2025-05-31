import os
from pathlib import Path
import pytest
from tko.util.compare import Compare

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)

    def test_simple_list1(self, capsys: pytest.CaptureFixture[str]):
        Compare.list(capsys, "out1", ["-m", "run", "cases.tio"])

    def test_simple_list2(self, capsys: pytest.CaptureFixture[str]):
        Compare.list(capsys, "out2", ["-m", "run", "cases.tio", "cases2.tio"])
