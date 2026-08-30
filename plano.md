Updated todo list

Vou transformar isso em um plano executável por etapas, com foco em reduzir risco, criar testes de domínio e separar infraestrutura antes de mexer em regras complexas.

## Plano de refatoração para tornar o TKO testável e sustentável

A ideia não é “refatorar tudo de uma vez”. O objetivo é criar limites claros entre domínio, aplicação, infraestrutura e interface, de modo que a suíte de testes passe a cobrir comportamento real e não o ambiente do terminal.

A ordem abaixo foi pensada para minimizar risco e permitir que você e o Copilot/Codex avancem etapa por etapa, validando cada mudança.

### Status da execução da etapa zero

- Base atual verificada: parcialmente bloqueada pelo ambiente.
- Evidência: o projeto possui uma pasta `.venv`, mas ela não tem `pip` nem `pytest` instalados; `python -m pytest` falha com `No module named pytest`.
- Conclusão: a suíte não pode ser usada como linha de base ainda, porque o ambiente de desenvolvimento do projeto não foi preparado.
- Próximo passo necessário: preparar o ambiente virtual com as dependências de desenvolvimento antes de continuar para a próxima fase.

### Módulos de maior risco e acoplamento detectados

- [src/tko/__main__.py](src/tko/__main__.py): bootstrap da CLI, estado global e configuração.
- [src/tko/run/run_context.py](src/tko/run/run_context.py): mistura de configuração, ambiente, repo, task e UI.
- [src/tko/run/run_executor.py](src/tko/run/run_executor.py): execução, apresentação e persistência em um mesmo objeto.
- [src/tko/repository/repository.py](src/tko/repository/repository.py): agregador de repo, cache, logger e regras de workspace.
- [src/tko/feno/build.py](src/tko/feno/build.py): manipulação de diretório atual, subprocessos e console.
- [src/tko/cli/cli_main.py](src/tko/cli/cli_main.py): uso de `os.chdir` em fluxo de CLI.
- [src/tko/run/filter_mode_service.py](src/tko/run/filter_mode_service.py): mudança de diretório no ambiente de execução.

---

## Fase 0 — Baseline e congelamento do comportamento

### Objetivo
Estabelecer uma linha de base antes de mexer em arquitetura.

### O que analisar
- `__main__.py`
- `run_context.py`
- `run_executor.py`
- `repository.py`
- `build.py`

### Tarefas
1. Listar os módulos que:
   - usam `os.chdir`
   - usam `subprocess.run`
   - usam `Console.print`
   - manipulam `Path` do ambiente global
   - têm muitos setters fluentes
2. Identificar quais partes são “domínio” e quais são “infraestrutura”.
3. Registrar em um documento de planejamento as classes/modos que serão extraídos.

### Verificação
- Rodar a suíte atual:
  - `pytest -q`
- Considerar que a base atual é “verde” antes da refatoração.
- Se houver falhas existentes, documentar e não tentar corrigi-las junto com a arquitetura.

### Critério de conclusão
- Você tem um mapa dos módulos mais acoplados e uma referência de linha de base.

---

## Fase 1 — Mapa de responsabilidades e fronteiras

### Objetivo
Separar classes por responsabilidade sem mudar comportamento.

“Emita uma checklist de refatoração para fase 1 com foco em separar domínio e infraestrutura em run_context.py, run_executor.py e repository.py.”
“Crie um resumo das responsabilidades de __main__.py, cli_main.py e build.py.”

### Análise executada até o momento

#### 1) Domínio puro (candidatos a testes sem terminal)
- Parsing de metadata de tasks/quests e regras de estrutura.
- Estado de execução e cálculo de progresso.
- Decisão de sucesso/falha por caso de teste.
- Regras de relógio, ordenação, dependência e completude.
- Tipos de resultado e objetos de dados para execução.

#### 2) Aplicação (orquestração)
- Montagem de contexto a partir de repo, settings e argumentos.
- Casos de uso de execução, build e carregamento do workspace.
- Serviços que coordenam domínio + infraestrutura sem conhecer terminal diretamente.

