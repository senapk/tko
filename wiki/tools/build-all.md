# Build all - pipeline de automacao de artefatos

Este guia documenta o que o comando abaixo faz na pratica:

```bash
tko build all
```

## Visao geral

O comando tko build all roda um pipeline de preparacao de artefatos por pasta alvo.

No fluxo padrao, ele:

- Atualiza markdown com o preprocessador mdpp.
- Gera starters em .cache/starter a partir de src usando filtro por marcadores.
- Pode executar local.sh quando existir.
- Atualiza markdown novamente (para refletir mudancas causadas pelo passo anterior).

No fluxo moodle (opcional), ele tambem:

- Gera README rebaseado para remoto/local.
- Gera HTML do enunciado.
- Gera arquivo de testes.
- Mantem os starters filtrados por linguagem em `.cache/starter`.

## Comando e opcoes

Uso basico:

```bash
tko build all
```

Com alvos especificos:

```bash
tko build all labs/tres labs/media
```

Opcoes principais:

- -c, --check: so reconstrui quando detectar mudancas.
- -b, --brief: reduz logs.
- -m, --moodle: ativa pipeline de artefatos Moodle (README rebaseado, html, tests.vpl e starters).
- -l, --local: nao usa configuracao remota para links absolutos.
- -e, --erase: apaga arquivos temporarios de saida (README.md, README.html, tests.vpl em .cache).

## Ordem real das etapas

Para cada alvo (diretorio):

1. Carrega titulo do README.
2. Garante pasta .cache.
3. Executa mdpp no README da origem.
4. Se precisar rebuild (ou sem --check), limpa .cache e segue:
5. Gera starters com DeepFilter de src para .cache/starter.
6. Executa local.sh (se existir).
7. Executa mdpp novamente.
8. Se --moodle:
   - rebase de links (README para .cache/README.md)
   - gera .cache/README.html
   - gera .cache/tests.vpl
9. Se --erase, remove alguns artefatos temporarios.

## Artefatos gerados

No modo Moodle, os artefatos ficam dentro da pasta `.cache` da tarefa:

- `.cache/README.md`: copia especial do README da tarefa, com links locais reescritos. Imagens apontam para `raw.githubusercontent.com`; links para arquivos apontam para `github.com/.../blob`; links para pastas apontam para `github.com/.../tree`.
- `.cache/README.html`: HTML gerado a partir de `.cache/README.md`, usado como enunciado no Moodle.
- `.cache/tests.vpl`: arquivo de casos gerado a partir do `README.md` e dos arquivos `.tio`, `.vpl` e `.toml` encontrados na tarefa.
- `.cache/starter/<linguagem>/...`: starters filtrados a partir de `src/<linguagem>/...`, preservando a estrutura de arquivos por linguagem.

## Relacao com mdpp, filter e rascunhos

### mdpp

O build chama internamente o preprocessador markdown para atualizar o README.

Relaciona-se ao comando manual:

```bash
tko tool mdpp README.md
```

### filter e drafts

O build usa DeepFilter sobre src e envia resultado para .cache/starter.

Relaciona-se ao comando manual:

```bash
tko tool filter src -r -o .cache/starter
```

Observacao: no build, o filtro e chamado pelo pipeline interno, com indentacao configurada, focando geracao de drafts.

### rascunhos

Os rascunhos usados como starters ficam em .cache/starter durante a montagem de artefatos no modo moodle.

## Exemplo rapido (repositorio da disciplina)

Na raiz de uma tarefa:

```bash
# pipeline padrao: mdpp + drafts (+ local.sh se existir)
tko build all .

# pipeline completo para moodle
tko build all . -m

# so reconstruir se houver mudancas
tko build all . -c -m
```

## Quando usar cada modo

- build all sem -m:
  - ciclo rapido de preparacao local.
  - atualizacao de markdown e drafts.

- build all com -m:
  - geracao de artefatos para publicacao/empacotamento (README rebaseado, html, tests.vpl e starters).

## Observacoes importantes

- Se nenhum alvo for informado, o comando usa o diretorio atual.
- Pastas iniciadas com ., _ e + sao ignoradas no pipeline.
- local.sh e opcional e executado no diretorio da tarefa.
- O comportamento de links remotos depende de remote.toml quando aplicavel.
