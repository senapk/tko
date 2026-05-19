# Gamificação e Progressão

Este guia centraliza como o TKO calcula progresso, XP, quests e desbloqueio de tarefas.

## Modelo mental

O repositorio de tarefas funciona como um banco de tarefas:

- Cada pasta de tarefa contem os dados da tarefa (README, testes, codigo base).
- O arquivo de indice (normalmente um README de trilha) funciona como indexador de metadados.

No indice, ha dois niveis:

- Quests: cabecalhos `##` ou `###`.
- Tasks: linhas markdown de tarefa (`- [ ]...`).

## Quests: como sao definidas

Uma quest e lida por cabecalho e pode incluir metadados no proprio titulo:

- `@chave`: chave da quest.
- `+skill` ou `+skill:valor`: skills aplicadas as tarefas da quest.
- `!@outra_quest`: dependencia para desbloqueio.
- `=linguagem`: filtro por linguagem.
- `%N`: percentual minimo para considerar a quest completa.

Exemplo:

```md
## Selecao 1 @if1 +if_else !@base %50
```

Comportamento no codigo:

- Parser de quest: [src/tko/game/quest_parser.py](../src/tko/game/quest_parser.py)
- Entidade quest: [src/tko/game/quest.py](../src/tko/game/quest.py)

## Tasks: como entram na gamificacao

Nas linhas de tarefa, o parser extrai:

- XP numerico (`:1`, `:2`, ...).
- Tipo de trilha (`main`, `perk`, `side`).
- Politica de perda (`free`, `part`, `zero`).
- Modo de avaliacao (`test`, `self`).

Regra importante:

- Chave com `@+` vira VIEW (consumo).
- Chave com `@` (sem `+`) fica como EDIT por padrao.

Comportamento no codigo:

- Parser de task: [src/tko/game/task_parser.py](../src/tko/game/task_parser.py)
- Config de task: [src/tko/game/task_config.py](../src/tko/game/task_config.py)
- Estado de jogo da task (xp/reachable): [src/tko/game/task_game.py](../src/tko/game/task_game.py)

## Como o TaskGrader calcula a nota

Cada tarefa tem duas partes:

1. Percentual de execucao (`rate`):
   - vem de testes automaticos ou autoavaliacao.
2. Percentual de qualidade:
   - aplica penalidade conforme `loss` e flags de ajuda (`guided`, `ia_code`, `ia_debug`, `ia_problem`).

Formula principal:

$$
\text{full\_percent} = \frac{\text{rate\_percent} \times \text{quality\_percent}}{100}
$$

E o ratio usado para XP da tarefa:

$$
\text{ratio} = \frac{\text{full\_percent}}{100}
$$

Completude da tarefa:

- `is_complete` quando `full_percent >= 70`.

Comportamento no codigo:

- Regras de penalidade e calculo: [src/tko/game/task_grader.py](../src/tko/game/task_grader.py)
- Dados de autoavaliacao: [src/tko/game/task_info.py](../src/tko/game/task_info.py)

## Como o progresso da quest e calculado

Cada task contribui com XP ponderado pelo desempenho:

$$
\text{xp\_earned\_task} = \text{xp\_task} \times \frac{\text{full\_percent}}{100}
$$

A quest soma XP obtido e total, e deriva percentuais.

Pontos importantes:

- `main` e `perk` entram no percentual principal.
- `side` entra como adicional.
- Quest completa depende de `min_percent_completion` (padrao 50%).

Comportamento no codigo:

- Calculo por quest: [src/tko/game/quest.py](../src/tko/game/quest.py)
- Funcoes de agregacao: [src/tko/game/quest_grader.py](../src/tko/game/quest_grader.py)
- Resume global de XP/skills: [src/tko/game/xp_resume.py](../src/tko/game/xp_resume.py)

## Desbloqueio de quests e inbox

Desbloqueio de quest:

- Uma quest so fica alcancavel se todas as `requires` estiverem completas e alcancaveis.

Comportamento no codigo:

- Atualizacao de alcance: [src/tko/game/game.py](../src/tko/game/game.py)

Inbox (visao reduzida de tarefas):

- Mostra quests alcancaveis e ainda nao finalizadas.
- Limita quantidade de tarefas por quest (maximo 10 no fluxo atual).
- Prioriza tarefas nao concluidas e tarefas ja baixadas.

Comportamento no codigo:

- Filtro de inbox e montagem da arvore: [src/tko/play_tree/tree_builder.py](../src/tko/play_tree/tree_builder.py)
- Estado do filtro de inbox: [src/tko/play_tree/tree_state.py](../src/tko/play_tree/tree_state.py)

## Papel do build index no banco de tarefas

Como o indice e o ponto de metadados, mantenha ele sincronizado com:

```bash
tko build index README.md base
```

Esse comando ajuda a:

- adicionar tarefas faltantes no indice;
- remover linhas com README local inexistente.

Guia detalhado:

- [Build index: manter e atualizar índices](build-index.md)

## Onde documentar cada coisa

- Regras de gamificação e progressão: este arquivo.
- Sintaxe de tags por linha de tarefa: [Marcadores-e-Tipos.md](Marcadores-e-Tipos.md).
- Operacao de autoria para professores: [Criando-Tarefas-e-Testes.md](Criando-Tarefas-e-Testes.md).
- Detalhes tecnicos de parser/engine: [Desenvolvimento-de-Tarefas.md](Desenvolvimento-de-Tarefas.md).
