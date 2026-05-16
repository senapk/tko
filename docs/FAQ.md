# FAQ do TKO

## 1) O comando `tko` não é encontrado após instalar

Sintoma:

- `command not found: tko`

Solução:

```bash
pipx ensurepath
```

Feche e abra o terminal novamente.

## 2) Qual comando uso para validar instalação?

```bash
tko --version
tko --help
```

Se `--help` listar comandos como `task`, `build`, `class`, `remote`, a instalação está ok.

## 3) Como rodar os testes do projeto TKO?

```bash
uv run pytest -q
```

## 4) Sou aluno fora de disciplina. Como começo?

Use o guia:

- `wiki/Testando-Sem-Disciplina.md`

E escolha um repositório oficial listado no README.

## 5) Sou professor. Como distribuo e coleto atividades?

Fluxo recomendado:

- Distribuir e coletar via Git/GitHub Classroom.
- Alternativas: Dropbox e e-mail.

Guias:

- `wiki/Classroom.md`
- `wiki/Criando-Atividades.md`
- `wiki/Criando-Tarefas-e-Testes.md`

## 6) Qual a diferença entre `cases.tio` e testes em pasta?

- `cases.tio`: formato compacto, comum no fluxo do TKO.
- Pasta: arquivos separados (`.in` e `.sol`) úteis para edição manual.

Conversões e exemplos:

- `wiki/Criando-Tarefas-e-Testes.md`

## 7) Como converter formatos de testes?

Exemplos:

```bash
tko build tests t.vpl testes.tio
tko build tests t.tio README.md extra.tio
tko build tests pasta cases.tio
```

Para padrões de nome personalizados, use `-p`.

## 8) Como adicionar suporte a linguagem no fluxo atual?

Use `languages.toml` quando o fluxo é build/run padrão.

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