#### 3) Infraestrutura (I/O, shell, filesystem, git, logger)
- subprocessos e execuções externas.
- manipulação de diretório atual.
- acesso ao sistema de arquivos, cache e logs.
- git/cache e watchers.
- terminal e console output.

#### 4) Interface (CLI e apresentação)
- Typer commands e argumentos.
- impressão em terminal e interação com o usuário.
- conversão de resultados para texto.

### Mapeamento concreto dos módulos críticos

| Módulo | Observação | Camada provável |
|---|---|---|
| [src/tko/run/run_context.py](src/tko/run/run_context.py) | Guarda config, repo, task, opener, UI flags e estado de execução | mistura de domínio + aplicação + interface |
| [src/tko/run/run_executor.py](src/tko/run/run_executor.py) | calcula taxa, apresenta texto, salva log e executa fluxo | aplicação + interface + infraestrutura |
| [src/tko/repository/repository.py](src/tko/repository/repository.py) | agrega estado do workspace, cache, repo, logger e task resolver | aplicação + infraestrutura |
| [src/tko/feno/build.py](src/tko/feno/build.py) | muda diretório atual, roda shell, manipula cache e console | infraestrutura + interface |
| [src/tko/__main__.py](src/tko/__main__.py) | monta o app e configura globals do ambiente | interface + bootstrap |
| [src/tko/cli/cli_main.py](src/tko/cli/cli_main.py) | orquestra CLI, faz chdir e delega execução | interface |
| [src/tko/run/filter_mode_service.py](src/tko/run/filter_mode_service.py) | usa diretório global e console | infraestrutura + interface |
| [src/tko/logger/audit_tracker.py](src/tko/logger/audit_tracker.py) | grava snapshots, valida arquivos e usa lock | infraestrutura |

### Checklist para a execução da fase 1

#### Tarefa 1 — Separar domínio de interface
- [ ] Identificar objetos que representam resultado de execução e progresso.
- [ ] Mover regras de cálculo para classes puras sem Console, Path global ou subprocessos.
- [ ] Garantir que qualquer saída para terminal fique fora do domínio.

#### Tarefa 2 — Separar aplicação de infraestrutura
- [ ] Definir serviços de aplicação que orquestram o fluxo.
- [ ] Injetar dependências de sistema operacional e repositório em vez de usar estado global.
- [ ] Garantir que a aplicação receba dados e retorne objetos prontos para apresentação.

#### Tarefa 3 — reduzir acoplamento de I/O
- [ ] Isolar os pontos de shell, git, filesystem e console em adapters.
- [ ] Remover chamadas diretas a os.chdir da lógica de negócio.
- [ ] Trocar chamadas globais por dependências explícitas.

#### Tarefa 4 — classificar módulos por prioridade
- [ ] Prioridade 1: [src/tko/run/run_context.py](src/tko/run/run_context.py), [src/tko/run/run_executor.py](src/tko/run/run_executor.py)
- [ ] Prioridade 2: [src/tko/repository/repository.py](src/tko/repository/repository.py), [src/tko/feno/build.py](src/tko/feno/build.py)
- [ ] Prioridade 3: [src/tko/__main__.py](src/tko/__main__.py), [src/tko/cli/cli_main.py](src/tko/cli/cli_main.py)

### Entregáveis esperados da fase 1
- Um documento de arquitetura interna com as fronteiras entre as camadas.
- Lista de classes a migrar para domínio puro.
- Lista de adapters a criar para console, filesystem e subprocessos.
- Critério claro de quando um módulo “está pronto” para a próxima fase.

### Verificação
- Revisar se cada módulo fica em apenas uma categoria.
- Se uma classe mistura regra + terminal + filesystem, ela deve entrar na lista de refatoração.
- Validar que os objetos de domínio não importam módulos de interface nem de infraestrutura.

### Critério de conclusão
- O código já tem fronteiras de responsabilidade reconhecíveis.
- O próximo passo fica claro: extrair domínio puro, depois isolar infraestrutura e só então lidar com o CLI.

