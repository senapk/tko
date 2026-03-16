# O-que-é-o-tko

O TKO é uma Plataforma de Prática Deliberada em Programação (CLI/TUI)

## 1. Visão Geral

A ferramenta descrita é um **ambiente de prática de programação
local-first**, orientado a terminal, que permite estudantes resolverem
tarefas de programação em seu próprio ambiente de desenvolvimento (IDE
ou editor), enquanto o sistema acompanha o processo de resolução e
coleta dados sobre a evolução da solução.

A proposta central não é apenas verificar se o código final funciona,
mas **capturar o processo de aprendizagem** --- incluindo tentativas,
erros, tempo de interação e evolução do código.

O sistema é **open source**, distribuído via repositórios Git, e pode
ser usado gratuitamente por qualquer pessoa ou instituição.

------------------------------------------------------------------------

# 2. Objetivos Educacionais

A ferramenta foi projetada para promover:

-   **Prática deliberada em programação**
-   Aprendizado baseado em tentativa e erro
-   Feedback imediato através de testes automatizados
-   Reflexão do aluno sobre o próprio processo de solução

Diferente de muitas plataformas tradicionais que avaliam apenas a
submissão final, o sistema enfatiza:

-   o processo de construção da solução
-   a progressão gradual de entendimento
-   a interação contínua com o problema

Esse modelo aproxima-se de abordagens conhecidas na pesquisa educacional
como:

-   Process-based assessment
-   Learning analytics
-   Deliberate practice environments

------------------------------------------------------------------------

# 3. Arquitetura Geral

A arquitetura segue um modelo **local-first e distribuído**.

## Componentes principais

1.  CLI da ferramenta
2.  Interface TUI (terminal UI)
3.  Repositórios de tarefas
4.  Sistema de testes automatizados
5.  Sistema de logs e analytics
6.  Integração com Git e GitHub Classroom

Não existe dependência obrigatória de servidores centrais.

O fluxo básico:

    aluno recebe repositório
    ↓
    abre workspace
    ↓
    inicia TUI
    ↓
    seleciona tarefa
    ↓
    edita código no seu editor
    ↓
    executa testes
    ↓
    analisa feedback
    ↓
    repete até solução

------------------------------------------------------------------------

# 4. Fluxo do Aluno

O aluno trabalha em um **workspace local**.

### Etapas principais

1.  Criar pasta de trabalho
2.  Adicionar repositório de tarefas
3.  Abrir a interface TUI
4.  Navegar pelas tarefas disponíveis
5.  Baixar ou ativar uma tarefa
6.  Editar arquivos no editor de preferência
7.  Executar testes automatizados
8.  Visualizar diffs e progresso
9.  Executar testes personalizados
10. Concluir tarefa e registrar autoavaliação

Durante esse processo, o sistema registra eventos relevantes.

------------------------------------------------------------------------

# 5. Estrutura de Tarefas

Cada tarefa possui:

-   descrição do problema
-   arquivos base para o aluno
-   testes automatizados
-   metadados pedagógicos

Exemplo de estrutura:

    task/
     ├─ task.yml
     ├─ README.md
     ├─ template/
     │   └─ solution.py
     ├─ tests/
     │   ├─ input/
     │   └─ output/
     └─ hints.md

Metadados incluem:

-   habilidades envolvidas
-   pontos da tarefa
-   dificuldade
-   dependências

------------------------------------------------------------------------

# 6. Gamificação

O sistema inclui elementos de gamificação para aumentar engajamento.

Cada tarefa pode ter:

-   pontuação
-   tags de habilidade
-   dificuldade

O aluno pode acompanhar:

-   progresso por habilidade
-   porcentagem de domínio
-   pontos acumulados

Exemplo de visualização:

    loops        ███████░░░ 70%
    strings      █████████░ 90%
    recursão     ██░░░░░░░░ 20%

------------------------------------------------------------------------

# 7. Sistema de Registro de Processo

O sistema registra **eventos durante a resolução da tarefa**.

Existem dois tipos principais de eventos.

## Eventos de execução

Registrados quando o aluno executa intencionalmente o código.

Incluem:

-   diff do código
-   número de testes que passaram
-   número de testes que falharam

Exemplo:

    run
    diff_id: 3
    tests_passed: 5
    tests_failed: 3

## Eventos de atividade

Registram apenas interação, sem salvar código.

Exemplo:

    edit_activity
    lines_changed: 4

Essa separação permite:

