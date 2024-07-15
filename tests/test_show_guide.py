import unittest

from tko.__main__ import exec, Parser

guide = """
       ╔════ TKO GUIA COMPACTO ════╗
╔══════╩═════ BAIXAR PROBLEMA ═════╩═══════╗
║        tko down <curso> <label>          ║
║ exemplo poo  : tko down poo carro        ║
║ exemplo fup  : tko down fup opala        ║
╟─────────── EXECUTAR SEM TESTAR ──────────╢
║          tko run <cod, cod...>           ║
║exemplo ts  : tko run solver.ts           ║
║exemplo cpp : tko run main.cpp lib.cpp    ║
╟──────── ABRIR O MODO INTERATIVO ─────────╢
║              tko play <curso>            ║
║exemplo:      tko play fup                ║
╟──────────── RODAR OS TESTES ─────────────╢
║   tko run cases.tio <cod, ...> [-i ind]  ║
║ exemplo: tko run cases.tio main.ts       ║
╟── DEFINIR EXTENSÃO PADRÃO DOS RASCUNHOS ─╢
║           tko config -l <ext>            ║
║     exemplo c : tko config -l c          ║
║  exemplo java : tko config -l java       ║
╟─────────── MUDAR VISUALIZAÇÃO ───────────╢
║             tko config <--opcao>         ║
║DiffMode: tko config [--side  | --down ]  ║
║Cores   : tko config [--mono  | --color  ]║
║Encoding: tko config [--ascii | --unicode]║
╚══════════════════════════════════════════╝
"""[1:]

class Test:
    def test_guide(self, capsys):
        parser = Parser().parser
        args = parser.parse_args(["-g"])
        exec(parser, args)
        capture = capsys.readouterr()
        assert capture.out == guide


if __name__ == '__main__':
    unittest.main()
