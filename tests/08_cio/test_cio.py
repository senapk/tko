import unittest
import os
from pathlib import Path
from tko.__main__ import execute, Parser #type: ignore
from tko.util.compare import Compare

class Test:
    @classmethod
    def setup_method(cls):
        os.chdir(Path(__file__).parent)
    
    def test_cio_1(self, capsys): # type: ignore
        # path = os.path.join(Test.folder + "_calc.tio")
        # if os.path.exists(path):
        #     os.remove(path)
        # Compare.text(capsys, "out1", "build _calc.tio calc.md")
        Compare.text(capsys, "out2", "-w 50 -m run _calc.tio -d") 
        Compare.text(capsys, "out3", "-w 50 -m run _calc.tio empty.py -d")
        
    def test_cio_2(self, capsys): # type: ignore
        # path = os.path.join(Test.folder, "_calc2.tio")
        # if os.path.exists(path):
        #     os.remove(path)
        # Compare.text(capsys, "out4", "build _calc2.tio calc2.md")
        Compare.text(capsys, "out5", "-w 50 -m run _calc2.tio -d")
        Compare.text(capsys, "out6", "-w 50 -m run _calc2.tio empty.py -d")
        

if __name__ == '__main__':
    unittest.main()
