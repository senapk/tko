# Operadores de Corte

A ferramenta de filtragem utiliza diretivas em comentários para transformar o código-fonte com base em **estados de tratamento** e **escopo por indentação**.

---

## Conceito

As diretivas não são simples ações isoladas, mas sim **definições de estado** para o processamento do código:

- Cada linha do arquivo é processada sob um determinado estado ativo.
- O estado padrão e inicial é `@KEEP` (manter código na saída).
- Uma diretiva altera o estado do escopo correspondente para as linhas seguintes.
- Não existem comandos de fechamento como `@END`; o ciclo de vida dos estados é gerenciado automaticamente pelo **retorno da indentação** e pela **substituição no mesmo nível**.

---

## Operadores

Os quatro operadores disponíveis representam os seguintes estados:

| Operador | Nome | Estado / Efeito |
| :--- | :--- | :--- |
| `@KEEP` | Keep | **Mantém** o código inalterado na saída (estado padrão) |
| `@DROP` | Drop | **Remove** as linhas do código da saída |
| `@COM`  | Comment | **Comenta** as linhas do código |
| `@UNC`  | Uncomment | **Descomenta** as linhas que já estavam comentadas |

As diretivas devem ser escritas no formato de comentário da linguagem do arquivo:

**Python / Shell / YAML (`#`)**:
```python
# @KEEP
# @DROP
# @COM
# @UNC
```

**C / C++ / Java / Go / TypeScript / JavaScript / Zig (`//`)**:
```c
// @KEEP
// @DROP
// @COM
// @UNC
```

**Haskell / SQL / Lua (`--`)**:
```haskell
-- @KEEP
-- @DROP
-- @COM
-- @UNC
```

**PlantUML (`'`)**:
```plantuml
' @KEEP
' @DROP
' @COM
' @UNC
```

---

## Escopo por indentação

O escopo de uma diretiva de bloco é delimitado pela indentação:

1. Ao declarar uma diretiva em uma determinada coluna de indentação, aquele nível passa a operar sob o novo estado.
2. Todas as linhas seguintes com **indentação igual ou maior** pertencem a esse escopo (ou a blocos aninhados a ele) e herdam esse estado.
3. Quando a indentação **retorna a um nível anterior** (menor quantidade de espaços/tabs), o estado do nível mais interno encerra seu ciclo e o estado do nível pai volta a vigorar imediatamente.
4. Cada nível de indentação mantém seu próprio estado de forma independente.

### Exemplo

Entrada:

```python
def processar():
    # @DROP
    dados = carregar()
    validar(dados)

print("processamento concluído")
```

Saída:

```python
def processar():
print("processamento concluído")
```

> **Explicação**: A diretiva `# @DROP` está indentada com 4 espaços (dentro de `def processar():`). As linhas `dados = carregar()` e `validar(dados)` possuem 4 espaços e são removidas. A linha `print("processamento concluído")` possui indentação 0, retornando ao escopo externo (estado padrão `@KEEP`), sendo portanto mantida.

### Exemplo com escopos aninhados

Entrada:

```python
def calcular():
    # @DROP
    x = 10
    if True:
        # @KEEP
        y = 20
    z = 30
```

Saída:

```python
def calcular():
        y = 20
```

> **Explicação**: Dentro do bloco `# @DROP` (indentação 4), o bloco interno `if True:` declara `# @KEEP` (indentação 8), mantendo `y = 20`. Ao retornar para a indentação 4, a linha `z = 30` volta a estar sob o efeito do `# @DROP` e é removida.

---

## Estados no mesmo nível

Uma nova diretiva encontrada no mesmo nível de indentação **substitui** o estado anteriormente definido naquele nível.

Não é necessário nenhum marcador de fechamento: para alterar o modo de tratamento de um bloco seguinte, basta declarar a nova diretiva no mesmo nível.

### Exemplo

Entrada:

```python
class Servico:
    # @COM
    def metodo_antigo(self):
        return 1

    # @UNC
    # def metodo_novo(self):
    #     return 2

    # @KEEP
    def metodo_comum(self):
        return 3
```

