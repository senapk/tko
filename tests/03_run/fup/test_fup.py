import unittest
import os

from tko.__main__ import exec, Parser

out_1 = """
═══════ Running solver against test cases ═══════
base:[cases.tio(03)] prog:[free cmd] [✓ ✓ ✓]
"""[1:]

class Test:
    def load(self):
        os.chdir("tests/03_run/fup")

        return self

    def restore(self):
        os.chdir("../../../")
        return self

    def test_run_cmd(self, capsys):
        self.load()
        parser = Parser().parser
        cmd = "-m go solver.cpp cases.tio -as"
        args = parser.parse_args(cmd.split(" "))
        exec(parser, args)
        capture = capsys.readouterr()
        out = capture.out
        out1 = open("zz_a_cpp_mixed_output.out").read()
        assert out == out1
        self.restore()





if __name__ == '__main__':
    unittest.main()
