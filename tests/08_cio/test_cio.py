import unittest
import os
from typing import Tuple

from tko.__main__ import exec, Parser


class Test:
    def load(self):
        os.chdir("tests/08_cio")
        return self

    def restore(self):
        os.chdir("../../")
        return self

    def exec(self, cmd):
        parser = Parser().parser
        args = parser.parse_args(cmd.split(" "))
        exec(parser, args)

    def get_exp_rec(self, capsys, test) -> Tuple[str, str]:
        received = capsys.readouterr().out
        expected = ""
        if os.path.exists(f"{test}.out"):
            expected = open(f"{test}.out").read()
            if expected != received:
                open(f"{test}.user", "w").write(received)
        else:
            open(f"{test}.out", "w").write(received)
            expected = received

        return expected, received
            
    def test_cio_1(self, capsys):
        self.load()
        self.exec("build _calc.tio calc.md")
        data = open("_calc.tio").read()
        print(data)
        expected, received = self.get_exp_rec(capsys, "test_1")
        os.remove("_calc.tio")
        self.restore()
        assert expected == received

    def test_cio_2(self, capsys):
        self.load()
        self.exec("build _calc2.tio calc2.md")
        data = open("_calc2.tio").read()
        print(data)
        expected, received = self.get_exp_rec(capsys, "test_2")
        os.remove("_calc2.tio")
        self.restore()
        assert expected == received

if __name__ == '__main__':
    unittest.main()
