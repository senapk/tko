# Referência rápida da CLI

Use `tko --help` e `tko <grupo> <comando> --help` para consultar opções.

## Opções globais

As opções globais vêm antes do comando:

- `-C, --changedir PATH`: diretório efetivo para procurar repositórios e resolver caminhos relativos de qualquer comando.
- `-S, --settings PATH`: pasta de configurações, relativa ao diretório de invocação, antes de aplicar `-C`.
- `--ui-language pt|en`: idioma da interface, salvo na configuração global.
- `-w, --width N`: largura do terminal.
- `-m, --mono`: saída sem cores.
- `-D, --debug`: diagnóstico detalhado.
- `-U, --update`: força atualização das fontes remotas.
- `-O, --offline`: desativa tentativas de atualização.
- `-v, --version`: mostra a versão.

```bash
tko --ui-language pt -C meu-repositorio task list
```

## Inicialização e execução

```bash
tko repo init --language py
tko repo init --skip-sources
tko repo init --profile URL_DO_PERFIL
tko repo source add course URL_DO_INDICE
tko open
tko run [ARQUIVOS_OU_DIRETORIOS...] --language py --diff-mode side --failures first
```

`open` abre a interface do repositório; `run` executa testes no terminal e também
funciona com arquivos independentes, sem um repositório TKO.
`--failures first|all|none` controla as falhas exibidas; o padrão é `first`.
`run --filter/-F` filtra os solvers temporariamente. `--index/-i` escolhe um teste.

## Atividades: task

```bash
tko repo list --all
tko repo list --downloaded
tko task show [PATH] --width 100 --height 12
tko task show [PATH] --graph-only
tko task open [PATHS...] --diff-mode side
tko task list [PATHS...]
tko task down [CHAVE]
tkm task build [DIRETORIOS...]
tkm task check [DIRETORIOS...]
```

`show`, `open` e `list` recebem caminhos existentes. Um path pode apontar para
um arquivo ou diretório. `show` identifica a atividade que contém esse caminho;
`open` e `list` também aceitam vários arquivos ou diretórios.
Sem path, os comandos usam a atividade que contém a pasta atual, inclusive suas
subpastas. Fora de uma atividade, oferecem seleção numérica. `--fzf/-f` solicita
explicitamente seleção por fzf, mesmo dentro de uma atividade.
Não combine paths explícitos com `--fzf`.

`show` exige uma atividade materializada reconhecida no repositório; `open`
exige um repositório. `tkm tests list` com caminhos explícitos também funciona
com arquivos independentes. Um path inválido retorna erro, sem ser interpretado
como chave. Cancelar a seleção é uma saída normal.

`task list` mostra componentes e casos de teste da atividade. `repo list` lista
as tarefas disponíveis nas fontes do repositório.
`down` recebe uma chave como `course@labs/fila` e oferece apenas atividades
externas ainda não baixadas. Sem chave, abre seleção numérica; aceita `--fzf/-f`.
O download prepara arquivos e rascunhos para execução.
Ao atualizar uma tarefa já materializada, substitui os Markdown, testes (`.toml` e
`.tio`) da raiz e a pasta `assets`; soluções e outras subpastas do aluno são
preservadas.

`task open --filter/-F` filtra solvers temporariamente. `run` e `task open`
herdam o modo de diff da configuração, salvo quando `--diff-mode` é informado.

## Índices: index

```bash
tkm index build README.md --from labs
tkm index download README.md [CAMINHOS_DE_ATIVIDADES...]
tkm index update README.md [CAMINHOS_DE_ATIVIDADES...]
```

`build` valida e atualiza o índice. `download` copia atividades externas para
fontes locais e reescreve os links do índice. `update` substitui os diretórios
materializados pelo conteúdo da origem, removendo seu conteúdo anterior.

## Configuração e instalação: config

`tko config` gerencia somente preferências globais. `-C` seleciona o repositório
para comandos `repo`; `-S` seleciona a pasta global de configurações.

