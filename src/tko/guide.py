tko_guide = """╭─────────────────────── TKO ─────────────────────────╮
│Mostrar esse guia : tko -g                           │
│Atualizar scripts : update.sh                        │
├─────────────────────────────────────────────────────┤
│Baixar o problema : tko down [fup|poo|ed] _id _ext   │
│ Exemplo para poo : tko down poo 012 cpp             │
├─────────────────────────────────────────────────────┤
│Rodar teste: tko run _codigo[s] _testes [-v] [-i ind]│
│    exemplo: tko run solver.cpp cases.tio            │
│  diff vert: tko run solver.cpp cases.tio -v         │
│ só teste 6: tko run solver.cpp cases.tio -i 6       │
├─────────────────────────────────────────────────────┤
│Executar sem testar: tko exec _codigo                │
│           exemplo : tko exec solver.ts              │
╰─────────────────────────────────────────────────────╯
"""

bash_guide = """╭─────────────────────── BASH ────────────────────────╮
│Mostrar esse guia : tko -b                           │
├─────────────────────────────────────────────────────┤
│Mostrar arquivos  : ls                               │
│Mudar de pasta    : cd _nome_da_pasta                │
│Subir um nível    : cd ..                            │
│Criar um arquivo  : touch _nome_do_arquivo           │
│Criar uma pasta   : mkdir _nome_da_pasta             │
│Limpar console    : Control L                        │
│Apagar um arquivo : rm _nome_do_arquivo              │
│Apagar uma pasta  : rm -r _nome_da_pasta             │
│Renomear ou mover : mv _antigo _novo                 │
╰─────────────────────────────────────────────────────╯
"""