---

## Fase 2 — Criar a camada de domínio puro

### Objetivo
Extrair regras sem I/O para um pacote novo e testável.

### O que criar
Um novo pacote, por exemplo:
- `src/tko/domain/`
- `src/tko/app/`
- `src/tko/infra/`
- `src/tko/interface/`

### O que migrar primeiro
Priorizar regras de negócio simples e de alto valor de teste:
- cálculo de percentual
- regras de progresso
- dependências entre tasks/quests
- status de execução
- normalização de metadados

### Tarefas
1. Extrair tipos de resultado:
   - `ExecutionResult`
   - `ProgressState`
   - `TaskSummary`
   - `QuestSummary`
2. Mover lógica de cálculo para classes puras.
3. Deixar que qualquer I/O aconteça fora do domínio.

### Verificação
- Escrever testes de unidade para a nova camada:
  - sem filesystem
  - sem terminal
  - sem subprocess
- Rodar:
  - `pytest -q `tko`.` ou testes específicos criados para esse módulo

### Critério de conclusão
- A camada de domínio tem comportamento estável e pode ser testada com objetos simples.

---

## Fase 3 — Introduzir seams para infraestrutura

### Objetivo
Permitir testar o código sem depender de subprocessos, `os.chdir` e console.

### O que analisar
Principalmente:
- `build.py`
- `run_executor.py`
- `git_cache.py`
- `runner.py`

### Tarefas
1. Criar interfaces ou abstrações para:
   - `CommandRunner`
   - `FileSystem`
   - `WorkingDirectoryService`
   - `Renderer`
   - `Logger`
2. Injetar essas dependências em serviços de aplicação.
3. Não deixar que o domínio conheça essas abstrações.

### Verificação
- Testes usando stubs/fakes em vez de shell.
- Verificar que o comportamento foi preservado.

### Critério de conclusão
- Quando o domínio é testado, ele não depende de sistema operacional, terminal nem repo real.

---

## Fase 4 — Refatorar o fluxo de execução

### Objetivo
Quebrar a classe de execução em serviços menores.

### O que analisar
- `run_context.py`
- `run_executor.py`

### Tarefas
1. Separar:
   - criação do contexto
   - cálculo do resultado
   - apresentação
   - persistência de log
   - execução de comandos
2. Transformar `RunContext` em container de dados, não em orquestrador de regra.
3. Garantir que a lógica de execução retorne um objeto pronto para apresentação.

### Entregáveis
- `ExecutionSummary`
- `RunPresenter`
- `ExecutionLogStore`
- `TestExecutionService`

### Verificação
- Testes sem terminal:
  - “dado X, resultado Y”
  - sem `Console.print`
  - sem `os.chdir`
- Rodar testes específicos e depois a suíte relevante.

### Critério de conclusão
- A execução de testes passa a ser testável por data objects e serviços.

---

## Fase 5 — Refatorar o repositório e o carregamento de estado

### Objetivo
Tirar do `Repository` a responsabilidade de agir como “caixa de ferramentas”.

### O que analisar
- `repository.py`
- `repository_builder.py`

### Tarefas
1. Separar:
   - carga de configuração
   - descoberta de repo
   - estado de workspace
   - serviços de git/cache
   - serviços de tarefa
2. Manter `Repository` como agregado de estado, não como “coletor de infraestrutura”.
3. Mover log, cache e biologia de git para serviços.

### Verificação
- Testes de repositório com diretório temporário.
- Garantir que a lógica de carregamento continua funcionando sem depender do terminal.

### Critério de conclusão
- O repo continua funcional, mas sem carregar a responsabilidade de processo e console.

---

## Fase 6 — Separar interface da aplicação

### Objetivo
O CLI só orquestra e delega.

### O que analisar
- `__main__.py`
- arquivos em `cli`

### Tarefas
1. Mover a criação de settings e wiring para um “bootstrap”.
2. Deixar a CLI responsável apenas por:
   - parsear argumentos
   - montar objetos
   - chamar casos de uso
   - renderizar resultado
