import unittest
import os

from tko.__main__ import exec, Parser

out_simple = """
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌ No solvers found. Listing Test Cases ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
base:[cases.tio(10)] prog:[]
(. untested_)[00] GR:010 tests/02_list/cases.tio (iniciar mostrar e recarregar)
(. untested_)[01] GR:010 tests/02_list/cases.tio (boundary                    )
(. untested_)[02] GR:010 tests/02_list/cases.tio (reset                       )
(. untested_)[03] GR:010 tests/02_list/cases.tio (somando                     )
(. untested_)[04] GR:010 tests/02_list/cases.tio (gastando bateria            )
(. untested_)[05] GR:010 tests/02_list/cases.tio (sem bateria                 )
(. untested_)[06] GR:010 tests/02_list/cases.tio (recarregando                )
(. untested_)[07] GR:010 tests/02_list/cases.tio (dividindo                   )
(. untested_)[08] GR:010 tests/02_list/cases.tio (dividindo por zero          )
(. untested_)[09] GR:010 tests/02_list/cases.tio (gastando bateria            )
"""[1:]

out_repeated = """
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌ No solvers found. Listing Test Cases ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
base:[cases.tio(10), cases2.tio(03)] prog:[]
(. untested_)[00] GR:008 tests/02_list/cases.tio  (iniciar mostrar e recarregar)
(. untested_)[01] GR:008 tests/02_list/cases.tio  (boundary                    )
(. untested_)[02] GR:008 tests/02_list/cases.tio  (reset                       )
(. untested_)[03] GR:008 tests/02_list/cases.tio  (somando                     )
(. untested_)[04] GR:008 tests/02_list/cases.tio  (gastando bateria            )
(. untested_)[05] GR:008 tests/02_list/cases.tio  (sem bateria                 )
(. untested_)[06] GR:008 tests/02_list/cases.tio  (recarregando                )
(. untested_)[07] GR:008 tests/02_list/cases.tio  (dividindo                   )
(. untested_)[08] GR:008 tests/02_list/cases.tio  (dividindo por zero          )
(. untested_)[09] GR:008 tests/02_list/cases.tio  (gastando bateria            )
(. untested_)[10] GR:008 tests/02_list/cases2.tio (iniciar mostrar e recarregar) [0]
(. untested_)[11] GR:008 tests/02_list/cases2.tio (boundary                    ) [1]
(. untested_)[12] GR:008 tests/02_list/cases2.tio (novo teste                  )
"""[1:]

class Test:
    def test_simple_list(self, capsys):
        parser = Parser().parser
        args = parser.parse_args(["-m", "-a", "run", "tests/02_list/cases.tio"])
        # print(os.getcwd())
        exec(parser, args)
        capture = capsys.readouterr()
        assert capture.out == out_simple

    def test_repeated(self, capsys):
        parser = Parser().parser
        args = parser.parse_args(["-m", "-a", "run", "tests/02_list/cases.tio", "tests/02_list/cases2.tio"])
        exec(parser, args)
        capture = capsys.readouterr()
        assert capture.out == out_repeated

if __name__ == '__main__':
    unittest.main()
