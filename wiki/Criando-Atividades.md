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

A estrutura do repositório segue dois níveis:

-   **Quest** --- conjunto de tarefas relacionadas
-   **Task** --- atividade individual


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

## Formato de Task (linha única)

Cada task é definida em uma linha markdown, seguida de pares chave-valor:

Exemplo:

    - [ ] key=@t1 xp=10 type=task path=main eval=auto loss=part
    - [ ] @t2 xp=5 type=read path=side eval=self loss=free

**Campos suportados:**
- `key=@chave` ou `@chave`: identificador único da task
- `xp=valor`: valor em pontos/XP da tarefa
- `type=task` ou `type=read`: tipo da tarefa (produção ou consumo)
- `path=main` ou `path=side`: categoria/trilha da tarefa
- `eval=auto` ou `eval=self`: modo de avaliação
- `loss=zero`, `loss=part`, `loss=free`: política de penalidade por consulta

**Notas:**
- Apenas key é obrigatória.
- Campos podem aparecer em qualquer ordem.
- Campos não obrigatórios assumem valores padrão.
- Sintaxe antiga ainda é suportada por compatibilidade, mas recomenda-se o novo formato.

------------------------------------------------------------------------

## Benefícios dessa estrutura

Essa organização permite:

-   navegação simples pelo GitHub
-   integração direta com a ferramenta `tko`
-   reutilização de tarefas em diferentes cursos
-   contribuição fácil da comunidade

Cada tarefa é autocontida e pode ser reutilizada em outros repositórios
ou trilhas de aprendizado.


## Formato de Quest (linha única)

Cada quest é definida em uma linha de título markdown, seguida de pares chave-valor:

Exemplo:

    ## Ponteiros em C key=@ptr tag=ponteiro requires=@intro factor=2 total=100 threshold=80 lang=c lang=c++

**Campos suportados:**
- `key=@chave`: identificador único da quest
- `tag=nome`: habilidade/tópico trabalhado (pode repetir para múltiplos)
- `requires=@outra`: pré-requisito (pode repetir)
- `factor=valor`: multiplicador de XP das tasks
- `total=valor`: pontuação-alvo para 100% de completude
- `threshold=valor`: percentual mínimo para considerar a quest completa
- `lang=nome`: linguagem de programação específica (pode repetir, ex: lang=c lang=python)
- `active=true|false`: define se a quest está ativa (default: true). Se `active=false`, a quest e suas questões são desabilitadas e não participam da gamificação.

**Regras e padrões:**
- Apenas `key` é obrigatória.
- Se `tag` não for definida, será usada a própria `key` como tag.
- `factor` é opcional, valor padrão é 1.
- `requires` não é obrigatório, mas é usado para definir dependências e gamificação da disciplina.
- `total` define o XP (pontuação de tasks) necessário para atingir 100% da quest.
- `threshold` é opcional, o padrão é 50 (50%) e define o percentual mínimo para considerar a quest completa.
- `lang` é opcional, define as linguagens de programação específicas da quest.

**Notas:**
- Comentários HTML (`<!-- ... -->`) e crases são ignorados.
- Os campos podem aparecer em qualquer ordem após o título.

**Exemplo completo:**

    ## Estruturas de Repetição key=@loops tag=for tag=while requires=@intro factor=2 total=100 threshold=80 lang=python


## Dependências entre Quests, Tags e Habilidades

As **quests** podem declarar duas informações importantes:

1. **Quais tópicos/habilidades são trabalhados** (usando `tag=nome`)
2. **Quais quests precisam ser concluídas antes** (usando `requires=@outra`)

Essas informações são definidas diretamente no cabeçalho da missão usando os campos chave-valor.

Esse formato tem duas vantagens importantes:

- mantém o arquivo **legível para humanos**

---

## Exemplo de definição de habilidades e dependências

As habilidades/tópicos são declarados usando `tag=nome` (pode repetir para múltiplos):

```md
## Missão: Operações key=@operations tag=basic
## Missão: Seleção 1 key=@selection1 tag=if requires=@operations
## Missão: Seleção 2 key=@selection2 tag=if requires=@selection1
## Missão: Repetição1 key=@repetition1 tag=for requires=@selection2
## Missão: Repetição2 key=@repetition2 tag=for requires=@repetition1
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
- atualização automática de referências no VS Code
- permite construir **grafos de progressão de aprendizado**

Além disso, o sistema pode usar essas relações para:

- desbloquear quests conforme o progresso
- calcular domínio de habilidades/tags
- sugerir próximas atividades ao aluno
