# FAQ do TKO

## 1) O comando `tko` não é encontrado após instalar

Sintoma:

- `command not found: tko`

Para a instalação gerenciada pelo TKO, adicione `~/.local/bin` ao PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Depois abra um novo terminal. Em instalações via `pipx`, use `pipx ensurepath`.

## 2) Como atualizo o TKO?

```bash
tko config self-update
```

Instalações via `pipx` continuam usando:

```bash
pipx upgrade tko
```

## 3) Qual comando uso para validar instalação?

```bash
tko --version
tko --help
```

Se `--help` listar comandos como `task`, `index`, `config` e `tool`, a instalação está ok.

## 4) Como rodar os testes do projeto TKO?

```bash
uv run pytest -q
```

## 5) Sou aluno fora de disciplina. Como começo?

Use o guia:

- `wiki/Testando-Sem-Disciplina.md`

E escolha um repositório oficial listado no README.

## 6) Sou professor. Como distribuo e coleto atividades?

Fluxo recomendado:

- Distribuir conteúdo por um repositório Git.
- Usar um repositório por aluno para entregas e histórico.
- O aluno pode criar o repositório e compartilhar com o professor.
- O professor pode criar repositórios em lote com scripts, como os do projeto `senapk/classroom`.

Guias:

- [Gestão de repositórios de turma](../wiki/Classroom.md)
- [Guia para criar repositórios de tarefas](../wiki/Criando-Atividades.md)
- [Criando testes e conversões](../wiki/Criando-Tarefas-e-Testes.md)

## 7) Qual a diferença entre `cases.tio` e testes em pasta?

- `tests.toml`: formato compacto, comum no fluxo do TKO.
- Pasta: arquivos separados (`.in` e `.sol`) úteis para edição manual.

Conversões e exemplos:

- [Criando testes e conversões](../wiki/Criando-Tarefas-e-Testes.md)

## 8) Como converter formatos de testes?

Exemplos:

```bash
tko tool convert-tests t.vpl -o tests.toml
tko tool convert-tests README.md extra.tio -o t.tio
tko tool convert-tests pasta -o tests.toml
```

Para padrões de nome personalizados, use `-p`.

## 9) Como adicionar suporte a linguagem no fluxo atual?

Use `programming-languages.toml` quando o fluxo é build/run padrão.

Guia:

- `wiki/Linguagens.md`

## 9) O que fazer quando um link da documentação quebra?

1. Abra issue usando o template de docs.
2. Informe arquivo e trecho afetado.
3. Se puder, proponha o link correto.

Template:

- `.github/ISSUE_TEMPLATE/documentation_bug.yml`

## 10) A documentação está desatualizada. Como contribuir?

1. Abra PR com correção objetiva.
2. Preencha checklist de docs no template de PR.
3. Garanta que links e comandos foram revisados.

Referências:

- `CONTRIBUTING.md`
- `.github/pull_request_template.md`
