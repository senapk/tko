# Gestão de repositórios de turma

O GitHub Classroom foi descontinuado. O fluxo atual do TKO usa repositórios Git comuns para cada aluno, sem depender do serviço Classroom.

Existem dois caminhos principais:

- Cada aluno cria seu próprio repositório e compartilha acesso com o professor.
- O professor cria os repositórios em lote e entrega cada repositório ao aluno correspondente.

Para automatizar a criação e organização desses repositórios, use como referência:

- [senapk/classroom](https://github.com/senapk/classroom)

Esse repositório contém scripts para automatizar a criação de repositórios de turma.

## Modelo recomendado

O professor mantém dois tipos de repositório:

1. Repositório de conteúdo: contém índices, quests, tasks, enunciados e testes publicados para a disciplina.
2. Repositórios dos alunos: cada aluno trabalha em seu próprio workspace TKO e envia commits/push regularmente.

O repositório do aluno pode ser criado manualmente pelo aluno ou criado previamente pelo professor.

## Opção 1: aluno cria e compartilha

O aluno:

1. Cria um repositório no GitHub, normalmente privado.
2. Dá acesso ao professor como colaborador, quando necessário.
3. Clona o repositório na própria máquina, WSL ou Codespace.
4. Executa `tko init`.
5. Adiciona a fonte indicada pelo professor.
6. Resolve as atividades.
7. Faz commits e push com frequência.

Exemplo de configuração de fonte:

```bash
tko source add fup @fup
```

Para apontar para um repositório personalizado:

```bash
tko source add disciplina https://github.com/<usuario-ou-org>/<repositorio>
```

## Opção 2: professor cria em lote

O professor pode criar todos os repositórios da turma previamente, usando scripts próprios ou os scripts do projeto [senapk/classroom](https://github.com/senapk/classroom).

Nesse fluxo, o professor:

1. Prepara a lista de alunos.
2. Cria os repositórios em lote.
3. Define permissões de acesso.
4. Envia a cada aluno o link do seu repositório.
5. Orienta o aluno a clonar ou abrir o repositório no Codespaces.
6. Coleta os repositórios localmente quando precisar avaliar.

Esse fluxo é útil quando a turma precisa de padronização, repositórios privados ou nomes controlados.

## Codespaces

Para turmas que usam Codespaces, o repositório padrão para alunos é:

- [senapk/tko-student-starter](https://github.com/senapk/tko-student-starter)

Esse starter já traz scripts para instalar ferramentas de setup e para facilitar operações comuns com Git.

Fluxo comum do aluno:

1. Abrir o repositório no Codespaces.
2. Rodar o script de setup indicado pelo professor.
3. Escolher a linguagem da disciplina.
4. Validar `tko --version` e `tko --help`.
5. Rodar `tko open`.

Veja também [GitHub Codespaces](Codespaces.md).

## Coleta para avaliação

Para avaliar, o professor precisa ter os repositórios dos alunos disponíveis localmente.

Fluxo comum:

1. Clonar ou atualizar todos os repositórios dos alunos.
2. Entrar na pasta que contém esses repositórios.
3. Usar os comandos de coleta do TKO.

Exemplos:

```bash
tko class pull aluno1 aluno2 aluno3
tko class tasks aluno1 aluno2 aluno3
tko class skills aluno1 aluno2 aluno3
```

Os argumentos são caminhos para os repositórios locais dos alunos. Eles podem ser informados um a um ou expandidos pelo shell, conforme a organização da pasta.

## Evidências coletadas

O professor pode analisar:

- atividades realizadas;
- progresso por task;
- progresso por skill;
- histórico de execução;
- registros de auditoria, quando habilitados;
- commits e push no Git.

Os registros do TKO devem ser tratados como evidências de aprendizagem. Para aumentar a confiabilidade, use repositórios privados, permissões controladas, commits frequentes e coleta periódica.

## Checklist do professor

- Repositório de conteúdo publicado e testado.
- Fonte da disciplina definida para os alunos.
- Repositórios dos alunos criados ou instruções de criação enviadas.
- Permissões de acesso conferidas.
- Fluxo de clone, commit e push validado.
- Estratégia de coleta local definida.
- Scripts de automação testados antes de aplicar na turma inteira.
