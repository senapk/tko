import os
from pathlib import Path
from tko.util.compare import Compare
import pytest

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)
    
    def test_not_defined(self, capsys: pytest.CaptureFixture[str]): # type: ignore
        Compare.text(capsys, "not_defined", "-w 50 -m run")

    def test_defined(self, capsys: pytest.CaptureFixture[str]): # type: ignore
        Compare.text(capsys, "defined", "-w 50 -m run -l c") 
