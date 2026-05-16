# Ciclo de vida de tarefas no TKO

Este guia descreve o fluxo completo de criação, publicação e consumo de tarefas no TKO.

## Visão geral

O modelo do TKO é descentralizado e baseado em Git:

1. O professor cria tarefas no próprio repositório.
2. O aluno conecta o repositório remoto no TKO local.
3. O TKO sincroniza periodicamente e exibe novas atividades.

## Fluxo do professor

### Criar e publicar tarefa

Uma tarefa normalmente contém:

- descrição do problema (README da tarefa)
- casos de teste (ex.: cases.tio ou formato equivalente)
- opcionalmente rascunhos por linguagem

Depois de criar a tarefa, o professor publica no repositório Git da disciplina.

Na próxima sincronização dos alunos, a tarefa aparece automaticamente no TKO.

### Estratégias de autoria

O professor pode:

1. Reusar atividades já existentes em qualquer repositório compatível com TKO:
   - oficiais
   - comunidade
   - outros professores

   Basta referenciar a URL completa da tarefa no README de índice da disciplina.

2. Criar atividade nova no próprio repositório:
   - enunciado
   - testes
   - rascunhos (opcional)

## Fluxo do aluno

Primeira configuração no ambiente local:

1. Inicializar estrutura local de tarefas:

   tko init

2. Adicionar remoto da disciplina:

   tko remote add <alias> <url_git_do_professor>

3. Abrir interface de tarefas:

   tko open

## Sincronização e cache remoto

Internamente, o TKO trabalha com clone e cache local dos repositórios remotos.

Comportamento padrão:

1. No primeiro acesso, faz clone da fonte remota.
2. Mantém cache por 1 hora.
3. Após 1 hora, ao abrir o TKO novamente, tenta atualizar (pull/sync).
4. Se o professor publicou novas atividades, elas passam a aparecer para os alunos.

## Cenários comuns

### Professor adicionou novas atividades

- Publica no repositório da disciplina.
- Aluno abre o TKO após janela de cache.
- Novas tarefas são descobertas automaticamente.

### Professor quer montar disciplina usando material existente

- Mantém README de índice da disciplina.
- Referencia tarefas prontas por URL completa.
- Publica e distribui para turma.

### Aluno quer estudar fora de disciplina

- Pode adicionar remotos públicos de trilhas e atividades.
- Segue o mesmo fluxo de init, remote add e open.

## Guias relacionados

- docs/REFERENCE.md
- wiki/Criando-Atividades.md
- wiki/Criando-Tarefas-e-Testes.md
- wiki/Testando-Sem-Disciplina.md
