# Marcadores e Modos de Avaliação

Uma tarefa é definida por uma linha Markdown com checkbox e link:

```md
- [ ] `@t1 gcs=332 eval=diff` [Implementar função soma](t1/README.md)
- [ ] `@t2 gcs=2 eval=none` [Ler material sobre listas](wiki/listas/README.md)
```

`@chave` e `eval` são obrigatórios. Os demais campos usam o valor padrão `1`.

## Indicadores

| Campo | Valores | Padrão | Descrição |
|---|---|---|---|
| `gain=` | inteiro de 1 a 3 | `1` | Utilidade pedagógica |
| `cost=` | inteiro de 1 a 6 | `1` | Custo/dificuldade |
| `size=` | inteiro de 1 a 3 | `1` | Tamanho da tarefa |
| `gcs=` | 1 a 3 dígitos | `1` | Forma compacta de `gain`, `cost`, `size` |
| `eval=` | `none`, `self`, `diff` | obrigatório | Modo de avaliação |

O XP de tarefas avaliáveis é `((gain + size) × cost) / 2`.

O sistema preserva o valor fracionário nos cálculos. A lista de tarefas o mostra truncado com uma casa decimal; somatórios de quests e skills são exibidos sem a parte fracionária.

## Modos

- `eval=none`: material de consulta; não gera XP, rascunho ou testes.
- `eval=self`: atividade com autoavaliação; gera rascunho para fontes externas.
- `eval=diff`: atividade com testes de entrada e saída; gera rascunho e testes para fontes externas.

`gcs` usa a ordem `gain`, `cost`, `size` e preenche as posições omitidas com
`1`: `gcs=3` equivale a `gain=3 cost=1 size=1`; `gcs=32` equivale a
`gain=3 cost=2 size=1`; e `gcs=312` equivale a `gain=3 cost=1 size=2`.
Os campos explícitos ainda são aceitos e prevalecem sobre seu componente em
`gcs`.

## Normalização pelo índice

`tko build index` valida links, inclui tarefas encontradas no diretório-base e renderiza cada linha no formato canônico com `eval` e `gcs`.

Os nomes e formatos antigos — `type=`, `hard=`, `xp=`, `tier=`, `eval=test` e tags colonadas — não são aceitos.
