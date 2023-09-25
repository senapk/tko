tko_guide = """
╔══════════════════ TKO SIMPLE GUIDE ═════════════════╗
║Toggle diff [up_down | side-by-side] : tko config -d ║
║Toggle color[mono    | colors]       : tko config -c ║
╟────────────────────── BAIXAR ───────────────────────╢
║Baixar o problema  : tko down [fup|poo|ed] _id _ext  ║
║ Exemplo para poo  : tko down poo 012 cpp            ║
╟────────────────────── EXECUTAR ─────────────────────╢
║Compilar e executar: tko run _codigo[s]              ║
║           exemplo : tko run solver.ts               ║
║           exemplo : tko run main.cpp lib.cpp        ║
╟────────────────────── TESTAR ───────────────────────╢
║Compilar e testar: tko run _codigo[s] _cases [-i ind]║
║    exemplo: tko run solver.cpp cases.tio            ║
║ só teste 6: tko run solver.cpp cases.tio -i 6       ║
╚═════════════════════════════════════════════════════╝
"""

bash_guide = """
╭────────────────── BASH SIMPLE GUIDE ────────────────╮
│Mostrar esse guia : tko -g                           │
├────────────────────── NAVEGAR ──────────────────────┤
│Mostrar arquivos  : ls                               │
│Mudar de pasta    : cd _nome_da_pasta                │
│Subir um nível    : cd ..                            │
├─────────────────────── CRIAR ───────────────────────┤
│Criar um arquivo  : touch _nome_do_arquivo           │
│Criar uma pasta   : mkdir _nome_da_pasta             │
├────────────────────── REMOVER ──────────────────────┤
│Apagar um arquivo : rm _nome_do_arquivo              │
│Apagar uma pasta  : rm -r _nome_da_pasta             │
│Renomear ou mover : mv _antigo _novo                 │
├───────────────────── CONTROLAR ─────────────────────┤
│Limpar console    : Control L                        │
│Cancelar execução : Control C                        │
│Finalizar entrada : Control D                        │
╰─────────────────────────────────────────────────────╯
"""