# Arquitetura do TKO

Este documento apresenta a visão técnica do TKO para manutenção, extensão e refatoração.

## Visão em camadas

Fluxo macro:

1. CLI recebe comando e parâmetros.
2. Contexto de aplicação é montado.
3. Repositório e tarefas são carregados.
4. Execução e avaliação são processadas.
5. Resultado é apresentado e persistido em logs/progresso.

## Camada CLI

Arquivo de entrada principal:

- src/tko/__main__.py

Responsabilidades:

1. Registrar comandos e subcomandos.
2. Ler opções globais (settings, changedir, width, update, offline, etc).
3. Inicializar AppContext para comandos subsequentes.

Subapps principais:

- build
- task
- config
- reset
- remote
- collect
- class
- tool

## Contexto e configuração

Peças centrais:

- src/tko/app_context.py
- src/tko/config/settings.py

Responsabilidades:

1. Resolver diretórios de trabalho e configurações.
2. Controlar comportamento global (cache, update, offline, render).
3. Disponibilizar contexto consistente para os comandos.

## Repositórios e carga de tarefas

Pacotes principais:

- src/tko/repository
- src/tko/loader
- src/tko/game

Responsabilidades:

1. Carregar fontes locais e remotas.
2. Parsear README de índice com quests/tasks.
3. Transformar metadados em estrutura de execução e progresso.

## Execução de código

Pacote principal:

- src/tko/run

Elementos relevantes:

- src/tko/cmds/cmd_run.py
- src/tko/run/run_context.py
- src/tko/run/run_loader.py
- src/tko/run/run_executor.py
- src/tko/run/test_loop_service.py

Responsabilidades:

1. Preparar ambiente de execução (solver, testes, working dir).
2. Decidir modo de execução:
   - raw terminal
   - TUI curses
3. Executar testes, coletar resultados e calcular taxa de acerto.
4. Persistir logs e estado de execução.

## Apresentação de resultado

Pacotes principais:

- src/tko/run/run_presenter.py
- src/tko/util/rtext.py
- src/tko/util/raw_terminal.py

Responsabilidades:

1. Exibir feedback legível no terminal.
2. Renderizar diferenças de saída quando aplicável.
3. Adaptar render para largura e modo visual (colorido/mono).

## TUI e interação

Pacote principal:

- src/tko/tester

Responsabilidades:

1. Interface interativa para navegação e execução.
2. Integração com run loader/executor.
3. Controle de abertura de arquivos e ações no ciclo de teste.

## Modelo de progresso e gamificação

Pacote principal:

- src/tko/game

Responsabilidades:

1. Parse de quests e tasks.
2. Cálculo de métricas (rate, quality, XP).
3. Controle de desbloqueio e progressão.

## Fluxo de dados (resumo)

1. Usuário executa comando CLI.
2. CLI cria AppContext com settings e diretório alvo.
3. Camada de repository/loader carrega estrutura de tarefas.
4. Camada run prepara solver e testes.
5. Executor processa casos e coleta resultados.
6. Presenter exibe feedback e tracker persiste log.
7. Camada game atualiza visão de progresso.

## Pontos de extensão

1. Linguagens novas:
   - ajustar configuração e guias em docs/LANGUAGE_SUPPORT.md
2. Novos formatos de tarefa/teste:
   - refletir em docs/FORMATS.md
3. Novos comandos:
   - registrar em src/tko/__main__.py e subapps CLI
4. Nova lógica de avaliação:
   - evoluir serviços em src/tko/run e src/tko/game

## Princípios de manutenção

1. Evitar acoplamento entre UI e engine de execução.
2. Preservar compatibilidade de sintaxe de tarefas sempre que possível.
3. Cobrir mudanças com testes e atualização de docs no mesmo PR.
4. Manter mensagens de erro claras para aluno e professor.

## Referências relacionadas

- docs/REFERENCE.md
- docs/TASK_LIFECYCLE.md
- docs/LANGUAGE_SUPPORT.md
- docs/TESTING.md
- CONTRIBUTING.md
- wiki/Desenvolvimento-de-Tarefas.md
