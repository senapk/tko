# Build all - pipeline de automacao de artefatos

Este guia documenta o que o comando abaixo faz na pratica:

```bash
tko build all
```

## Visao geral

O comando tko build all roda um pipeline de preparacao de artefatos por pasta alvo.

No fluxo padrao, ele:

- Atualiza markdown com o preprocessador mdpp.
- Gera drafts em .cache/drafts a partir de src usando filtro por marcadores.
- Pode executar local.sh quando existir.
- Atualiza markdown novamente (para refletir mudancas causadas pelo passo anterior).

No fluxo moodle (opcional), ele tambem:

- Gera README rebaseado para remoto/local.
- Gera HTML do enunciado.
- Gera arquivo de testes VPL.
- Monta mapi.json.

## Comando e opcoes

Uso basico:

```bash
tko build all
```

Com alvos especificos:

```bash
tko build all base/tres base/media
```

Opcoes principais:

- -c, --check: so reconstrui quando detectar mudancas.
- -b, --brief: reduz logs.
- -m, --moodle: ativa pipeline de artefatos Moodle (html, tests.vpl, mapi.json).
- -l, --local: nao usa configuracao remota para links absolutos.
- -e, --erase: apaga arquivos temporarios de saida (README.md, README.html, tests.vpl em .cache).

## Ordem real das etapas

Para cada alvo (diretorio):

1. Carrega titulo do README.
2. Garante pasta .cache.
3. Executa mdpp no README da origem.
4. Se precisar rebuild (ou sem --check), limpa .cache e segue:
5. Gera drafts com DeepFilter de src para .cache/drafts.
6. Executa local.sh (se existir).
7. Executa mdpp novamente.
8. Se --moodle:
   - rebase de links (README para .cache/README.md)
   - gera .cache/README.html
   - gera .cache/tests.vpl
   - monta .cache/mapi.json
9. Se --erase, remove alguns artefatos temporarios.

## Relacao com mdpp, filter e rascunhos

### mdpp

O build chama internamente o preprocessador markdown para atualizar o README.

Relaciona-se ao comando manual:

```bash
tko tool mdpp README.md
```

### filter e drafts

O build usa DeepFilter sobre src e envia resultado para .cache/drafts.

Relaciona-se ao comando manual:

```bash
tko tool filter src -r -o .cache/drafts
```

Observacao: no build, o filtro e chamado pelo pipeline interno, com indentacao configurada, focando geracao de drafts.

### rascunhos

Os rascunhos usados no mapeamento de tarefa sao carregados de .cache/drafts durante a montagem de artefatos no modo moodle.

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
  - geracao de artefatos para publicacao/empacotamento (html, tests.vpl, mapi.json).

## Observacoes importantes

- Se nenhum alvo for informado, o comando usa o diretorio atual.
- Pastas iniciadas com ., _ e + sao ignoradas no pipeline.
- local.sh e opcional e executado no diretorio da tarefa.
- O comportamento de links remotos depende de remote.toml quando aplicavel.
