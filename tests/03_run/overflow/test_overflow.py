import unittest
import os

from tko.__main__ import exec, Parser


class Test:
    def load(self):
        os.chdir("tests/03_run/overflow")

        return self

    def restore(self):
        os.chdir("../../../")
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
            self.restore()
            assert out == out1
        else:
            open(f"{test}.out", "w").write(out)
            self.restore()
            assert False
            
    def test_run_mixed_1(self, capsys):
        self.load()
        self.exec("-w 80 -m go runtime.cpp cases.tio -as")
        self.check(capsys, "test_1")
        

    def test_run_mixed_2(self, capsys):
        self.load()
        self.exec("-w 80 -m go runtime.cpp")
        out = capsys.readouterr().out
        out1 = open(f"test_2.out").read()
        self.restore()
        assert "\n".join(out.split("\n")[1:]) == "\n".join(out1.split("\n")[1:])

    def test_run_mixed_3(self, capsys):
        self.load()
        self.exec("-w 80 -m go exception.py")
        self.check(capsys, "test_3")

    def test_run_mixed_4(self, capsys):
        self.load()
        self.exec("-w 80 -m go exception.cpp cases.tio -d")
        self.check(capsys, "test_4")

    def test_run_mixed_5(self, capsys):
        self.load()
        self.exec("-w 80 -m go exception.py cases.tio")
        self.check(capsys, "test_5")

if __name__ == '__main__':
    unittest.main()
