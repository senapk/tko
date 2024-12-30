rota_guide = """
       ╔════ rota GUIA COMPACTO ════╗
╔══════╩═════ BAIXAR PROBLEMA ═════╩═══════╗
║        rota down <curso> <label>          ║
║ exemplo poo  : rota down poo carro        ║
║ exemplo fup  : rota down fup opala        ║
╟─────────── EXECUTAR SEM TESTAR ──────────╢
║          rota run <cod, cod...>           ║
║exemplo ts  : rota run solver.ts           ║
║exemplo cpp : rota run main.cpp lib.cpp    ║
╟──────── ABRIR O MODO INTERATIVO ─────────╢
║              rota play <curso>            ║
║exemplo:      rota play fup                ║
╟──────────── RODAR OS TESTES ─────────────╢
║   rota run cases.tio <cod, ...> [-i ind]  ║
║ exemplo: rota run cases.tio main.ts       ║
╟── DEFINIR EXTENSÃO PADRÃO DOS RASCUNHOS ─╢
║           rota config -l <ext>            ║
║     exemplo c : rota config -l c          ║
║  exemplo java : rota config -l java       ║
╟─────────── MUDAR VISUALIZAÇÃO ───────────╢
║             rota config <--opcao>         ║
║DiffMode: rota config [--side  | --down ]  ║
║Cores   : rota config [--mono  | --color  ]║
║Encoding: rota config [--ascii | --unicode]║
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