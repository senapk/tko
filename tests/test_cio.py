import unittest
import os
from typing import Tuple

from .compare import compare_text

class Test:
    folder = "tests/08_cio"
    
    def test_cio_1(self, capsys):
        path = Test.folder + "/_calc.tio"
        if os.path.exists(path):
            os.remove(path)
        compare_text(capsys, Test.folder, "out1", "build _calc.tio calc.md")
        compare_text(capsys, Test.folder, "out2", "-w 50 -m test _calc.tio")
        compare_text(capsys, Test.folder, "out3", "-w 50 -m test _calc.tio empty.py")
        
    def test_cio_2(self, capsys):
        path = Test.folder + "_calc2.tio"
        if os.path.exists(path):
            os.remove(path)
        compare_text(capsys, Test.folder, "out4", "build _calc2.tio calc2.md")
        compare_text(capsys, Test.folder, "out5", "-w 50 -m test _calc2.tio")
        compare_text(capsys, Test.folder, "out6", "-w 50 -m test _calc2.tio empty.py")
        

if __name__ == '__main__':
    unittest.main()
