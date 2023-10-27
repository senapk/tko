tko_guide = """
╔═════════════ TKO SIMPLE GUIDE ═══════════╗
║Toggle diff [up   | side ] : tko config -d║
║Toggle color[mono | color] : tko config -c║
╟───────────────── BAIXAR ─────────────────╢
║Baixar config : tko down _disc _id _ext   ║
║ Exemplo poo  : tko down poo 012 cpp      ║
╟──────────────── EXECUTAR ────────────────╢
║   Executar: tko run _codigo[s]           ║
║   exemplo : tko run solver.ts            ║
║   exemplo : tko run main.cpp lib.cpp     ║
╟───────────────── TESTAR ─────────────────╢
║    Testar: tko run _cod[s] _tio [-i ind] ║
║   exemplo: tko run main.ts cases.tio     ║
║ só caso 6: tko run main.ts cases.tio -i 6║
╚══════════════════════════════════════════╝
"""

bash_guide = """
╭───────────── BASH SIMPLE GUIDE ──────────╮
│Mostrar arquivos  : ls                    │
│Mudar de pasta    : cd _nome_da_pasta     │
│Subir um nível    : cd ..                 │
├─────────────── CRIAR ────────────────────┤
│Criar um arquivo  : touch _nome_do_arquivo│
│Criar uma pasta   : mkdir _nome_da_pasta  │
├─────────────── REMOVER ──────────────────┤
│Apagar um arquivo : rm _nome_do_arquivo   │
│Apagar uma pasta  : rm -r _nome_da_pasta  │
│Renomear ou mover : mv _antigo _novo      │
├─────────────── CONTROLAR ────────────────┤
│Últimos comandos  : SETA PRA CIMA         │
│Limpar console    : Control L             │
│Cancelar execução : Control C             │
│Finalizar entrada : Control D             │
╰──────────────────────────────────────────╯
"""