3. Não colocar regra de negócio no nível do Typer.

### Verificação
- Testar os comandos com `CliRunner` de forma focada.
- Não usar mocks do “sistema inteiro”; testar apenas contrato de entrada/saída.

### Critério de conclusão
- O CLI não executa a lógica em si; ele apenas coordena.

---

## Fase 7 — Cobertura e testes de regressão

### Objetivo
Garantir que a estrutura nova continue estável.

### Tarefas
1. Criar testes para:
   - parsing
   - cálculo
   - regra de progressão
   - decisão de execução
   - carregamento de dados
2. Priorizar os módulos que já têm maior risco.
3. Manter testes pequenos e determinísticos.

### Verificação
- Rodar:
  - `pytest -q`
- Se a suíte for grande, rodar subset por fases:
  - domínio
  - app
  - infra
  - cli

### Critério de conclusão
- Cada regra importante tem teste específico e não depende de terminal ou filesystem.

---

## Fase 8 — Limpeza e estabilização

### Objetivo
Reducir o custo de mudança e manter a base evolutiva.

### Tarefas
1. Remover duplicidades
2. Simplificar nomes e responsabilidades
3. Eliminar “god objects”
4. Centralizar padrões de logger/console/runner
5. Estabelecer convenções de design para novos módulos

### Verificação
- Revisar com:
  - `pytest -q`
  - inspeção de módulos críticos
- Verificar se qualquer novo módulo continua respeitando as fronteiras

### Critério de conclusão
- Novas features podem ser adicionadas sem exigir hacks de terminal e shell.

---

## Ordem recomendada de execução

1. Fase 0 — baseline
2. Fase 1 — mapeamento de responsabilidades
3. Fase 2 — domínio puro
4. Fase 3 — seams de infraestrutura
5. Fase 4 — execução
6. Fase 5 — repositório
7. Fase 6 — interface
8. Fase 7 — regressão
9. Fase 8 — estabilização

---

## Regras operacionais para você e para o Copilot/Codex

### Regra 1: um alvo por etapa
Não tente refatorar tudo junto. Cada etapa deve ter um alvo claro.

### Regra 2: teste antes da refatoração
Em cada módulo:
- escrever teste do comportamento atual
- refatorar
- garantir que o teste continua verde

### Regra 3: sem módulo “gordo”
Se um arquivo faz domínio + CLI + filesystem + shell, ele precisa ser quebrado.

### Regra 4: a interface deve ser a última camada que mexe
A regra de negócio não deve depender de `Console`, `Path`, `os.chdir`, `subprocess` ou Typer.

---

## Como usar Copilot e Codex nessa sequência

### Para o Copilot
Use prompts do tipo:
- “Analise `run_executor.py` e me diga quais partes são domínio, infraestrutura e interface.”
- “Extraia a lógica de cálculo de percentual para uma classe pura com testes.”
- “Crie uma abstração para execução de comandos e me mostre como injetá-la sem quebrar o CLI.”
- “Identifique módulos de alto acoplamento no projeto e proponha uma ordem de refatoração.”

### Para o Codex
Use prompts mais focados:
- “Emita um plano de refatoração para separar domínio e infraestrutura em `run_executor.py` e `run_context.py`.”
- “Crie testes unitários para o cálculo de progresso e resultados de execução sem usar terminal.”
- “Refatore `build.py` para remover `os.chdir` e `subprocess.run` da lógica de negócio.”

---

## Critério de sucesso final

Ao fim da refatoração, o projeto deve ter:
- regras de negócio em módulos puros
- CLI e terminal isolados
- filesystem e subprocessos em adapters
- testes rápidos e determinísticos
- menos regressões em qualquer nova mudança

---

Se quiser, no próximo passo eu posso transformar este plano em uma checklist prática por PR, com:
- objetivo da etapa
- arquivos a tocar
- tasks do Copilot
- tasks do Codex
- comando de verificação final
- critério de aceite da etapa.