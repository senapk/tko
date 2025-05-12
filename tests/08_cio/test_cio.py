import unittest
import os
from pathlib import Path
from tko.__main__ import exec, Parser #type: ignore
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
        Compare.text(capsys, "out2", "-w 50 -m exec _calc.tio") 
        Compare.text(capsys, "out3", "-w 50 -m exec _calc.tio empty.py")
        
    def test_cio_2(self, capsys): # type: ignore
        # path = os.path.join(Test.folder, "_calc2.tio")
        # if os.path.exists(path):
        #     os.remove(path)
        # Compare.text(capsys, "out4", "build _calc2.tio calc2.md")
        Compare.text(capsys, "out5", "-w 50 -m exec _calc2.tio")
        Compare.text(capsys, "out6", "-w 50 -m exec _calc2.tio empty.py")
        

if __name__ == '__main__':
    unittest.main()