### Fontes e perfis

```bash
tko repo source list
tko repo source add python python/README.md --authoring
tko repo source set python --uri novo/README.md --authoring
tko repo source set python --authoring
tko repo source remove python
tko repo profile link URL_DO_PERFIL
tko repo profile status
tko repo profile update
tko repo profile unlink
```

`repo source set` exige `--uri`, `--authoring` ou ambos. As alterações são validadas
juntas antes de salvar. Fontes controladas por um perfil vinculado não podem
ser alteradas localmente. `repo profile unlink` mantém o perfil atual localmente.

### Preferências globais e cache

```bash
tko config list
tko config set --diff-mode side --editor code --timeout 5
tko config reset settings
tko config reset cache
tko config reset languages
```

`settings` restaura preferências e aliases Git; `languages` recria o arquivo de
exemplo das linguagens; `cache` remove o cache Git global das fontes remotas.
Esses comandos não apagam os repositórios de trabalho.

## Relatórios e turmas

```bash
tkm collect repo --resume
tkm collect repo --history --game --json
tkm collect repo --daily --width 100 --height 10
tkm collect tasks aluno1 aluno2 --csv tasks.csv
tkm collect skills aluno1 aluno2 --csv skills.csv --source course --language py
tkm tool pull aluno1 aluno2 --threads 10
```

`collect repo` trabalha no repositório atual; `tasks` e `skills` produzem
relatórios CSV de vários repositórios. `tkm tool pull` atualiza repositórios via Git em paralelo.
O gráfico de uma atividade está em `task show --graph-only`.

## Auditoria

```bash
tko repo audit on --interval 30
tko repo audit off
tko repo audit status
tkm audit init --interval 30
tkm audit preview [PATHS...]
tkm audit unpack ARQUIVO.jsonl
```

`tko repo audit on/off` configura a auditoria persistente. `tkm audit init` executa um
monitor em primeiro plano até Ctrl+C. Apenas um coletor pode estar ativo por
workspace; uma segunda abertura não inicia outro watcher e uma segunda chamada
a `audit init` informa que a auditoria já está ativa.

## Ferramentas

```bash
tkm tool mdpp README.md
tkm tests convert README.md extra.tio -o tests.toml
tkm tests convert pasta -o tests.toml --read-pattern "in.@ out.@"
tkm tests convert tests.toml -o pasta/ --write-pattern "@.in @.sol"
tkm tool diff "texto A" "texto B" --diff-mode side
tkm tool diff esperado.txt recebido.txt --input-type file --diff-mode down
tkm tool rebase README.md -o docs/README.md
tkm tool filter solver.cpp
tkm tool html README.md pagina.html
tkm tool older arquivo-ou-diretorio
```

`tkm tests convert` escreve TOML na saída padrão quando `--output/-o` é omitido.
`diff` interpreta os alvos como texto por padrão; use `--input-type file` para
arquivos. Seu modo de diff padrão é `down`. Arquivos inexistentes geram erro.
`rebase` exige destino explícito com `--output/-o`.

## Migração e instalação

```bash
tko repo migrate --dry-run
tko repo migrate
tko repo migrate /caminho/do/workspace
tko repo migrate --recover
tko update
tko uninstall
```

Sem path, `migrate` valida e usa o diretório atual, incluindo o definido por
`-C`. A migração é aplicada por padrão, sem criar cópias locais dos dados; o Git
pode restaurar o repositório em caso de erro. `--dry-run` apenas inspeciona;
`--map ARQUIVO.json` fornece correspondências explícitas; `--recover` existe
apenas para reverter migrações interrompidas por versões antigas e não pode ser
combinado com `--dry-run` ou `--map`.
Consulte [Migração dos dados de tarefas](TASK_DATA_MIGRATION.md).

Os nomes e opções substituídos foram removidos, sem aliases de compatibilidade.
