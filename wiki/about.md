# O que é o TKO

O TKO é um ambiente de aprendizagem executado no terminal para organizar,
realizar, testar e acompanhar atividades, especialmente atividades de
programação.

Ele separa três responsabilidades:

- fontes e índices de atividades;
- área de trabalho do aluno;
- histórico de execução, testes e evolução.

O TKO pode ser usado com qualquer editor e integrado a repositórios Git. O
professor publica atividades em um repositório; o aluno cadastra a fonte,
escolhe as tarefas e trabalha no próprio workspace.

## Comece por aqui

- [Conceitos e arquitetura](Conceitos-e-Arquitetura.md): modelo conceitual,
  fontes, origem, workspace e materialização.
- [Ciclo de vida de tarefas](../docs/TASK_LIFECYCLE.md): fluxo completo de
  criação, publicação e consumo.
- [Fazendo atividades](Fazendo-Atividades.md): tutorial do aluno.
- [Criando atividades](Criando-Atividades.md): guia do professor para
  organizar quests e tasks.
- [Marcadores e tipos de tarefas](game/tasks.md): sintaxe dos índices.

## Princípio central

Uma tarefa sempre aponta para um `README.md` local ou para um `README.md` no
GitHub.

Tarefas locais trabalham diretamente na origem. Tarefas externas são
materializadas na área de trabalho do aluno. A cópia inclui o README, `assets/`
e os demais Markdown da pasta; somente tarefas externas `make` também recebem
testes e rascunhos.

## Navegação

Consulte o [índice da Wiki](README.md) para encontrar guias por público e por
assunto.
