<!-- markdownlint-configure-file {
  "MD033": false,
  "MD041": false
} -->

# TKO

Distribuição de tarefas de programação com Git, desenvolvimento direto na IDE do aluno e feedback contínuo para professores com métricas de progresso.

Plataforma para ensino prático de programação que conecta autoria de questões, execução local de testes e observabilidade pedagógica sem depender de LMS/hosting como Moodle.

[![Tests](https://github.com/senapk/tko/actions/workflows/tests.yml/badge.svg)](https://github.com/senapk/tko/actions/workflows/tests.yml)
[![PyPI version](https://img.shields.io/pypi/v/tko)](https://pypi.org/project/tko/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://pypi.org/project/tko/)
[![Downloads](https://static.pepy.tech/badge/tko/month)](https://pepy.tech/project/tko)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Repo](https://img.shields.io/badge/GitHub-senapk%2Ftko-181717?logo=github)](https://github.com/senapk/tko)
[![Stars](https://img.shields.io/github/stars/senapk/tko?style=social)](https://github.com/senapk/tko/stargazers)

O TKO é um ecossistema de ensino de programação centrado em prática, versionamento e evidências de aprendizagem. Ele distribui atividades via Git, permite desenvolvimento na IDE local e acompanha progresso de turmas com dados reais de evolução.

## Visão Geral

O TKO resolve o problema de acoplar ensino de programação a ambientes artificiais de navegador. Em vez disso, o aluno trabalha no próprio fluxo profissional: editor, terminal, compilador e controle de versão.

Para o professor, o sistema viabiliza distribuição de tarefas personalizadas e acompanhamento de execução com sinais de desenvolvimento, como tempo de resolução, histórico de versões e progresso por atividade.

Fluxo rápido:

1. Professor cria ou publica repositórios de questões.
2. Aluno baixa a atividade e desenvolve na própria IDE.
3. Aluno executa os testes localmente e itera com feedback imediato.
4. Aluno envia para o professor via Git, GitHub Classroom, Dropbox ou e-mail.
5. Professor acompanha evolução, métricas de aprendizado, tentativas e progresso da turma.

## Quick Start

### Linux / WSL

```bash
pipx install tko
tko --version
tko --help
```

Saída esperada:

- O comando `tko --version` deve mostrar a versão instalada.
- O comando `tko --help` deve listar os comandos principais (`task`, `build`, `class`, `remote`, ...).

Se `tko` não for encontrado após instalar com `pipx`, rode:

```bash
pipx ensurepath
```

Depois reabra o terminal.

### Windows

Use o guia recomendado para setup completo com VS Code e WSL:

- [Windows, VS Code e WSL - Recomendado](wiki/Windows-WSL.md)

## Casos de Uso

- Distribuição de listas e atividades de programação via Git.
- Desenvolvimento local na IDE do aluno, sem dependência de browser.
- Correção automática com testes e iteração rápida.
- Acompanhamento docente com indicadores de progresso e histórico.

## Documentação por Perfil

- Professor da disciplina (distribui e coleta via Git, GitHub Classroom (recomendado), Dropbox e e-mail):
  [Uso pelos professores](#uso-pelos-professores),
  [Criando tarefas e testes](wiki/Criando-Tarefas-e-Testes.md)
- Aluno da disciplina:
  [Uso do TKO pelos alunos](#uso-do-tko-pelos-alunos),
  [Fazendo as atividades](wiki/Fazendo-Atividades.md)
- Aluno em estudo autônomo (fora de disciplina):
  [Testando sem estar em uma disciplina](wiki/Testando-Sem-Disciplina.md),
  [Repositórios de referência](#repositórios-de-referência)
- Instalação e ambiente: [Instalação](#instalação)
- Desenvolvedores: [Uso pelos desenvolvedores](#uso-pelos-desenvolvedores)
- Ferramentas auxiliares: [Ferramentas](#ferramentas)

Repositórios de referência:

- [FUP - Fundamentos de Programação](https://github.com/qxcodefup/arcade)
- [ED - Estrutura de Dados](https://github.com/qxcodeed/arcade)
- [POO - Programação Orientada a Objetos](https://github.com/qxcodepoo/arcade)

## Instalação

- [Windows, VS Code e WSL - Recomendado](wiki/Windows-WSL.md)
- [Linux: VS Code](wiki/ubuntu_vscode.md)
- [WSL e Ubuntu: Setup básico com GIT, Python, TKO](wiki/ubuntu_git_python_tko.md)
- [Windows sem WSL](wiki/Windows-Sem-WSL.md)
- [Linguagens - Java, C, C++, Python, TypeScript, Go](wiki/Linguagens.md)
- [Outros sistemas operacionais](wiki/Outros-Sistemas-Operacionais.md)

## Uso do TKO pelos alunos

- [Testando sem estar em uma disciplina](wiki/Testando-Sem-Disciplina.md)
- [Como organizar seus repositórios da disciplina](wiki/Organizando-Disciplinas.md)
- [Fazendo as atividades](wiki/Fazendo-Atividades.md)

## Uso pelos professores

- [Trabalhando com o GitHub Classroom](wiki/Classroom.md)
- [Repositórios e quests](wiki/Criando-Atividades.md)
- [Marcadores e tipos de atividades](wiki/Marcadores-e-Tipos.md)
- [Criando tarefas e testes](wiki/Criando-Tarefas-e-Testes.md)
- [Gamificação e progressão](wiki/Gamificacao-e-Progressao.md)

## Uso pelos desenvolvedores

- [Desenvolvimento de tarefas no TKO](wiki/Desenvolvimento-de-Tarefas.md)
- [Gamificação e progressão](wiki/Gamificacao-e-Progressao.md)

## Ferramentas

- [Filtragem e Rascunhos](wiki/filter.md)
- [Markdown Preprocessor](wiki/mdpp.md)
- [Rebase de links markdown](wiki/rebase-links.md)
- [Build all: pipeline de mdpp, filter e drafts](wiki/build-all.md)
- [Build index: manter e atualizar índices](wiki/build-index.md)

## Referência e suporte

- [Guia de contribuição](CONTRIBUTING.md)
- [FAQ](docs/FAQ.md)
- [Referência rápida da CLI](docs/REFERENCE.md)
- [Especificação de formatos](docs/FORMATS.md)
- [Exemplos end-to-end](docs/EXAMPLES.md)
- [Ciclo de vida de tarefas](docs/TASK_LIFECYCLE.md)
- [Suporte a linguagens](docs/LANGUAGE_SUPPORT.md)
- [Guia de testes e QA](docs/TESTING.md)

## Atualizando o TKO

Para atualizar o TKO para a versão mais recente, basta executar o comando:

```bash
pipx upgrade tko          # windows, codespace, arch, ubuntu e wsl
```

## Contribuição

Contribuições são bem-vindas via pull request.

Fluxo mínimo para validar mudanças localmente:

```bash
uv run pytest -q
```

Se possível, mantenha mudanças pequenas, com descrição clara do problema e da solução no PR.

## Licença

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE).
