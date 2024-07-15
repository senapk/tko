import unittest
import os

from tko.__main__ import exec, Parser


class Test:
    def load(self):
        os.chdir("tests/03_run/fup")

        return self

    def restore(self):
        os.chdir("../../../")
        return self

    def test_run_mixed_side(self, capsys):
        self.load()
        parser = Parser().parser
        cmd = "-w 80 -m go solver.cpp cases.tio -as"
        args = parser.parse_args(cmd.split(" "))
        exec(parser, args)
        out = capsys.readouterr().out
        out1 = open("test_1.out").read()
        assert out == out1
        self.restore()

    def test_run_mixed_down(self, capsys):
        self.load()
        parser = Parser().parser
        cmd = "-w 80 -m go solver.cpp cases.tio -ad"
        args = parser.parse_args(cmd.split(" "))
        exec(parser, args)
        out = capsys.readouterr().out
        out1 = open("test_2.out").read()
        # open("test_0.out", "w").write(out)
        assert out == out1
        self.restore()


    def test_run_error_1(self, capsys):
        self.load()
        parser = Parser().parser
        cmd = "-w 80 -m go solver.py cases.tio -d"
        args = parser.parse_args(cmd.split(" "))
        exec(parser, args)
        out = capsys.readouterr().out
        out1 = open("test_3.out").read()
        # open("test_01.out", "w").write(out)
        assert out == out1
        self.restore()

    def test_run_error_2(self, capsys):
        self.load()
        parser = Parser().parser
        cmd = "-w 80 -m go solver.py cases.tio -s"
        args = parser.parse_args(cmd.split(" "))
        exec(parser, args)
        out = capsys.readouterr().out
        out1 = open("test_4.out").read()
        # open("test_02.out", "w").write(out)
        assert out == out1
        self.restore()

    def test_run_error_3(self, capsys):
        self.load()
        parser = Parser().parser
        cmd = "-w 80 -m go solver.py cases.tio -a"
        args = parser.parse_args(cmd.split(" "))
        exec(parser, args)
        out = capsys.readouterr().out
        out1 = open("test_5.out").read()
        # open("gen.out", "w").write(out)
        assert out == out1
        self.restore()

if __name__ == '__main__':
    unittest.main()
