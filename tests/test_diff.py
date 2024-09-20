import unittest

from .compare import compare_text

class Test:
    folder = "tests/04_diff"
                
    def test_run_mixed_1(self, capsys):
        compare_text(capsys, Test.folder, "out1", "-w 80 -m test cases.tio solver.py -s")


    def test_run_mixed_2(self, capsys):
        compare_text(capsys, Test.folder, "out2", "-w 80 -m test cases.tio solver.py -d")

if __name__ == '__main__':
    unittest.main()
