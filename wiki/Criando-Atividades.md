# Guia para Criar um Repositorio de Tarefas

Este guia e o caminho principal para professores que querem criar e publicar
seus proprios repositorios de tarefas no TKO.

Para uma visão geral do fluxo completo, consulte o [ciclo de vida de tarefas](../docs/TASK_LIFECYCLE.md).

A ideia central e simples: o repositorio tem um `README.md` principal que
funciona como indice navegavel das atividades. Esse indice organiza as tarefas
em quests, guarda metadados pedagogicos e aponta para as pastas ou links onde
cada tarefa esta descrita.

## Estrutura minima

Um repositorio de tarefas pode comecar assim:

```txt
README.md
labs/
├── soma/
│   ├── README.md
│   └── tests.toml
└── media/
    ├── README.md
    └── tests.toml
```

Papeis dos arquivos:

- `README.md`: indice principal do repositorio, com quests e tasks.
- `labs/<tarefa>/README.md`: enunciado da tarefa.
- `labs/<tarefa>/tests.toml`: casos de teste, quando houver avaliacao automatica.
- `labs/<tarefa>/src/<lang>/...`: solucoes, rascunhos ou codigo de apoio, quando usados pela disciplina.

O repositorio de conteudo do professor nao precisa ter `.tko/`. Essa pasta e
normalmente parte do workspace do aluno, nao do formato publico das tarefas.

Quando uma tarefa externa é materializada, o TKO copia o conteúdo da atividade
para o caminho indicado pela chave. A URL original permanece em um comentário
HTML para permitir atualizações posteriores.

## Modelo mental

O indice trabalha com dois niveis:

- **Quest**: um bloco de aprendizagem, modulo ou missao.
- **Task**: uma atividade individual dentro de uma quest.

Exemplo minimo:

```md
# Minha Disciplina

## Operacoes Basicas key=@basic tag=basic xpgoal=2 min=70%

- [x] `@soma  eval=diff gain=1 cost=1 size=1` [Soma](labs/soma/README.md)
- [x] `@media eval=diff gain=1 cost=1 size=1` [Media](labs/media/README.md)
```

Use `[x]` nas tarefas que contam para a meta principal da quest. Ao rodar
`tko build index`, o TKO pode usar essas marcacoes para recalcular o `xpgoal`.
Tarefas extras ou desafios podem ficar com `[ ]`.

## Criando quests

Cada quest e declarada em um titulo Markdown com metadados em pares
chave-valor.

```md
## Vetores key=@vetores tag=array deps=@basic xpgoal=10 min=70% lang=c lang=python
```

Campos mais usados:

- `key=@chave`: identificador unico da quest.
- `tag=nome`: habilidade ou topico trabalhado.
- `deps=@outra`: quest que precisa vir antes.
- `xpgoal=valor`: meta de ganho pedagogico para completar a quest.
- `min=valor%`: percentual minimo para considerar a quest completa.
- `lang=nome`: linguagem associada a quest.
- `active=true|false`: desativa temporariamente a quest quando for `false`.

Regras praticas:

- `key` e o campo essencial.
- Se `tag` nao for informado, o TKO usa a propria chave como tag.
- `deps`, `lang` e `active` sao opcionais.
- Prefira chaves curtas, estaveis e sem espacos, como `@vetores`.

## Criando tasks

Cada task e uma linha Markdown com checkbox, metadados entre crases e link para
o recurso.

```md
- [ ] `@soma eval=diff gain=1 cost=1 size=1` [Soma](labs/soma/README.md)
- [ ] `@intro gain=1 cost=1 size=1 eval=none` [Texto introdutorio](wiki/intro/README.md)
```

Campos mais usados:

- `@chave`: identificador unico da task.
- `gain=valor`: ganho pedagogico.
- `cost=valor`: custo/dificuldade.
- `size=valor`: tamanho ou volume de trabalho.
- `eval=diff`: avaliacao automatica.
- `eval=self`: autoavaliacao.
- `eval=none`: leitura ou consulta sem avaliação.

Padroes aplicados pelo TKO:

- `gain=1`, `cost=1`, `size=1`.
- `eval` é obrigatório.

Sintaxes antigas como `xp=`, `tier=`, `:make`, `:read`, `:test` e `:self` ainda
sao aceitas por compatibilidade. Em repositorios novos, prefira sempre os
campos chave-valor acima.

