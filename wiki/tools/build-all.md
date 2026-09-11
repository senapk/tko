# Build task - pipeline de automacao de artefatos

Este guia documenta o que o comando abaixo faz na pratica:

```bash
tko task build
```

## Visao geral

O comando tko task build roda um pipeline de preparacao de artefatos por pasta alvo.

No fluxo padrao, ele:

- Gera starters em .cache/starter a partir de src usando filtro por marcadores.
- Pode executar local.sh quando existir.
- Atualiza markdown com o preprocessador mdpp ao final do rebuild.

No fluxo moodle (opcional), ele tambem:

- Gera README rebaseado usando uma URL GitHub indicada explicitamente.
- Gera HTML do enunciado.
- Gera arquivo de testes.
- Mantem os starters filtrados por linguagem em `.cache/starter`.

## Comando e opcoes

Uso basico:

```bash
tko task build
```

Com alvos especificos:

```bash
tko task build labs/tres labs/media
```

Opcoes principais:

- -c, --check: so reconstrui quando detectar mudancas.
- -b, --brief: reduz logs.
- -m, --moodle URL: ativa pipeline de artefatos Moodle usando a URL raiz do repositório GitHub para rebasear links (README rebaseado, html, tests.vpl e starters).
- -e, --erase: apaga arquivos temporarios de saida (README.md, README.html, tests.vpl em .cache).

## Ordem real das etapas

Para cada alvo (diretorio):

1. Carrega titulo do README.
2. Garante pasta .cache.
3. Se precisar rebuild (ou sem --check), limpa .cache e segue:
4. Gera starters com DeepFilter de src para .cache/starter.
5. Executa local.sh (se existir).
6. Executa mdpp no README da origem.
7. Se --moodle URL:
   - rebase de links (README para .cache/README.md)
   - gera .cache/README.html
   - gera .cache/tests.vpl
8. Se --erase, remove alguns artefatos temporarios.

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
# pipeline padrao: drafts + local.sh + mdpp
tko task build .

# pipeline completo para moodle
tko task build . --moodle https://github.com/usuario/repositorio/tree/main

# so reconstruir se houver mudancas
tko task build . -c --moodle https://github.com/usuario/repositorio/tree/main
```

## Quando usar cada modo

- task build sem --moodle:
  - ciclo rapido de preparacao local.
  - atualizacao de markdown e drafts.

- task build com --moodle URL:
  - geracao de artefatos para publicacao/empacotamento (README rebaseado, html, tests.vpl e starters).

## Observacoes importantes

- Se nenhum alvo for informado, o comando usa o diretorio atual.
- Pastas iniciadas com ., _ e + sao ignoradas no pipeline.
- local.sh e opcional e executado no diretorio da tarefa.
- A URL passada para --moodle define os links remotos. O caminho da tarefa é calculado relativamente ao diretório em que o comando é executado.
