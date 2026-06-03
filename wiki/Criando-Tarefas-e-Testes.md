# Criando Tarefas e Testes

Este guia e para professores que organizam atividades de disciplina com TKO.

## Objetivo

Uma tarefa no TKO normalmente tem:

- Uma linha no indice (geralmente um `README.md` de trilha/quest).
- Uma pasta da tarefa (por exemplo `base/tres/`).
- Um `README.md` com enunciado.
- Um arquivo de testes (como `cases.tio`) ou testes em `toml`.

As tarefas tambem podem apontar para arquivos em repositorios remotos (por URL), nao apenas para arquivos locais.

## Reuso com repositorio remoto

Quando voce usa uma fonte remota (por exemplo um `README.md` hospedado no GitHub), o comando abaixo reescreve links relativos para links absolutos e prontos para reuso:

```bash
tko tool rebase-links @fup
```

Isso facilita reaproveitar trilhas e listas de tarefas ja publicadas em outro repositorio, sem quebrar links internos.

## Arquivos de solucao e rascunho

No fluxo de trabalho, arquivos de solucao costumam ficar em `src/lang/arquivo` (ou `src/lang/arquivos`, conforme organizacao da disciplina).

Com o comando de filtro, voce pode aplicar marcacoes no codigo e gerar versoes/drafts para alunos:

```bash
tko tool filter
```

Consulte tambem: [Filtragem e Rascunhos](tools/filter.md).

## Ferramenta de markdown

O TKO possui a ferramenta de preprocessamento markdown no comando:

```bash
tko tool mdpp
```

Ela oferece funcionalidades como:

- Geracao de TOC automaticamente.
- Inclusao de conteudo carregado por diretivas.
- Insercao de testes a partir de arquivo TOML (ex.: `tests.toml`) em blocos gerados.

Consulte: [Markdown Preprocessor](tools/mdpp.md).

## Formato da linha de tarefa

Exemplo:

```md
- [ ]`@tres xp:1 type:make`[Soma de tres inteiros](base/tres/README.md)
```

Partes:

- `@tres`: chave da tarefa.
- `xp:1`: XP da tarefa.
- `type:make`: tipo da tarefa (consumo ou producao).
- `[Soma de tres inteiros]`: texto do link.
- `(base/tres/README.md)`: link para o enunciado.


Regra importante da chave:

- A chave inicia com `@`.
- O tipo da atividade e indicado por `type=read` ou `type=make`.

Exemplo de tarefa de consumo:

```md
- [ ]`@video_intro xp:1 type=read`[Video de introducao](https://exemplo.com/video)
```

## Tipos e marcadores

Consulte a referencia completa em:

- [Marcadores e Tipos](game/tasks.md)

Resumo util:

- Politica de perda: `loss:free`, `loss:part`, `loss:zero`.
- Modo de avaliacao: `eval:test`, `eval:self`.

## Como criar uma nova tarefa (passo a passo)

1. Crie a pasta da tarefa, por exemplo `base/minha_tarefa/`.
2. Crie o enunciado em `base/minha_tarefa/README.md`.
3. Adicione testes em `tests.toml` se for uma tarefa com testes.
5. Rode localmente com TKO para validar enunciado e testes.

Exemplo de execucao local:

```bash
mkdir base/minha_tarefa
# adicionar elementos na pasta, como README.md e tests.toml
cd base/minha_tarefa
tko task run
```

## Como escrever testes

Voce pode usar:

- Bloco `toml` no `README.md` da tarefa.
- Arquivo `tests.toml` na pasta da tarefa.

Exemplo em `toml`:

```toml
[[tests]]
input = '1 2\n'
output = '3\n'

[[tests]]
input = '''
10
20
'''
output = '''
30
'''
```

## Trabalhando com `cases.tio` e pastas

Se preferir trabalhar com os testes em arquivos separados, voce pode descompactar um arquivo de testes `cases.tio` ou `tests.toml` para uma pasta com pares de entrada/saida.

Exemplo:

```bash
mkdir pasta
tko build pasta tests.toml
ls pasta
```

Serao gerados arquivos como `00.in`, `00.sol`, `01.in`, `01.sol`.

Para rodar a partir da pasta descompactada:

```bash
tko task run Solver.java pasta
```

## Convertendo entre formatos

Alguns fluxos comuns:

- Gerar `t.vpl` a partir de `testes.tio`:

```bash
tko build tests t.vpl testes.tio
```

- Gerar `t.tio` a partir de `README.md` e `extra.tio`:

```bash
tko build tests t.tio README.md extra.tio
```

- Extrair os testes para pasta (um arquivo de entrada e um de saida por caso):

```bash
mkdir pasta
tko build tests pasta cases.tio
```

## Padrao de nomes com `-p`

Voce pode definir o padrao de nome dos arquivos gerados com `-p`, usando `@` como wildcard para a numeracao.

Exemplo:

```bash
tko build tests pasta/ cases.tio -p "in.@ out.@"
```

Para formatos de maratona, voce pode adaptar para o padrao esperado:

- `-p "@.in @.out"`
- `-p "in@ out@"`
- outros padroes equivalentes

## Boas praticas para professores

- Use chaves curtas e consistentes (`@tres`, `@media`, `@bhaskara`).
- Evite mudar chave de tarefa depois de publicada.
- Mantenha enunciado claro com exemplo de entrada e saida.
- Crie testes cobrindo caso simples, borda e caso invalido (quando aplicavel).
- Use XP e trilha para progressao gradual da disciplina.

## Organizacao recomendada

- Um arquivo indice por modulo/trilha.
- Pastas de tarefa com mesmo padrao de nomes.
- Historico de mudancas no repositorio (git) antes de publicar turma.

## Checklist antes de publicar

- A linha da tarefa aponta para link valido.
- O enunciado abre corretamente no TKO.
- Os testes executam localmente.
- O nivel de dificuldade bate com XP e trilha.
- O titulo esta claro para os alunos.

## Guias relacionados

- [Gamificação e progressão](Gamificacao-e-Progressao.md)
- [Build all: pipeline de mdpp, filter e drafts](tools/build-all.md)
- [Build index: manter e atualizar índices](tools/build-index.md)
