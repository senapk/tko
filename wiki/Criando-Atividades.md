# Estrutura de um Repositório de Tarefas

Um repositório de tarefas contém um arquivo principal `README.md` que
funciona como **índice navegável das atividades**.

Esse arquivo lista as tarefas disponíveis e define metadados usados pelo
sistema de gamificação, como:

-   pontuação
-   habilidades associadas
-   nível ou tipo de tarefa

Cada item da lista aponta para uma pasta contendo a descrição completa
da atividade.

O `README.md` é projetado para ser **legível diretamente no GitHub**,
permitindo que alunos naveguem e explorem o repositório mesmo fora da
ferramenta.

------------------------------------------------------------------------

## Organização conceitual

A estrutura do repositório segue três níveis:

-   **Cluster** --- agrupamento de conceitos
-   **Quest** --- conjunto de tarefas relacionadas
-   **Task** --- atividade individual

------------------------------------------------------------------------

## Exemplo de `README.md`

    # Repositório de Tarefas de Programação

    ## Cluster: Operações Básicas

    ### Quest: Operações com Inteiros

    - [ ] `@tres   *1 :open` [Soma de três inteiros](base/tres/README.md)
    - [ ] `@resto  *1 :leet` [Resultado e resto na divisão](base/resto/README.md)
    - [ ] `@media  *1 :leet` [Média de dois inteiros](base/media/README.md)
    - [ ] `@sobrou *1 :leet` [Calculando quanto sobrou](base/sobrou/README.md)

Cada linha representa uma tarefa e inclui metadados compactos.

------------------------------------------------------------------------

## Convenções

A sintaxe utilizada na lista segue algumas convenções:

-   `@nome` --- chave única da tarefa
-   `*N` --- pontuação associada
-   emojis --- classificações da tarefa

Exemplos:

-   `:leet` --- tarefa com **testes automatizados**
-   `:open` --- tarefa **aberta**, sem testes automáticos

O link aponta para o `README.md` da pasta da tarefa, onde está a
descrição completa do problema.

------------------------------------------------------------------------

## Estrutura de uma tarefa

Cada tarefa possui sua própria pasta contendo os arquivos necessários
para resolução.

Uma tarefa normalmente inclui:

-   descrição do problema
-   arquivos de rascunho para o aluno
-   testes automatizados (opcional)

Exemplo de estrutura:

    task/
    ├─ README.md
    ├─ .cache/drafts/
    │  ├─ py/draft.py
    │  └─ go/draft.go
    ├─ local.sh # script opcional para configurações locais
    └─ tests.toml

### Arquivos

**README.md**\
Descrição completa do problema, exemplos de entrada e saída e instruções
da tarefa.

**.cache/drafts/**\
Arquivos iniciais fornecidos para o aluno em diferentes linguagens.

**tests.toml**\
Arquivo opcional contendo casos de teste automatizados.

------------------------------------------------------------------------

## Benefícios dessa estrutura

Essa organização permite:

-   navegação simples pelo GitHub
-   integração direta com a ferramenta `tko`
-   reutilização de tarefas em diferentes cursos
-   contribuição fácil da comunidade

Cada tarefa é autocontida e pode ser reutilizada em outros repositórios
ou trilhas de aprendizado.



## Dependências entre Quests e Habilidades

As **quests** podem declarar duas informações importantes:

1. **quais habilidades são trabalhadas**
2. **quais quests precisam ser concluídas antes**

Essas informações são definidas diretamente no cabeçalho da missão
utilizando comentários Markdown e links internos.

Esse formato tem duas vantagens importantes:

- mantém o arquivo **legível para humanos**
- permite que o **VSCode atualize automaticamente as referências**
  quando títulos são renomeados

---

## Definição de habilidades

As habilidades são declaradas usando a sintaxe:

```

<!-- +habilidade:valor -->

```

Onde:

- `+` indica que a quest **contribui para uma habilidade**
- `habilidade` é o identificador da habilidade
- `valor` define o **peso ou pontuação** associada

Exemplo:

```md
### Missão: Operações<!-- +basic:1 -->

Isso indica que as tarefas dessa missão trabalham a habilidade `basic`
com peso `1`.

Uma mesma missão pode contribuir para várias habilidades:
### Missão: Listas<!-- +arrays:1 +loops:1 -->

```

---

## Definição de dependências entre quests

Dependências são declaradas utilizando **links Markdown internos**.

Sintaxe:

```md

[](#slug-da-missao)

```

Isso indica que a missão atual depende da missão referenciada.

Exemplo:

```md

### Missão: Seleção 1<!-- +if_else:1 --> [](#missão-operações)

```

Nesse caso:

- a missão trabalha a habilidade `if_else`
- a missão **Operações** deve ser concluída antes

---

## Exemplo completo

```md

### Missão: Operações<!-- +basic:1 -->

### Missão: Seleção 1<!-- +if_else:1 --> [](#missão-operações)

### Missão: Seleção 2<!-- +if_else:1 --> [](#missão-seleção-1)

### Missão: Repetição1 <!-- +for:1 --> [](#missão-seleção-1)

### Missão: Repetição2 <!-- +for:1 --> [](#missão-repetição-1)

```

Esse conjunto define o seguinte grafo de progressão:

```txt

Operações
↓
Seleção 1
↓
Seleção 2
↓
Repetição 1
↓
Repetição 2

```

---

## Benefícios desse modelo

Essa abordagem oferece várias vantagens:

- dependências **claras e visíveis no README**
- fácil edição manual
- compatível com Markdown padrão
- atualização automática de referências no VSCode
- permite construir **grafos de progressão de aprendizado**

Além disso, o sistema pode usar essas relações para:

- desbloquear quests conforme o progresso
- calcular domínio de habilidades
- sugerir próximas atividades ao aluno
```

## Edição com o VSCode

Abra seu arquivo de configurações e adicione as seguintes linhas:

```json
"markdown.updateLinksOnFileMove.enabled": "always",
```

Isso garante que, ao mover ou renomear um título ou arquivo pelo VSCode, o VSCode atualize automaticamente os links internos que fazem referência a ele.