Saída:

```python
class Servico:
    # def metodo_antigo(self):
        # return 1

    def metodo_novo(self):
        return 2

    def metodo_comum(self):
        return 3
```

> **Explicação**: Todas as diretivas estão no mesmo nível (4 espaços). Cada nova diretiva substitui o estado anterior para as funções subsequentes da classe.

---

## Operadores de bloco

Uma diretiva é classificada como **operador de bloco** quando o comentário contendo o marcador está **sozinho na linha** (ignorando espaços e o delimitador de comentário).

- Define o estado de processamento persistente para as linhas seguintes até a substituição ou redução da indentação.
- A própria linha contendo a diretiva de bloco nunca é emitida na saída final.

Exemplo:

```python
# @DROP
# Linha isolada de comentário -> Operador de bloco que afeta todo o bloco seguinte
```

---

## Operadores inline

Uma diretiva é classificada como **operador inline** quando aparece no **final de uma linha de código**.

- O operador inline afeta **exclusivamente aquela linha específica**.
- Não modifica nem sobrescreve o estado do escopo do bloco atual.
- O comentário da diretiva inline é automaticamente removido da linha resultante.

### Exemplo

Entrada:

```python
def exemplo():
    # @DROP
    print("removido 1")
    print("mantido")  # @KEEP
    print("comentado")  # @COM
    # print("descomentado")  # @UNC
    print("removido 2")
```

Saída:

```python
def exemplo():
    print("mantido")
    # print("comentado")
    print("descomentado")
```

> **Explicação**: O bloco está sob o estado `@DROP`. As diretivas inline `# @KEEP`, `# @COM` e `# @UNC` aplicam seus tratamentos apenas às suas respectivas linhas. As linhas sem diretiva inline (`removido 1` e `removido 2`) continuam seguindo o estado `@DROP` do bloco e são removidas.

---

## Compatibilidade com a sintaxe antiga

A sintaxe legada (`ADD!`, `DEL!`, `COM!`, `ACT!`) é mantida para compatibilidade retroativa (tanto em bloco quanto inline), sendo convertida para os novos estados correspondentes:

| Sintaxe Legada | Sintaxe Recomendada | Efeito |
| :--- | :--- | :--- |
| `ADD!` | `@KEEP` | Mantém o código |
| `DEL!` | `@DROP` | Remove o código |
| `COM!` | `@COM` | Comenta o código |
| `ACT!` | `@UNC` | Descomenta o código |

> **Nota**: Recomenda-se utilizar exclusivamente a sintaxe `@TAG` em novos projetos e materiais.

---

## Resumo

| Diretiva | Estado | Comportamento em Bloco | Comportamento Inline |
| :--- | :--- | :--- | :--- |
| `@KEEP` | Manter | Mantém todas as linhas do escopo | Mantém apenas a linha atual |
| `@DROP` | Remover | Remove todas as linhas do escopo | Remove apenas a linha atual |
| `@COM`  | Comentar | Comenta todas as linhas do escopo | Comenta apenas a linha atual |
| `@UNC`  | Descomentar | Descomenta as linhas do escopo | Descomenta apenas a linha atual |

- **Escopo**: Iniciado pela diretiva de bloco e finalizado quando a indentação diminui.
- **Substituição**: Uma nova diretiva no mesmo nível redefine o estado para as linhas seguintes.
- **Inline**: Afeta apenas uma linha e não altera a pilha de escopos.
- **Padrão**: Todo arquivo inicia no estado `@KEEP`.

---

## Uso típico

- **Material didático**: Manter o código da solução completa do professor e gerar automaticamente rascunhos (*drafts*) para alunos via `@DROP` ou `@COM`.
- **Exercícios com código inicial**: Usar `@UNC` para manter código comentado na solução do professor que deve aparecer ativo para o estudante.
- **Variações de código**: Alternar blocos de implementação dentro de um mesmo arquivo-fonte.
- **Ocultação de gabaritos**: Remoção de testes ou trechos privados antes da distribuição.


