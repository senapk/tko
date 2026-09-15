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
tko init --language py
tko init --skip-sources
tko init --profile URL_DO_PERFIL
tko config source add course URL_DO_INDICE
tko open
tko open --audit
tko run [ARQUIVOS_OU_DIRETORIOS...] --language py --diff-mode side --failures first
```

`open` abre a interface do repositório; `run` executa testes no terminal e também
funciona com arquivos independentes, sem um repositório TKO.
`--failures first|all|none` controla as falhas exibidas; o padrão é `first`.
`run --filter/-F` filtra os solvers temporariamente. `--index/-i` escolhe um teste.

## Atividades: task

```bash
tko task list --all
tko task list --downloaded
tko task show [PATH] --width 100 --height 12
tko task show [PATH] --graph-only
tko task open [PATHS...] --diff-mode side
tko task tests [PATHS...]
tko task download [CHAVE]
tko task build [DIRETORIOS...]
```

`show`, `open` e `tests` recebem caminhos existentes. Um path pode apontar para
um arquivo ou diretório. `show` identifica a atividade que contém esse caminho;
`open` e `tests` também aceitam vários arquivos ou diretórios.
Sem path, os comandos usam a atividade que contém a pasta atual, inclusive suas
subpastas. Fora de uma atividade, oferecem seleção numérica. `--fzf/-f` solicita
explicitamente seleção por fzf, mesmo dentro de uma atividade.
Não combine paths explícitos com `--fzf`.

`show` exige uma atividade materializada reconhecida no repositório; `open`
exige um repositório. `tests` com caminhos explícitos também funciona com
arquivos independentes. Um path inválido retorna erro, sem ser interpretado
como chave. Cancelar a seleção é uma saída normal.

`download` recebe uma chave como `course@labs/fila` e oferece apenas atividades
externas ainda não baixadas. Sem chave, abre seleção numérica; aceita `--fzf/-f`.
O download prepara arquivos e rascunhos para execução.

`task open --filter/-F` filtra solvers temporariamente. `run` e `task open`
herdam o modo de diff da configuração, salvo quando `--diff-mode` é informado.

## Índices: index

```bash
tko index build README.md --from labs
tko index download README.md [CAMINHOS_DE_ATIVIDADES...]
tko index update README.md [CAMINHOS_DE_ATIVIDADES...]
```

`build` valida e atualiza o índice. `download` copia atividades externas para
fontes locais e reescreve os links do índice. `update` substitui os diretórios
materializados pelo conteúdo da origem, removendo seu conteúdo anterior.

## Configuração e instalação: config

`config` reúne preferências globais, configuração de fontes e perfis do
repositório, manutenção da instalação e limpeza de cache. `-C` seleciona o
repositório para `config source/profile`; `-S` seleciona a pasta de configuração
global para `config set/list/reset`.

### Fontes e perfis

```bash
tko config source list
tko config source add python python/README.md --authoring
tko config source set python --uri novo/README.md --authoring
tko config source set python --authoring
tko config source remove python
tko config profile link URL_DO_PERFIL
tko config profile status
tko config profile update
tko config profile unlink
```

`config source set` exige `--uri`, `--authoring` ou ambos. As alterações são validadas
juntas antes de salvar. Fontes controladas por um perfil vinculado não podem
ser alteradas localmente. `config profile unlink` mantém o perfil atual localmente.

### Preferências globais e cache

```bash
tko config list
tko config set --diff-mode side --editor code --timeout 5
tko config reset
tko config clear-cache
```

`config reset` restaura a configuração global. `config clear-cache` remove o cache
Git global das fontes remotas. Não apaga os repositórios de trabalho.

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
relatórios CSV de vários repositórios. `tool pull` atualiza repositórios via Git em paralelo.
O gráfico de uma atividade está em `task show --graph-only`.

## Auditoria

```bash
tko audit on --interval 30
tko audit off
tko audit start --interval 30
tko audit preview [PATHS...]
tko audit unpack ARQUIVO.jsonl
```

`on/off` configuram auditoria persistente. `start` executa um monitor em primeiro
plano até Ctrl+C. `open --audit` ativa auditoria para aquela sessão.

## Ferramentas

```bash
tko tool mdpp README.md
tko tool convert-tests README.md extra.tio -o tests.toml
tko tool convert-tests pasta -o tests.toml --read-pattern "in.@ out.@"
tko tool convert-tests tests.toml -o pasta/ --write-pattern "@.in @.sol"
tko tool diff "texto A" "texto B" --diff-mode side
tko tool diff esperado.txt recebido.txt --input-type file --diff-mode down
tko tool rebase README.md -o docs/README.md
tko tool filter solver.cpp
tko tool html README.md pagina.html
tko tool older arquivo-ou-diretorio
```

`convert-tests` escreve TOML na saída padrão quando `--output/-o` é omitido.
`diff` interpreta os alvos como texto por padrão; use `--input-type file` para
arquivos. Seu modo de diff padrão é `down`. Arquivos inexistentes geram erro.
`rebase` exige destino explícito com `--output/-o`.

## Migração e instalação

```bash
tko tool migrate --dry-run
tko tool migrate
tko tool migrate /caminho/do/workspace
tko tool migrate --recover
tko config self-update
tko config uninstall
```

Sem path, `migrate` valida e usa o diretório atual, incluindo o definido por
`-C`. A migração é aplicada por padrão, com backup. `--dry-run` apenas inspeciona;
`--map ARQUIVO.json` fornece correspondências explícitas; `--recover` reverte
uma migração interrompida e não pode ser combinado com `--dry-run` ou `--map`.
Consulte [Migração dos dados de tarefas](TASK_DATA_MIGRATION.md).

Os nomes e opções substituídos foram removidos, sem aliases de compatibilidade.
