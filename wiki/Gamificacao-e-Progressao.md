# Gamificação e Progressão

Este guia centraliza como o TKO calcula progresso, XP, quests e desbloqueio de tarefas.

## Modelo mental

O repositorio de tarefas funciona como um banco de tarefas:

- Cada pasta de tarefa contem os dados da tarefa (README, testes, codigo base).
- O arquivo de indice (normalmente um README de trilha) funciona como indexador de metadados.

No indice, ha dois niveis:

- Quests: cabecalhos `##` ou `###`.
- Tasks: linhas markdown de tarefa (`- [ ]...`) ou (`- [x]...`).

## Quests: como sao definidas

Uma quest e lida por cabecalho e pode incluir metadados no proprio titulo:

- `key=@chave`: chave da quest.
- `tag=skill`: skill aplicada as tarefas da quest.
- `deps=@outra_quest`: dependencia para desbloqueio.
- `lang=linguagem`: filtro por linguagem.
- `xpgoal=N`: XP alvo para 100% de completude.
- `min=N%`: percentual minimo para considerar a quest completa.
- `active=true|false`: ativa ou desativa a quest.

Exemplo:

```md
## Selecao 1 key=@if1 tag=if_else deps=@base min=50%
```

O parser ainda aceita sintaxes legadas como `@if1`, `!@base`, `=python` e `%50`, mas a documentacao deve preferir os campos chave-valor.

Comportamento no codigo:

- Parser de quest: [src/tko/game/quest_parser.py](../src/tko/game/quest_parser.py)
- Entidade quest: [src/tko/game/quest.py](../src/tko/game/quest.py)

## Tasks: como entram na gamificacao

Nas linhas de tarefa, o parser extrai os três indicadores da atividade:

- Ganho (`gain=1`, compatível com `xp=`).
- Dificuldade (`hard=1`, compatível com `tier=`).
- Tamanho (`size=1`).
- Tipo (`type=make`, `type=read`) e modo de avaliação (`eval=test`, `eval=self`).

Comportamento no codigo:

- Parser de task: [src/tko/game/task_parser.py](../src/tko/game/task_parser.py)
- Config de task: [src/tko/game/task_config.py](../src/tko/game/task_config.py)
- Estado de jogo da task (xp/reachable): [src/tko/game/task_game.py](../src/tko/game/task_game.py)

## Como o TaskGrader calcula a nota

Cada tarefa tem duas partes:

1. Percentual de execucao (`rate`):
   - vem de testes automaticos ou autoavaliacao.
2. Percentual de qualidade:
   - aplica as regras de qualidade e flags de ajuda (`guided`, `ia_code`, `ia_debug`, `ia_problem`).

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

- Quest completa depende de `min` (padrao 50%).
- `xpgoal` pode ser definido manualmente ou gerado pelo `tko build index` a partir das tasks marcadas com `[x]` no indice.

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
tko build index README.md labs
```

Esse comando ajuda a:

- adicionar tarefas faltantes no indice;
- remover linhas com README local inexistente.
- atualizar e normalizar a sintaxe de tags e campos nas tarefas
- calcular `xpgoal` das quests somando o `gain` das tasks marcadas com `[x]`

Pastas novas dentro de `labs/` que contêm `README.md` entram automaticamente na quest correspondente,
com `gain=1 hard=1 size=1 type=make eval=test`. URLs HTTP/HTTPS são preservadas como referências
remotas e não são tratadas como arquivos locais quebrados.

Guia detalhado:

- [Build index: manter e atualizar índices](tools/build-index.md)

## Onde documentar cada coisa

- Regras de gamificação e progressão: este arquivo.
- Sintaxe de tags por linha de tarefa: [Marcadores-e-Tipos.md](game/tasks.md).
- Operacao de autoria para professores: [Guia para criar repositorios de tarefas](Criando-Atividades.md).
- Testes, conversoes e drafts: [Criando testes e conversoes](Criando-Tarefas-e-Testes.md).
- Detalhes tecnicos de parser/engine: [Desenvolvimento-de-Tarefas.md](Desenvolvimento-de-Tarefas.md).
