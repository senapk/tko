# Referência rápida da CLI

Esta página resume os comandos mais usados do TKO para consulta rápida.

> Dica: para detalhes completos, use `tko --help` e `tko <comando> --help`.

## Comandos globais

```bash
tko --help
tko --version
```

Opções globais úteis:

- `-C, --changedir`: define diretório do repositório
- `-S, --settings`: define pasta de configurações
- `-w, --width`: largura de terminal
- `-m, --mono`: desativa cores
- `-D, --debug`: ativa debug
- `-G, --global-cache`: usa cache global para fontes remotas
- `-U, --update`: força atualização de fontes remotas
- `-O, --offline`: desativa tentativas de atualização

## task

Fluxo do aluno para listar/abrir/rodar tarefas.

```bash
tko task --help
```

Exemplos:

```bash
tko task list
tko task open <chave_da_tarefa>
tko task run
```

## build

Ferramentas de construção e conversão de artefatos.

```bash
tko build --help
```

Exemplos comuns:

```bash
tko build tests pasta cases.tio
tko build tests t.vpl testes.tio
tko build tests t.tio README.md extra.tio
```

## class

Fluxos de turma/disciplina.

```bash
tko class --help
```

## remote

Gerência de fontes remotas/repositórios.

```bash
tko remote --help
```

## config

Configuração do ambiente do TKO.

```bash
tko config --help
```

## reset

Operações de reset de estado/cache quando necessário.

```bash
tko reset --help
```

## collect

Fluxos de coleta de atividades/resultados.

```bash
tko collect --help
```

## tool

Ferramentas auxiliares de conteúdo e automação.

```bash
tko tool --help
```

Exemplos:

```bash
tko tool rebase-links @fup
tko tool filter
tko tool mdpp
```

## Diagnóstico rápido

Quando algo não funcionar:

1. Confirme versão e help:

```bash
tko --version
tko --help
```

2. Rode testes do projeto local:

```bash
uv run pytest -q
```

3. Consulte FAQ:

- `docs/FAQ.md`
