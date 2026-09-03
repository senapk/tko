# Ciclo de vida de tarefas no TKO

Este guia descreve o fluxo completo de criação, publicação e consumo de tarefas no TKO.

## Visão geral

O modelo do TKO é descentralizado e baseado em Git:

1. O professor cria tarefas no próprio repositório.
2. O aluno conecta a fonte de atividades no TKO local.
3. O TKO sincroniza periodicamente e exibe novas atividades.

## Fluxo do professor

### Criar e publicar tarefa

Uma tarefa normalmente contém:

- descrição do problema (README da tarefa)
- casos de teste (ex.: cases.tio ou formato equivalente)
- opcionalmente rascunhos por linguagem

Toda tarefa deve ser referenciada por um arquivo `README.md`, usando um caminho
local ou uma URL do GitHub apontando para esse arquivo. URLs HTTP genéricas,
links para diretórios e links para outros arquivos não são aceitos pelo TKO.

Depois de criar a tarefa, o professor publica no repositório Git da disciplina.

Na próxima sincronização dos alunos, a tarefa aparece automaticamente no TKO.

### Estratégias de autoria

O professor pode:

1. Reusar atividades já existentes em qualquer repositório compatível com TKO:
   - oficiais
   - comunidade
   - outros professores

   Basta referenciar no README de índice da disciplina o caminho local ou a URL
   do GitHub para o `README.md` da tarefa.

2. Criar atividade nova no próprio repositório:
   - enunciado (`README.md`);
   - assets opcionais;
   - artefatos definidos pelo tipo: draft para `self`, código e testes para
     `diff`, e futuramente testes programáticos para `code`.

## Fluxo do aluno

Primeira configuração no ambiente local:

1. Inicializar estrutura local de tarefas:

   tko init

2. Adicionar remoto da disciplina:

   tko source add <label> <url_git_do_professor>

3. Abrir interface de tarefas:

   tko open

## Sincronização e cache remoto

Internamente, o TKO trabalha com clone e cache local das fontes Git.

Comportamento padrão:

1. No primeiro acesso, faz clone da fonte Git externa.
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
- Referencia tarefas prontas por caminho local ou por URL do GitHub apontando para `README.md`.
- Publica e distribui para turma.

### Aluno quer estudar fora de disciplina

- Pode adicionar remotos públicos de trilhas e atividades.
- Segue o mesmo fluxo de init, source add e open.

## Materialização de tarefas externas

Toda tarefa possui uma pasta materializada. Uma tarefa local trabalha diretamente
na origem; uma tarefa externa é copiada para a área de trabalho do aluno quando
é baixada.

Em ambos os casos, a pasta contém:

- `README.md`;
- a pasta `assets/`;
- os demais arquivos Markdown diretamente na pasta da tarefa.

Os artefatos adicionais dependem exclusivamente do tipo da tarefa: `wiki` não
recebe draft nem testes, `self` recebe draft, e `diff` recebe draft e testes.
O tipo `code` fica reservado para testes programáticos futuros.

## Guias relacionados

- [Referência rápida da CLI](REFERENCE.md)
- [Guia para criar repositórios de tarefas](../wiki/Criando-Atividades.md)
- [Criando testes e conversões](../wiki/Criando-Tarefas-e-Testes.md)
- [Testando sem estar em uma disciplina](../wiki/Testando-Sem-Disciplina.md)
