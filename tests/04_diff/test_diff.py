import unittest
import os

from tko.__main__ import exec, Parser


class Test:
    def load(self):
        os.chdir("tests/04_diff")
        return self

    def restore(self):
        os.chdir("../../")
        return self

    def exec(self, cmd):
        parser = Parser().parser
        args = parser.parse_args(cmd.split(" "))
        exec(parser, args)

    def check(self, capsys, test):
        out = capsys.readouterr().out
        out1 = ""
        if os.path.exists(f"{test}.out"):
            out1 = open(f"{test}.out").read()
        else:
            open(f"{test}.user", "w").write(out)
            out1 = out
        assert out == out1
            
    def test_run_mixed_1(self, capsys):
        self.load()
        self.exec("-w 80 -m go cases.tio solver.py -s")
        self.check(capsys, "test_1")
        self.restore()

    def test_run_mixed_2(self, capsys):
        self.load()
        self.exec("-w 80 -m go cases.tio solver.py -d")
        self.check(capsys, "test_2")
        self.restore()



if __name__ == '__main__':
    unittest.main()