## Criando uma tarefa

Fluxo recomendado:

1. Crie uma pasta para a tarefa, por exemplo `labs/minha_tarefa/`.
2. Escreva o enunciado em `labs/minha_tarefa/README.md`.
3. Adicione os testes no formato mais adequado à atividade, se houver avaliação
   automática.
4. Adicione a linha da task no `README.md` principal, ou deixe o indexador criá-la.
5. Rode o TKO localmente para validar.

Exemplo:

```bash
mkdir -p labs/minha_tarefa
$EDITOR labs/minha_tarefa/README.md
$EDITOR labs/minha_tarefa/tests.toml
$EDITOR README.md
cd labs/minha_tarefa
tko run
```

Para verificar os casos sem executar uma solução (inclusive quando os testes
estão no README ou em outro formato suportado):

```bash
tko task tests labs/minha_tarefa
```

## Escrevendo testes simples

O formato mais comum e `tests.toml` dentro da pasta da tarefa.

```toml
[[tests]]
input = '1 2\n'
output = '3\n'

[[tests]]
input = '''
10
20
'''
output = '''
30
'''
```

Para conversoes, testes em pasta, `cases.tio`, VPL e formatos especiais,
consulte [Criando testes e conversoes](Criando-Tarefas-e-Testes.md).

## Atualizando o indice

Depois de criar, renomear ou remover tarefas locais, rode:

```bash
tko build index README.md labs
```

Esse comando:

- encontra tarefas novas em `labs/`;
- remove links locais quebrados;
- alinha visualmente as linhas de tasks;
- atualiza `xpgoal` quando ha tarefas marcadas com `[x]`.

Detalhes e casos especiais estao em [Build index](tools/build-index.md).

Para testes, conversões e rascunhos, consulte [Criando Tarefas e Testes](Criando-Tarefas-e-Testes.md).

## Reaproveitando tarefas remotas

Uma task deve apontar para um `README.md` local ou para uma URL do GitHub que
aponte para um `README.md`. Não use URLs HTTP genéricas, links para diretórios
ou links para outros arquivos Markdown.

```md
- [ ] `@fila gain=2 cost=2 size=2 eval=diff` [Fila](https://github.com/qxcodeed/arcade/blob/main/labs/fila/README.md)
```

A chave externa é obrigatória porque também define onde a atividade será
materializada. O índice do professor pode ser preparado e atualizado assim:

```bash
tko index download README.md
tko index update README.md
```

O primeiro comando baixa as atividades externas ainda não materializadas. O
segundo substitui as cópias locais pelas versões atuais, descartando alterações
locais nessas pastas.

Para preparar um indice externo com links absolutos e reutilizaveis:

```bash
tko tool rebase @fup -o README.fup.md
```

Esse fluxo evita links relativos quebrados ao transportar uma lista de tarefas
entre repositorios. Veja [Rebase de links markdown](tools/rebase-links.md).

## Publicando para alunos

Fluxo tipico:

1. Crie ou atualize o repositorio de conteudo.
2. Valide o indice e as tarefas localmente.
3. Faca commit e push para o GitHub.
4. Informe aos alunos a URL do repositorio.
5. Oriente os alunos a registrar a fonte com `tko source add`.

Exemplo para o aluno:

```bash
tko init
tko source add disciplina https://github.com/<usuario>/<repositorio>
tko open
```

## Checklist antes de liberar

- O `README.md` principal lista as quests e tasks esperadas.
- Cada task local aponta para um `README.md` existente.
- Cada task externa aponta para um `README.md` local ou para uma URL GitHub de um `README.md` existente.
- As chaves `@...` sao curtas, unicas e estaveis.
- As linhas usam `gain`, `cost`, `size` e `eval`.
- Os enunciados abrem corretamente no GitHub.
- Os testes executam localmente nas tarefas com `eval=diff`.
- `tko build index README.md labs` foi executado e o diff foi revisado.
- O repositorio foi commitado e publicado.

## Referencias

- [Marcadores e tipos de tarefas](game/tasks.md)
- [Criando testes e conversoes](Criando-Tarefas-e-Testes.md)
- [Gamificacao e progressao](Gamificacao-e-Progressao.md)
- [Build index](tools/build-index.md)
- [Markdown Preprocessor](tools/mdpp.md)
- [Filtragem e rascunhos](tools/filter.md)