-   acompanhar atividade
-   manter baixo volume de dados
-   preservar apenas estados relevantes

------------------------------------------------------------------------

# 8. Reconstrução da Evolução da Solução

Como os diffs são armazenados incrementalmente, é possível reconstruir
qualquer versão do código.

Isso permite criar:

-   histórico completo da solução
-   replay da resolução da tarefa
-   análise pedagógica da trajetória

Exemplo de progressão:

    execução 1 → 0/10 testes
    execução 2 → 3/10 testes
    execução 3 → 7/10 testes
    execução 4 → 10/10 testes

------------------------------------------------------------------------

# 9. Replay da Resolução

Com os eventos registrados, é possível gerar uma linha do tempo da
solução.

Exemplo:

    00:00 tarefa iniciada
    00:02 edição detectada
    00:05 execução → 0/10
    00:08 edição detectada
    00:10 execução → 3/10
    00:14 execução → 7/10
    00:18 execução → 10/10

Isso permite que professores analisem o processo de aprendizagem.

------------------------------------------------------------------------

# 10. Integração com GitHub

O sistema se integra naturalmente com:

-   Git
-   GitHub
-   GitHub Classroom

Fluxo típico:

    professor cria repositório de tarefas
    ↓
    GitHub Classroom distribui repositórios
    ↓
    alunos resolvem tarefas localmente
    ↓
    commits registram evolução
    ↓
    professor analisa histórico

Essa integração fornece rastreabilidade adicional do processo.

------------------------------------------------------------------------

# 11. Compatibilidade com Ambientes de Desenvolvimento

Uma das decisões arquiteturais principais é permitir que o aluno utilize
seu **ambiente de desenvolvimento nativo**.

Isso inclui:

-   VSCode
-   Vim
-   Emacs
-   PyCharm
-   Neovim
-   outros editores

A ferramenta funciona como **orquestradora do fluxo de aprendizagem**,
não como editor.

------------------------------------------------------------------------

# 12. Compatibilidade com Cloud Development

A ferramenta funciona bem com ambientes como:

GitHub Codespaces.

Isso permite criar laboratórios prontos com:

-   linguagem instalada
-   dependências configuradas
-   tarefas disponíveis

------------------------------------------------------------------------

# 13. Vantagens em Relação a Plataformas Web

Muitas plataformas educacionais usam editores em navegador.

O modelo desta ferramenta difere porque:

-   usa ambiente real de desenvolvimento
-   executa testes localmente
-   não exige infraestrutura de servidores
-   escala facilmente

Arquitetura típica da ferramenta:

    terminal
    +
    editor local
    +
    git

------------------------------------------------------------------------

# 14. Acessibilidade e Custo

A proposta também tem um objetivo social importante.

Como o sistema é:

-   open source
-   local-first
-   distribuído via Git

Ele permite que qualquer pessoa ou instituição utilize a plataforma sem
custo de infraestrutura.

Isso torna possível:

-   ensino comunitário
-   cursos independentes
-   autoaprendizado

------------------------------------------------------------------------

# 15. Posicionamento de Mercado

A ferramenta ocupa um espaço pouco explorado entre:

-   plataformas de exercícios online
-   ambientes profissionais de desenvolvimento

Ela se posiciona como:

**Terminal-based deliberate practice environment for programming.**

Ou:

**Local-first programming learning platform.**

Comparação simplificada:

  Característica          Ferramenta
  ----------------------- ------------
  CLI                     sim
  TUI                     sim
  Testes locais           sim
  Gamificação             sim
  Analytics educacional   sim
  Execução local          sim

------------------------------------------------------------------------

# 16. Diferencial Principal

O diferencial mais importante é que o sistema captura:

**o processo de construção da solução**, não apenas o resultado final.

Isso permite:

-   observar aprendizado real
-   detectar padrões de resolução
-   analisar dificuldades conceituais
-   fornecer feedback pedagógico mais rico

------------------------------------------------------------------------

# 17. Potencial Futuro

O modelo abre caminho para evoluções como:

-   análise automática de trajetórias de solução
-   recomendações adaptativas de tarefas
-   visualizações de progresso da turma
-   análise de padrões de aprendizagem

------------------------------------------------------------------------

# 18. Conclusão

A ferramenta combina:

-   prática deliberada
-   feedback automático
-   observação do processo de resolução
-   execução local em ambiente real

Essa combinação é rara em plataformas educacionais e cria um ambiente
poderoso para ensino de programação.
