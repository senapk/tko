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

## Tasks

Uma tarefa segue a seguinte estrutura:

```md
[ ] @label :marcadores [Título](pasta/README.md)

Você pode empacotar dentro de crases para alinhas ou tags html para esconder, mas o formato é sempre o mesmo:
[ ] `@label :marcadores`[Título](pasta/README.md)
[ ] <!-- @label :marcadores -->[Título](pasta/README.md)
```

### Marcadores

Cada marcador representa uma propriedade da questão.

```txt
: [=|+] [$|%] [0..9] [a|u|t] [?|!]
(Ordem Livre)

Pergunta               Categoria   Valores                  Padrão
---------------------- ----------- ------------------------ --------
É Obrigatório?         Prioridade  =:main, +:side           =
Consumir ou Produzir?  Ação        $:edit, %:view           $
Quem avalia?           Avaliação   a:auto, u:user, t:tick   a
Quanto vale?           Nível       0..9                     1
Pode consultar?        Consulta    ?:open, !:exam           ?
```

**Regras:**

- Marcadores omitidos usam o valor padrão. 
- Se não houver ":" a atividade usa todos os valores padrão.
- Caso não existe um marcador para uma categoria, o valor padrão é assumido.
- A ordem dos marcadores é livre.
- Se dois marcadores de mesma categoria forem especificados, o último prevalece.
- Marcadores são case-sensitive.

### Símbolos no TKO

```txt
Categoria   Código   Símbolo   Nome    Significado
----------- -------- --------- ------- ---------------------------------------
Avaliação   a        ●         auto    avaliação automática por testes
            u        ○         user    avaliação feita pelo próprio usuário
            t        ◇         tick    apenas registro de conclusão (sem avaliação)

Ação        $        ✎         edit    editar / produzir conteúdo
            %        ↗         view    visualizar / consumir conteúdo

Prioridade  =        ★         main    tarefas sugeridas
            +        ☆         side    tarefas opcionais

Consulta    ?        ↺         open    consulta permitida
            !        ⊘         exam    consulta proibida
```

**Comportamento da ação view**

Se o view for um link remoto → abre no navegador.
Se o view for um link local → o arquivo é copiado para a pasta do aluno e não é aberto automaticamente.

**Nível**

O nível representa apenas a dificuldade/peso da atividade e é indicado somente por único número:

:0 :1 ... :9

**Exemplos**

```txt
Marcação   Interpretação
---------- ---------------------------------------------
:          main, edit, nível 1, auto, open
:%         leitura obrigatória
:+%        leitura extra
:2$u       exercício nível 2 com autoavaliação
:3$a!      prova automática nível 3
:0t%       leitura sem pontuação
:1t$       resumo apenas para entrega
:+3u$?     projeto extra com consulta
```

**Observação:**

| Dimensão   | Pergunta              |
| ---------- | --------------------- |
| Prioridade | É obrigatório?        |
| Ação       | Consumir ou produzir? |
| Avaliação  | Quem avalia?          |
| Consulta   | Pode consultar?       |
| Nível      | Quanto vale?          |

**Restrições**

Utilizar dois marcadores de mesma categoria é permitido, mas o último prevalece. Exemplo:

```txt
:324ta → nível 3, auto
```

Mesmo que qualquer combinação seja possível, nem todas fazem sentido, pois não vão gerar interações coerentes no sistema. Exemplo:

```txt
:a% → avaliação automática, mas para ser consumida, o que não faz sentido. O ideal seria :a$.
:!% → consulta proibida, mas para ser consumida, o que não faz sentido. O ideal seria :!$.
```

Atividades para serem consumidas normalmente vão estar como `tick` ou `user`.

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
+habilidade[:valor]
```

Onde:

- `+` indica que a quest **contribui para uma habilidade**
- `habilidade` é o identificador da habilidade
- `valor` define o **peso ou pontuação** associada

Exemplo:

```md
## Missão: Operações  +basic @basic
Isso indica que as tarefas dessa missão trabalham a habilidade `basic` com peso `1`.
A chave @basic é a chave da atividade.
```

Uma mesma missão pode contribuir para várias habilidades e pode definir requisitos de outras missões usando links internos.
```md
## Missão: Listas +loops:2 +for @list
Isso indica que as tarefas dessa missão trabalham a habilidade `loops` com peso `2` e a habilidade `for` com peso `1`.
A chave @list é a chave da atividade.
```

---

## Definição de dependências entre quests

Dependências são declaradas utilizando referências para chaves de outras missões, usando a sintaxe:

```
!@outra_missão
```

Sintaxe:

```md
### Missão: Seleção 1 +if @selection !@operations
```

Nesse caso:

- a missão trabalha a habilidade `if` com peso `1`
- a missão `operations` deve ser concluída antes de `selection`

---

## Exemplo completo

```md

### Missão: Operações +basic @operations

### Missão: Seleção 1 +if @selection1 !@operations

### Missão: Seleção 2 +if @selection2 !@selection1

### Missão: Repetição1 +for:2 @repetition1 !@selection2

### Missão: Repetição2 +for:2 @repetition2 !@repetition1

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
