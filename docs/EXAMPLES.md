# Exemplos end-to-end

Este guia mostra fluxos completos e curtos para começar com TKO.

## Exemplo 1 - Aluno em disciplina

Objetivo: conectar repositório do professor e abrir tarefas.

```bash
tko init
tko remote add poo https://github.com/exemplo/disciplina-poo
tko open
```

Resultado esperado:

1. TKO cria estrutura local.
2. TKO registra remoto com alias `poo`.
3. Ao abrir, tarefas da disciplina ficam visíveis.

## Exemplo 2 - Professor criando tarefa nova

Objetivo: criar tarefa local e publicar para alunos.

Passos:

1. Criar pasta da tarefa e README com enunciado.
2. Adicionar casos de teste (`tests.toml` ou pasta).
3. Se tiver rascunhos a serem gerados para essa tarefa, ou links a serem atualizados, rodar `tko build all` na pasta da tarefa. 
4. Atualizar README de índice da trilha rodando no root do projeto `tko build index README.md <pasta>`.
5. Commit e push no repositório da disciplina.

Após publicação:

- alunos verão novas atividades na próxima janela de atualização do cache remoto.

## Exemplo 3 - Reuso de atividade remota

Objetivo: incluir atividade já existente em outro repositório.

Passos:

1. No README da trilha, adicione link completo para tarefa remota.
2. Commit e push da trilha.
3. Alunos sincronizam e passam a enxergar a atividade.

Observação:

- esse fluxo acelera montagem de disciplina com material comunitário/oficial.

## Exemplo 4 - Converter casos de teste

Objetivo: alternar entre formato compacto e pasta.

```bash
# extrair para pasta
tko build tests pasta tests.toml

# converter para vpl
tko build tests t.vpl tests.toml

# gerar t.tio a partir de README + extra
tko build tests t.tio README.md extra.tio
```

## Exemplo 5 - Rodar testes de desenvolvimento do projeto

Objetivo: validar mudanças antes de PR.

```bash
uv sync
uv run pytest -q
```

## Referências relacionadas

- [docs/TASK_LIFECYCLE.md](../docs/TASK_LIFECYCLE.md)
- [docs/REFERENCE.md](../docs/REFERENCE.md)
- [docs/FORMATS.md](../docs/FORMATS.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
