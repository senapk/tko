import unittest

from .compare import compare_text

class Test:
    def test_all(self, capsys):
        f = "tests/06_failures"
        compare_text(capsys, f, "out1", "-w 80 -m test cases.tio draft.ts -ad")
        compare_text(capsys, f, "out2", "-w 80 -m test cases.tio draft.ts -d")
        compare_text(capsys, f, "out3", "-w 80 -m test cases.tio draft.ts -qd")

if __name__ == '__main__':
    unittest.main()
