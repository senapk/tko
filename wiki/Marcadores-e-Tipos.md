# Tipos e Propriedades de Tarefas (Tasks)

Uma tarefa (task) é definida em uma linha markdown, usando o modelo chave-valor:

```md
- [ ] key=@t1 xp=10 type=task path=main eval=test loss=part [Título](pasta/README.md)
- [ ] @t2 xp=5 type=read path=side eval=self loss=free [Título](pasta/README.md)
```

**Campos suportados:**

| Campo  | Valores possíveis         | Padrão      | Descrição                                                        |
|--------|--------------------------|-------------|------------------------------------------------------------------|
| key    | @t1, @foo, ...           | — (obrig.)  | Identificador único da tarefa                                    |
| xp     | 1, 5, 10, ...            | 1           | Pontuação/XP da tarefa                                           |
| type   | task, read               | task        | Tipo: task (produção), read (consumo)                            |
| path   | main, side               | main        | Categoria/trilha: main (recomendada), side (opcional)            |
| eval   | test, self               | test/read   | Modo de avaliação: test (automática por testes), self (autoavaliação) |
| loss   | zero, part, free         | part/task   | Penalidade por consulta: zero (perde tudo), part, free (sem perda)|

**Notas:**
- Apenas key é obrigatória.
- Campos podem aparecer em qualquer ordem.
- Campos não obrigatórios assumem valores padrão.
- Sintaxe antiga (:main, :side, :test, etc) ainda é suportada por compatibilidade, mas recomenda-se o novo formato.

## Valores padrão

- xp=1
- type=task
- se type=task
  - eval=test
  - loss=part
- se type=read
  - eval=self
  - loss=free

## Exemplos

```md
- [ ] key=@t1 xp=10 type=task path=main eval=test loss=part [Implementar função soma](t1/README.md)
- [ ] @t2 xp=5 type=read path=side eval=self loss=free [Ler artigo sobre listas](t2/README.md)
```

## Significados e interações

- **type=task**: tarefa de produção (programar, escrever, pesquisar)
- **type=read**: tarefa de consumo (ler, assistir, explorar)
- **path=main**: tarefa recomendada, mas não obrigatória (pode ser substituída por outra side de mesmo valor)
- **path=side**: tarefa opcional
- **eval=test**: avaliação automática por testes
- **eval=self**: autoavaliação pelo próprio aluno
- **loss=zero**: consulta proibida, nota zero se consultar
- **loss=part**: consulta permitida, mas afeta a nota
- **loss=free**: consulta permitida e não afeta a nota

## Regras

- Campos podem ser omitidos; valores padrão serão assumidos.
- O campo key pode ser definido como key=@t1 ou apenas @t1 para compatibilidade.
- Campos não obrigatórios assumem valores padrão.

## Recomendações

- Prefira o modelo chave-valor para clareza e manutenção futura.
- Use nomes de campos e valores em minúsculas.
- Evite misturar sintaxe antiga e nova na mesma linha.
