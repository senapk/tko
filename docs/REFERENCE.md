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
tko --ui-language pt -C meu-repositorio task show
```

## Inicialização e execução

```bash
tko repo init --language py
tko repo init --skip-sources
tko repo init --profile URL_DO_PERFIL
tko repo source add course URL_DO_INDICE
tko open
tko run [ARQUIVOS_OU_DIRETORIOS...] --language py --side
```

`open` abre a interface do repositório; `run` executa testes no terminal e também
funciona com arquivos independentes, sem um repositório TKO.
`--all` mostra todas as falhas; `--none` oculta as falhas. Sem uma dessas opções,
`run` mostra a primeira. `--side` e `--down` escolhem o layout; sem ambas, usa a
preferência configurada.
`run --filter/-F` filtra os solvers temporariamente. `--index/-i` escolhe um teste.

## Atividades: task

```bash
tko repo list --all
tko repo list --downloaded
tko task show [PATH] --width 100 --height 12
tko task show [PATH] --graph-only
tko task open [PATHS...]
tko task down [CHAVE]
tko build task [DIRETORIOS...]
tko task check [DIRETORIOS...]
```

`show` e `open` recebem caminhos existentes. Um path pode apontar para um
arquivo ou diretório. `show` identifica a atividade que contém esse caminho.
Sem path, os comandos usam a atividade que contém a pasta atual, inclusive suas
subpastas. Fora de uma atividade, oferecem seleção numérica. `--fzf/-f` solicita
explicitamente seleção por fzf, mesmo dentro de uma atividade.
Não combine paths explícitos com `--fzf`.

`show` exige uma atividade materializada reconhecida no repositório; `open`
exige um repositório. `tko tests list` com caminhos explícitos também funciona
com arquivos independentes. Um path inválido retorna erro, sem ser interpretado
como chave. Cancelar a seleção é uma saída normal.

`repo list` lista as tarefas disponíveis nas fontes do repositório.
`down` recebe uma chave como `course@labs/fila` e oferece apenas atividades
externas ainda não baixadas. Sem chave, abre seleção numérica; aceita `--fzf/-f`.
O download prepara arquivos e rascunhos para execução.
Ao atualizar uma tarefa já materializada, substitui os Markdown, testes (`.toml` e
`.tio`) da raiz e a pasta `assets`; soluções e outras subpastas do aluno são
preservadas.

`task open --filter/-F` filtra solvers temporariamente. `run` e `task open`
herdam o modo de diff da configuração; `run` pode sobrescrevê-lo com `--side` ou
`--down`.

## Índices

```bash
tko build index README.md --from labs
tko build download README.md [CAMINHOS_DE_ATIVIDADES...]
tko build download --replace README.md [CAMINHOS_DE_ATIVIDADES...]
```

`tko build index` valida e atualiza o índice a partir das fontes locais.
`tko build download` copia atividades externas e reescreve seus links no índice.
Com `--replace`, também substitui diretórios já materializados, descartando
alterações locais.

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
tko config set --side --editor code --timeout 5
tko config reset settings
tko config reset cache
tko config reset languages
```

`settings` restaura preferências e aliases Git; `languages` recria o arquivo de
exemplo das linguagens; `cache` remove o cache Git global das fontes remotas.
Esses comandos não apagam os repositórios de trabalho.

## Relatórios e turmas

```bash
tko collect repo --resume
tko collect repo --history --game --json
tko collect repo --daily --width 100 --height 10
tko collect tasks aluno1 aluno2 --csv tasks.csv
tko collect skills aluno1 aluno2 --csv skills.csv --source course --language py
tko tool pull aluno1 aluno2 --threads 10
```

`collect repo` trabalha no repositório atual; `tasks` e `skills` produzem
relatórios CSV de vários repositórios. `tko tool pull` atualiza repositórios via Git em paralelo.
O gráfico de uma atividade está em `task show --graph-only`.

## Auditoria

```bash
tko repo audit on --interval 30
tko repo audit off
tko repo audit status
tko repo audit init --interval 30
tko tool timeline [PATHS...]
tko tool unpack ARQUIVO.jsonl
```

`tko repo audit on/off` configura a auditoria persistente. `tko repo audit init` executa um
monitor em primeiro plano até Ctrl+C. Apenas um coletor pode estar ativo por
workspace; uma segunda abertura não inicia outro watcher e uma segunda chamada
a `audit init` informa que a auditoria já está ativa.

## Ferramentas

```bash
tko tool mdpp README.md
tko tests convert README.md extra.tio -o tests.toml
tko tests convert pasta -o tests.toml --read-pattern "in.@ out.@"
tko tests convert tests.toml -o pasta/ --write-pattern "@.in @.sol"
tko tool diff "texto A" "texto B" --side
tko tool diff esperado.txt recebido.txt --input-type file --down
tko tool rebase README.md -o docs/README.md
tko tool filter solver.cpp
tko tool html README.md pagina.html
tko tool older arquivo-ou-diretorio
```

`tko tests convert` escreve TOML na saída padrão quando `--output/-o` é omitido.
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
