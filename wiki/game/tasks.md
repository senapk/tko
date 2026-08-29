# Marcadores e Tipos de Tarefas

Uma tarefa é definida em uma linha markdown com checkbox e link:

```md
- [ ] `@t1 gain=9 hard=3 size=2 type=make eval=test` [Implementar função soma](t1/README.md)
- [ ] `@t2 gain=5 type=read` [Ler artigo sobre listas](https://exemplo.com/material)
```

O identificador `@chave` é obrigatório. Os demais campos podem ser omitidos e assumem valores padrão.


## As 3 Dimensões Ortogonais de Atividade

Cada atividade possui 3 indicadores independentes:

1. **`gain`** (antigo `xp`): Valor pedagógico / utilidade da tarefa no curso.
2. **`hard`** (antigo `tier`): Nível de dificuldade / complexidade intelectual (1 a 4).
3. **`size`**: Tamanho / extensão da atividade (volume de trabalho/código).

`gain`, `hard` e `size` são ortogonais porque nem tudo que é difícil ou longo é o foco principal da disciplina, e vice-versa.


## Campos Suportados

| Campo | Valores possíveis | Padrão | Descrição |
|-------|-------------------|--------|-----------|
| `@chave` | `@t1`, `@foo`, ... | obrigatório | Identificador único da tarefa |
| `gain=` | números inteiros (≥ 1) | `1` | Utilidade / ganho pedagógico |
| `hard=` | números inteiros (1 a 4) | `1` | Dificuldade / complexidade |
| `size=` | números inteiros (≥ 1) | `1` | Tamanho / extensão da tarefa |
| `type=` | `make`, `read` | `make` | Tipo da tarefa (produção ou leitura) |
| `eval=` | `test`, `self` | `test` (make) / `self` (read) | Modo de avaliação |


## Tipos de Atividade

- **`type=make`**: Tarefa de produção/programação.
  - Pode apontar para uma pasta local (`base/soma/README.md`) ou para uma URL do GitHub (`https://github.com/.../README.md`).
  - No caso de URLs do GitHub, o TKO gerencia a clonagem/cache remoto para que o aluno possa resolver e testar localmente.
- **`type=read`**: Tarefa de consumo/leitura.
  - Pode apontar para documentação local (`wiki/git/README.md`) ou para links externos HTTP/HTTPS (artigos, vídeos, etc.).


## Modos de Avaliação

- **`eval=test`**: Avaliação automática por testes (casos em `tests.toml`, `.tio` ou blocos de teste no próprio `README.md`).
- **`eval=self`**: Autoavaliação pelo próprio aluno.


## Papel do `tko build index`

O comando `tko build index README.md <pasta_base>` sincroniza e formata o índice:

1. **Validação de Links Locais**: Detecta se alguma tarefa aponta para um README local que não existe mais, avisa o usuário e remove a entrada inválida.
2. **Auto-indexação de Novas Pastas**: Inspeciona a pasta base (ex: `base/`) e, se houver pastas de tarefas que ainda não estão no índice, avisa e adiciona automaticamente na seção correspondente.
3. **Alinhamento Visual (Padding)**: Formata as tarefas alinhando `@chave` e tags em colunas padronizadas, garantindo que os colchetes dos títulos fiquem perfeitamente alinhados verticalmente.
4. **Preservação de Escolhas**: O indexador não sobrescreve os tipos `type` ou modos de avaliação `eval` definidos pelo autor.


## Sintaxe Antiga e Compatibilidade

A sintaxe antiga com `xp=`, `tier=` e `:` ainda é aceita pelo parser na leitura por compatibilidade, sendo normalizada na execução do `tko build index`:

```md
- [ ] `@t1 xp=10 tier=2` [Implementar função soma](t1/README.md)
```
