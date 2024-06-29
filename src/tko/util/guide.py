tko_guide = """
       ╔════ TKO GUIA COMPACTO ════╗
╔══════╩═════ BAIXAR PROBLEMA ═════╩═══════╗
║        tko down <curso> <label>          ║
║ exemplo poo  : tko down poo carro        ║
║ exemplo fup  : tko down fup opala        ║
╟─────────── EXECUTAR SEM TESTAR ──────────╢
║          tko run <cod, cod...>           ║
║exemplo ts  : tko run solver.ts           ║
║exemplo cpp : tko run main.cpp lib.cpp    ║
╟──────────── RODAR OS TESTES ─────────────╢
║   tko run cases.tio <cod, ...> [-i ind]  ║
║ exemplo: tko run cases.tio main.ts       ║
║só ind 6: tko run cases.tio main.c -i 6   ║
╟── DEFINIR EXTENSÃO PADRÃO DOS RASCUNHOS ─╢
║           tko config -l <ext>            ║
║     exemplo c : tko config -l c          ║
║  exemplo java : tko config -l java       ║
╟─────────── MUDAR VISUALIZAÇÃO ───────────╢
║             tko config <--opcao>         ║
║DiffMode: tko config [--side  | --updown ]║
║Cores   : tko config [--mono  | --color  ]║
║Encoding: tko config [--ascii | --unicode]║
╚══════════════════════════════════════════╝
"""

bash_guide = """
       ╔═══ BASH  GUIA COMPACTO ════╗
╔══════╩════ MOSTRAR E NAVEGAR ═════╩══════╗
║Mostrar arquivos  : ls                    ║
║Mostrar ocultos   : ls -la                ║
║Mudar de pasta    : cd _nome_da_pasta     ║
║Subir um nível    : cd ..                 ║
╟─────────────── CRIAR ────────────────────╢
║Criar um arquivo  : touch _nome_do_arquivo║
║Criar uma pasta   : mkdir _nome_da_pasta  ║
╟─────────────── REMOVER ──────────────────╢
║Apagar um arquivo : rm _nome_do_arquivo   ║
║Apagar uma pasta  : rm -r _nome_da_pasta  ║
║Renomear ou mover : mv _antigo _novo      ║
╟─────────────── CONTROLAR ────────────────╢
║Últimos comandos  : SETA PRA CIMA         ║
║Limpar console    : Control L             ║
║Cancelar execução : Control C             ║
║Finalizar entrada : Control D             ║
╚══════════════════════════════════════════╝
"""