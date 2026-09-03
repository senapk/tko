# Desenvolvimento de Tarefas no TKO

Guia tecnico para quem estende parser, fluxo de carga e execucao de tarefas.

## Visao geral de arquitetura

Componentes principais no fluxo de tarefas:

- `TaskParser`: interpreta cada linha do indice e cria `Task`.
- `Task`: agrega metadados, configuracao, recurso e estado de jogo.
- `TaskLocation`: guarda origem do enunciado, tipo da atividade, linha do indice e informacoes de importacao remota.
- `TaskMatcher`: faz o parse da sintaxe markdown da linha.

Arquivos importantes:

- `src/tko/game/task_parser.py`
- `src/tko/game/task.py`
- `src/tko/game/task_location.py`

## Repositorio remoto e reuso de indices

Uma linha de tarefa deve apontar para um arquivo `README.md` local ou para uma
URL do GitHub que aponte para um `README.md`.

- Para URL GitHub, o parser extrai a estrutura do repositório e do caminho.
- Isso permite reutilizar listas de tarefas publicadas em outros repositorios.

Para preparar um indice remoto com links absolutos e reutilizaveis, use:

```bash
tko tool rebase @fup -o README.fup.md
```

O fluxo de `rebase` evita links relativos quebrados ao transportar um `README.md` entre repositorios.

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

## Modos de avaliação

No parser, tarefas são classificadas por `EvalMode`:

- `NONE`: leitura ou consulta de recurso externo/local.
- `SELF`: tarefa de produção com autoavaliação.
- `DIFF`: tarefa de produção com testes.

Regra de chave:

- A chave sempre inicia com `@`.
- O modo de avaliação é definido por `eval=none`, `eval=self` ou `eval=diff`.

Para links GitHub em tarefas:

- Se for URL GitHub reconhecida, o parser extrai `repository_url` e `relative_path`.
- Tarefas externas são materializadas no workspace do aluno.
- Tarefas locais continuam trabalhando diretamente na origem.
- Tarefas externas `eval=none` recebem README, assets e Markdown adicionais, sem testes ou drafts.
- Tarefas externas `eval=self` recebem drafts; `eval=diff` recebe drafts e testes.

## Regras de tags e defaults

`TaskMatcher` interpreta campos como:

- `@chave`: identificador da task.
- `gain=valor`: valor pedagogico.
- `cost=valor`: custo/dificuldade da tarefa.
- `size=valor`: tamanho ou extensao.
- `eval=none`, `eval=self` ou `eval=diff`: modo de avaliacao.

Defaults aplicados pelo parser:

- `gain=1`, `cost=1`, `size=1`.
- O modo `eval` é obrigatório.

Sintaxes antigas com `:read`, `:make`, `:test`, `:self`, `xp=`, `tier=`, `hard=` e `type=` não são aceitas.

## Como adicionar um novo marcador/tag

1. Defina a semantica no dominio (enum ou regra).
2. Atualize `TaskMatcher` para reconhecer o campo ou marcador.
3. Ajuste defaults se necessario no fluxo de parse.
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

- Preferir `loguru` em vez de `print` para erros
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

- [Gamificação e progressão](Gamificacao-e-Progressao.md)
- [Build all: pipeline de mdpp, filter e drafts](tools/build-all.md)
- [Build index: manter e atualizar índices](tools/build-index.md)
