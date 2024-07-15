import unittest
import os

from tko.__main__ import exec, Parser

out_1 = """
═══════ Running solver against test cases ═══════
=> base:[cases.tio(03)] prog:[free cmd] [✓ ✓ ✓]
"""[1:]

class Test:
    def load(self):
        self.args = ["-w", "50", "-m"]
        os.chdir("tests/03_run/cmd")

    def restore(self):
        os.chdir("../../..")
        pass

    def test_run_cmd(self, capsys):
        self.load()
        parser = Parser().parser
        cmd = "g++ solver.cpp -o solver.out && ./solver.out"
        args = parser.parse_args(self.args + ["go", "--cmd", cmd, "cases.tio"])
        exec(parser, args)
        capture = capsys.readouterr()
        out = capture.out

        assert out == out_1
        self.restore()

    def test_run_makefile(self, capsys):
        self.load()
        parser = Parser().parser
        cmd = "make -s solver.out && ./solver.out"
        args = parser.parse_args(["-w", "50", "-m", "go", "--cmd", cmd, "cases.tio"])
        exec(parser, args)
        capture = capsys.readouterr()
        out = capture.out
        assert out == out_1
        self.restore()



if __name__ == '__main__':
    unittest.main()
