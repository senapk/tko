import unittest
import os

from tko.__main__ import exec, Parser


class Test:
    def load(self):
        os.chdir("tests/03_run/sql")

    def restore(self):
        os.chdir("../../../")

    def test_run_1(self, capsys):
        self.load()
        parser = Parser().parser
        cmd = "cat create.sql solver.sql | sqlite3"
        args = parser.parse_args(["-m", "go", "--cmd", cmd, "cases.tio"])
        exec(parser, args)
        out = capsys.readouterr().out
        expected = open("test_1.out").read()
        assert out == expected
        self.restore()

    def test_run_2(self, capsys):
        self.load()
        parser = Parser().parser
        args = parser.parse_args("-w 80 -m go create.sql student.sql".split(" "))
        exec(parser, args)
        out = capsys.readouterr().out
        expected = open("test_2.out").read()
        self.restore()
        assert out == expected


if __name__ == '__main__':
    unittest.main()
