import unittest
import os

from tko.__main__ import exec, Parser


class Test:
    def load(self):
        os.chdir("tests/06_failures")
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
            open(f"{test}.out", "w").write(out)
            out1 = out
        assert out == out1
            
    def test_run_all(self, capsys):
        self.load()
        self.exec("-w 80 -m go cases.tio draft.ts -ad")
        self.check(capsys, "test_1")
        self.restore()

    def test_run_first(self, capsys):
        self.load()
        self.exec("-w 80 -m go cases.tio draft.ts -d")
        self.check(capsys, "test_2")
        self.restore()

    def test_run_quiet(self, capsys):
        self.load()
        self.exec("-w 80 -m go cases.tio draft.ts -qd")
        self.check(capsys, "test_3")
        self.restore()

    # def test_run_mixed_2(self, capsys):
    #     self.load()
    #     self.exec("-w 80 -m go cases.tio solver.py -d")
    #     self.check(capsys, "test_2")
    #     self.restore()



if __name__ == '__main__':
    unittest.main()
