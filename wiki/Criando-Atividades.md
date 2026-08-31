# Guia para Criar um Repositorio de Tarefas

Este guia e o caminho principal para professores que querem criar e publicar
seus proprios repositorios de tarefas no TKO.

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

## Modelo mental

O indice trabalha com dois niveis:

- **Quest**: um bloco de aprendizagem, modulo ou missao.
- **Task**: uma atividade individual dentro de uma quest.

Exemplo minimo:

```md
# Minha Disciplina

## Operacoes Basicas key=@basic tag=basic xpgoal=2 min=70%

- [x] `@soma  gain=1 hard=1 size=1 type=make eval=test` [Soma](labs/soma/README.md)
- [x] `@media gain=1 hard=1 size=1 type=make eval=test` [Media](labs/media/README.md)
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
- [ ] `@soma gain=1 hard=1 size=1 type=make eval=test` [Soma](labs/soma/README.md)
- [ ] `@intro gain=1 type=read eval=self` [Texto introdutorio](wiki/intro.md)
```

Campos mais usados:

- `@chave`: identificador unico da task.
- `gain=valor`: ganho pedagogico.
- `hard=valor`: dificuldade.
- `size=valor`: tamanho ou volume de trabalho.
- `type=make`: tarefa de producao/programacao.
- `type=read`: tarefa de leitura ou consulta.
- `eval=test`: avaliacao automatica.
- `eval=self`: autoavaliacao.

Padroes aplicados pelo TKO:

- `gain=1`, `hard=1`, `size=1`.
- `type=make`, quando o tipo nao e informado.
- `eval=test` para `type=make`.
- `eval=self` para `type=read`.

Sintaxes antigas como `xp=`, `tier=`, `:make`, `:read`, `:test` e `:self` ainda
sao aceitas por compatibilidade. Em repositorios novos, prefira sempre os
campos chave-valor acima.

## Criando uma tarefa

Fluxo recomendado:

1. Crie uma pasta para a tarefa, por exemplo `labs/minha_tarefa/`.
2. Escreva o enunciado em `labs/minha_tarefa/README.md`.
3. Adicione `tests.toml` se a tarefa tiver testes automaticos.
4. Adicione a linha da task no `README.md` principal.
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

## Reaproveitando tarefas remotas

Uma task pode apontar para um `README.md` local ou para uma URL remota.

```md
- [ ] `@fila gain=2 hard=2 size=2 type=make eval=test` [Fila](https://github.com/qxcodeed/arcade/blob/main/labs/fila/README.md)
```

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
- As chaves `@...` sao curtas, unicas e estaveis.
- As linhas usam `gain`, `hard`, `size`, `type` e `eval`.
- Os enunciados abrem corretamente no GitHub.
- Os testes executam localmente nas tarefas com `eval=test`.
- `tko build index README.md labs` foi executado e o diff foi revisado.
- O repositorio foi commitado e publicado.

## Referencias

- [Marcadores e tipos de tarefas](game/tasks.md)
- [Criando testes e conversoes](Criando-Tarefas-e-Testes.md)
- [Gamificacao e progressao](Gamificacao-e-Progressao.md)
- [Build index](tools/build-index.md)
- [Markdown Preprocessor](tools/mdpp.md)
- [Filtragem e rascunhos](tools/filter.md)
