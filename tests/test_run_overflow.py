import unittest

from .compare import compare_text

class Test:
    folder = "tests/03_run/overflow"

            
    def test_run_mixed_1(self, capsys):
        compare_text(capsys, Test.folder, "out1", "-w 80 -m test runtime.cpp cases.tio -as")

    # def test_run_mixed_2(self, capsys):
    #     compare_text(capsys, "-w 80 -m test runtime.cpp", "out2")

    def test_run_mixed_3(self, capsys):
        compare_text(capsys, Test.folder, "out2", "-w 80 -m test exception.py")

    def test_run_mixed_4(self, capsys):
        compare_text(capsys, Test.folder, "out3", "-w 80 -m test exception.cpp cases.tio -d")

    def test_run_mixed_5(self, capsys):
        compare_text(capsys, Test.folder, "out4", "-w 80 -m test exception.py cases.tio")

if __name__ == '__main__':
    unittest.main()
