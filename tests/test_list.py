import unittest
from .compare import compare_list

class Test:
    def test_simple_list1(self, capsys):
        folder = "tests/02_list"
        compare_list(capsys, folder, "out1", ["-m", "run", "cases.tio"])

    def test_simple_list2(self, capsys):
        folder = "tests/02_list"
        compare_list(capsys, folder, "out2", ["-m", "run", "cases.tio", "cases2.tio"])

if __name__ == '__main__':
    unittest.main()
