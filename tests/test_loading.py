import unittest

from .compare import compare_text


class Test:           
    folder = "tests/05_loading"
    def test_run_mixed_1(self, capsys):
        compare_text(capsys, Test.folder,  "out1", "-w 80 -m test")
    def test_run_mixed_5(self, capsys):
        compare_text(capsys, Test.folder,  "out5", "-w 80 -m test cases.tio")
    def test_run_mixed_6(self, capsys):
        compare_text(capsys, Test.folder,  "out6", "-w 80 -m test solver.py")
    def test_run_mixed_7(self, capsys):
        compare_text(capsys, Test.folder,  "out7", "-w 80 -m test solver.py cases_empty.tio")
    def test_run_mixed_8(self, capsys):
        compare_text(capsys, Test.folder,  "out8", "-w 80 -m test solver.py cases.tio")
        

if __name__ == '__main__':
    unittest.main()
