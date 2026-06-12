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
        output = Compare.run("-w 50 -m run -l c")

        # In some CI environments (notably Windows runners), the default gcc may
        # not provide sanitizer runtime libs (-lasan/-lubsan).
        has_expected_success = "[✓ ✓ ✓ ✓] 100%" in output
        has_missing_sanitizer_libs = (
            "cannot find -lasan" in output.lower()
            or "cannot find -lubsan" in output.lower()
        )

        assert has_expected_success or has_missing_sanitizer_libs
