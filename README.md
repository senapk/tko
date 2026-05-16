<!-- markdownlint-configure-file {
  "MD033": false,
  "MD041": false
} -->

# TKO

[![Tests](https://github.com/senapk/tko/actions/workflows/tests.yml/badge.svg)](https://github.com/senapk/tko/actions/workflows/tests.yml)
[![PyPI version](https://img.shields.io/pypi/v/tko)](https://pypi.org/project/tko/)
[![Python](https://img.shields.io/pypi/pyversions/tko)](https://pypi.org/project/tko/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/tko)](https://pypi.org/project/tko/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Repo](https://img.shields.io/badge/GitHub-senapk%2Ftko-181717?logo=github)](https://github.com/senapk/tko)
[![Stars](https://img.shields.io/github/stars/senapk/tko?style=social)](https://github.com/senapk/tko/stargazers)

O tko é um sistema de testes para programação competitiva. Ele é capaz de rodar testes em várias linguagens de programação e em vários formatos de testes. Ele está integrado com os repositórios de atividades das disciplinas de programação da UFC de Quixadá permitindo baixar as atividades e rodar os testes.

- [FUP - Fundamentos de Programação](https://github.com/qxcodefup/arcade)
- [ED - Estrutura de Dados](https://github.com/qxcodeed/arcade)
- [POO - Programação Orientada a Objetos](https://github.com/qxcodepoo/arcade)

## Instalação

- [Windows, Vscode e WSL- Recomendado](wiki/Windows-WSL.md)
- [Linux: Vscode](wiki/ubuntu_vscode.md)
- [WSL e Ubuntu: Setup básico com GIT, Python, TKO](wiki/ubuntu_git_python_tko.md)
- [Windows SEM WSL](wiki/Windows-Sem-WSL.md)
- [Linguagens - Java, C, C++, Python, Typescript, Go](wiki/Linguagens.md)
- [Outros sistemas operacionais](wiki/Outros-Sistemas-Operacionais.md)

## Uso do TKO pelos alunos

- [Testando sem estar em uma disciplina](wiki/Testando-Sem-Disciplina.md)
- [Como organizar seus repositórios da disciplina](wiki/Organizando-Disciplinas.md)
- [Fazendo as atividades](wiki/Fazendo-Atividades.md)

## Uso pelos professores

- [Trabalhando com o Classroom](wiki/Classroom.md)
- [Repositórios e quests](wiki/Criando-Atividades.md)
- [Marcadores e tipos de atividades](wiki/Marcadores-e-Tipos.md)
- [Criando tarefas e testes](wiki/Criando-Tarefas-e-Testes.md)
- [Gamificacao e progressao](wiki/Gamificacao-e-Progressao.md)

## Uso pelos desenvolvedores

- [Desenvolvimento de tarefas no TKO](wiki/Desenvolvimento-de-Tarefas.md)
- [Gamificacao e progressao](wiki/Gamificacao-e-Progressao.md)

## Ferramentas 

- [Filtragem e Rascunhos](wiki/filter.md)
- [Markdown Preprocessor](wiki/mdpp.md)
- [Rebase de links markdown](wiki/rebase-links.md)
- [Build all: pipeline de mdpp, filter e drafts](wiki/build-all.md)
- [Build index: manter e atualizar indices](wiki/build-index.md)

## Atualizando o tko

Para atualizar o tko para versão mais recente, basta executar o comando:

```bash
pipx upgrade tko          # windows, codespace, arch, ubuntu e wsl
```

## Criando os testes

### Descompactando os testes

Se preferir trabalhar com o modelo de testes em arquivos separados, você pode descompactar o arquivo `cases.tio` para uma pasta com os arquivos de entrada e saída. Será gerado um arquivo `.in` e um `.sol` para cada teste.

```bash
$ mkdir pasta
$ tko build pasta cases.tio
$ ls pasta
00.in 00.sol 01.in 01.sol 02.in 02.sol 03.in 03.sol 04.in 04.sol
```

Para rodar a partir da pasta com os testes descompactados, basta passar o nome da pasta como parâmetro.

```bash
tko task run Solver.java pasta
```

Se quiser utilizar um nome padrão diferente para leitura ou escrita das pastas, veja a seção de [Convertendo entre formatos](#convertendo-entre-formatos).

## Convertendo entre formatos

- Gerando um `t.vpl`
  - `tko build tests t.vpl testes.tio`
- Gerando um `t.tio` a partir do `README.md`e de um `extra.tio`.
  - `tko build tests t.tio README.md extra.tio`
- Para extrair os testes para uma pasta com um arquivo para entrada e outro para saída, crie uma pasta vazia e passe para o primeiro parâmetro do `tko build`.

```bash
$ ls
cases.tio  draft.c  README.md
$ mkdir pasta
$ tko build tests pasta cases.tio 
$ ls pasta/
00.in   02.sol  05.in   07.sol  10.in   12.sol  15.in   17.sol  20.in   22.sol
00.sol  03.in   05.sol  08.in   10.sol  13.in   15.sol  18.in   20.sol  23.in
01.in   03.sol  06.in   08.sol  11.in   13.sol  16.in   18.sol  21.in   23.sol
01.sol  04.in   06.sol  09.in   11.sol  14.in   16.sol  19.in   21.sol
02.in   04.sol  07.in   09.sol  12.in   14.sol  17.in   19.sol  22.in
```

- Você pode definir o padrão de nome dos arquivos gerados com `-p "@ @"`, sendo @ o wildcard que representa a numeração dos arquivo.
  - Vamos refazer o comando acima, mas colocando "-p in.@ out.@"

```bash
$ tko build tests pasta/ cases.tio -p "in.@ out.@"
$ ls pasta/
in.00  in.05  in.10  in.15  in.20   out.01  out.06  out.11  out.16  out.21
in.01  in.06  in.11  in.16  in.21   out.02  out.07  out.12  out.17  out.22
in.02  in.07  in.12  in.17  in.22   out.03  out.08  out.13  out.18  out.23
in.03  in.08  in.13  in.18  in.23   out.04  out.09  out.14  out.19
in.04  in.09  in.14  in.19  out.00  out.05  out.10  out.15  out.20
```

- O `pattern` é útil para converter os formatos de Maratona, que vem em múltiplos arquivos para o `.tio`. Basta fazer o `match` do modelo que eles utilizarem.
  - `-p "@.in @.out"`
  - `-p "in@ out@"`
  - entre outros.
