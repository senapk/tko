# Desenvolvimento de Tarefas no TKO

Guia tecnico para quem estende parser, fluxo de carga e execucao de tarefas.

## Visao geral de arquitetura

Componentes principais no fluxo de tarefas:

- `TaskParser`: interpreta cada linha do indice e cria `Task`.
- `Task`: agrega metadados, configuracao, recurso e estado de jogo.
- `TaskResource`: guarda origem do enunciado (local/remoto/url) e caminho relativo.
- `TaskMatcher`: faz o parse da sintaxe markdown da linha.

Arquivos importantes:

- `src/tko/game/task_parser.py`
- `src/tko/game/task.py`

## Repositorio remoto e reuso de indices

Uma linha de tarefa pode apontar para arquivo local ou URL remota.

- Para URL remota, o parser tenta extrair estrutura GitHub quando aplicavel.
- Isso permite reutilizar listas de tarefas publicadas em outros repositorios.

Para preparar um indice remoto com links absolutos e reutilizaveis, use:

```bash
tko tool rebase-links @fup
```

O fluxo de `rebase-links` evita links relativos quebrados ao transportar um `README.md` entre repositorios.

## Solucoes, drafts e ferramentas auxiliares

Organizacao comum de solucoes:

- `src/lang/arquivo` (ou `src/lang/arquivos`, conforme convencao adotada na disciplina).

Com marcacoes de corte no codigo, o comando abaixo permite gerar versoes de material/rascunho:

```bash
tko tool filter
```

Para preprocessamento de markdown, o comando implementado atualmente e:

```bash
tko tool mdpp
```

Capacidades relevantes para autoria de tarefas:

- Geracao de TOC.
- Carga/transformacao de blocos via diretivas markdown.
- Insercao de testes a partir de TOML (como `tests.toml`) em blocos renderizados.

## Tipos de recurso

No parser, tarefas podem cair em:

- `VIEW`: visualizacao (link externo ou leitura).
- `EDIT`: tarefa editavel com fonte local/remota.

Regra de chave:

- Quando a chave inicia com `@+`, a tarefa e tratada como `VIEW` (consumo).
- Quando a chave inicia com `@` (sem `+`), a tarefa segue como `EDIT` por padrao.

Para links HTTP em tarefas de edicao:

- Se for URL GitHub reconhecida, o parser extrai `repository_url` e `relative_path`.
- Se nao reconhecer, converte para `VIEW` e usa `external_url`.

## Regras de tags e defaults

`TaskParser.decode_task_types()` interpreta tags como:

- XP numerico (`:1`, `:2`, ...)
- Trilha (`main`, `side`, `perk`)
- Perda (`free`, `part`, `zero`)
- Tipo de teste (`test`, `self`)

Defaults aplicados em `__parse_task_types()`:

- Para `VIEW`: `loss=FREE`, `test=SELF`.
- Para `EDIT`: `loss=PART`, `test=TEST`.

## Como adicionar um novo marcador/tag

1. Defina a semantica no dominio (enum ou regra).
2. Atualize `TaskParser.decode_task_types()`.
3. Ajuste defaults se necessario em `__parse_task_types()`.
4. Escreva testes unitarios cobrindo:
   - parse valido
   - fallback/default
   - comportamento para tag desconhecida

## Estrategia de testes recomendada

Cobrir 3 niveis:

- Unitario do parser (`tests/game/test_task_parser.py`).
- Integracao de carga de repositorio (`tests/repository/...`).
- Fluxo CLI quando houver comando novo (`tests/cli/...`).

Casos minimos para parser:

- Link local relativo.
- URL externa de view.
- URL GitHub de edit.
- Tag desconhecida (espera warning).
- Linha invalida (retorna `None`).

## Convenções

- Preferir `logging` em vez de `print`.
- Usar `Path` para caminhos.
- Manter comportamento backward-compatible da sintaxe de tarefa.
- Evitar efeitos colaterais no parser (apenas interpretar e preencher `Task`).

## Checklist para PR de tarefas/parser

- Testes novos para cenarios alterados.
- Sem regressao no parse de markdown antigo.
- Logs em nivel apropriado (`info`/`warning`).
- Mensagens de erro objetivas para usuario final.
- Suite completa de testes passando.

## Guias relacionados

- [Gamificacao e progressao](Gamificacao-e-Progressao.md)
- [Build all: pipeline de mdpp, filter e drafts](build-all.md)
- [Build index: manter e atualizar indices](build-index.md)
