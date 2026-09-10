# Marcadores e Modos de Avaliação

Uma tarefa é definida por uma linha Markdown com checkbox e link:

```md
---
var: [value, depth]
xp: "value * depth"
---

- [ ] `@t1 value=3 depth=2 eval=diff` [Implementar função soma](t1/README.md)
- [ ] `@t2 eval=none` [Ler material sobre listas](wiki/listas/README.md)
```

`@chave` e `eval` são obrigatórios. Os demais campos usam o valor padrão `1`.

## Variáveis e XP

`var` declara os nomes das variáveis que a fonte usa e `xp` declara sua fórmula.
Os significados pedagógicos desses nomes pertencem à própria fonte; o TKO só aceita
valores numéricos e calcula o XP final. A task não retém as variáveis após o parsing.
`eval=` continua sendo o único campo operacional fixo.

O sistema preserva o valor fracionário nos cálculos. A lista de tarefas o mostra truncado com uma casa decimal; somatórios de quests e skills são exibidos sem a parte fracionária.

## Modos

- `eval=none`: material de consulta; não gera XP, rascunho ou testes.
- `eval=self`: atividade com autoavaliação; gera rascunho para fontes externas.
- `eval=diff`: atividade com testes de entrada e saída; gera rascunho e testes para fontes externas.

## Normalização pelo índice

`tko build index` valida links, inclui tarefas encontradas no diretório-base e preserva
o front matter e as variáveis existentes; ele não converte métricas em um formato
global nem inventa valores para novas tarefas.

Fontes sem `var` e `xp` recebem XP zero durante a migração.
