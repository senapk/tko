# Build task - pipeline de automacao de artefatos

Este guia documenta o que o comando abaixo faz na pratica:

```bash
tkm task build
```

## Visao geral

O comando tkm task build roda um pipeline de preparacao de artefatos por pasta alvo.

No fluxo padrao, ele:

- Gera starters em .cache/starter a partir de src usando filtro por marcadores.
- Pode executar local.sh quando existir.
- Atualiza markdown com o preprocessador mdpp ao final do rebuild.

No fluxo moodle (opcional), ele tambem:

- Gera um README autocontido com arquivos locais embutidos em Base64.
- Gera HTML do enunciado.
- Gera arquivo de testes.
- Mantem os starters filtrados por linguagem em `.cache/starter`.

## Comando e opcoes

Uso basico:

```bash
tkm task build
```

Com alvos especificos:

```bash
tkm task build labs/tres labs/media
```

Opcoes principais:

- -c, --check: so reconstrui quando detectar mudancas.
- -b, --brief: reduz logs.
- -m, --moodle: ativa o pipeline de artefatos Moodle (README com arquivos locais embutidos, HTML, tests.vpl e starters).
- -e, --erase: apaga arquivos temporarios de saida (README.md, README.html, tests.vpl em .cache).

## Ordem real das etapas

Para cada alvo (diretorio):

1. Carrega titulo do README.
2. Garante pasta .cache.
3. Se precisar rebuild (ou sem --check), limpa .cache e segue:
4. Gera starters com DeepFilter de src para .cache/starter.
5. Executa local.sh (se existir).
6. Executa mdpp no README da origem.
7. Se --moodle:
   - embute arquivos locais referenciados no README como URLs data: Base64
   - grava o README autocontido em .cache/README.md
   - gera .cache/README.html
   - gera .cache/tests.vpl
8. Se --erase, remove alguns artefatos temporarios.

## Artefatos gerados

No modo Moodle, os artefatos ficam dentro da pasta `.cache` da tarefa:

- `.cache/README.md`: cópia autocontida do README da tarefa. Referências locais a arquivos em Markdown e HTML são embutidas em Base64; links externos, âncoras e pastas permanecem como estão.
- `.cache/README.html`: HTML gerado a partir de `.cache/README.md`, usado como enunciado no Moodle.
- `.cache/tests.vpl`: arquivo de casos gerado a partir do `README.md` e dos arquivos `.tio`, `.vpl` e `.toml` encontrados na tarefa.
- `.cache/starter/<linguagem>/...`: starters filtrados a partir de `src/<linguagem>/...`, preservando a estrutura de arquivos por linguagem.

Esses três artefatos formam o pacote consumido pelo Mula:

```text
.cache/README.html
.cache/tests.vpl
.cache/starter/<linguagem>/
```

O Mula recebe a raiz do clone e o caminho relativo da tarefa. Quando algum
artefato necessário não existe, ele executa este build automaticamente sem
precisar de uma URL GitHub:

```bash
tkm task build labs/carro --moodle
```

O fluxo atual não depende de `.cache/mapi.json`. O caminho relativo da pasta,
como `labs/carro`, é a chave estável usada para publicar e atualizar a tarefa.

## Relacao com mdpp, filter e rascunhos

### mdpp

O build chama internamente o preprocessador markdown para atualizar o README.

Relaciona-se ao comando manual:

```bash
tkm tool mdpp README.md
```

### filter e drafts

O build usa DeepFilter sobre src e envia resultado para .cache/starter.

Relaciona-se ao comando manual:

```bash
tkm tool filter src -r -o .cache/starter
```

Observacao: no build, o filtro e chamado pelo pipeline interno, com indentacao configurada, focando geracao de drafts.

### rascunhos

Os rascunhos usados como starters ficam em .cache/starter durante a montagem de artefatos no modo moodle.

## Exemplo rapido (repositorio da disciplina)

Na raiz de uma tarefa:

```bash
# pipeline padrao: drafts + local.sh + mdpp
tkm task build .

# pipeline completo para moodle
tkm task build . --moodle

# so reconstruir se houver mudancas
tkm task build . -c --moodle
```

## Quando usar cada modo

- task build sem --moodle:
  - ciclo rapido de preparacao local.
  - atualizacao de markdown e drafts.

- task build com --moodle:
  - geracao de artefatos para publicacao/empacotamento (README autocontido, HTML, tests.vpl e starters).

## Observacoes importantes

- Se nenhum alvo for informado, o comando usa o diretorio atual.
- Pastas iniciadas com ., _ e + sao ignoradas no pipeline.
- local.sh e opcional e executado no diretorio da tarefa.
- Arquivos locais referenciados devem existir dentro da pasta da atividade; a falta de um arquivo impede gerar o HTML desse alvo e resulta em erro no comando.
- Arquivos locais referenciados são embutidos no README de cache. Arquivos maiores aumentam o tamanho de `.cache/README.md` e `.cache/README.html`.
