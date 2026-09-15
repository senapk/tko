# Especificação de formatos

Este documento descreve os formatos de arquivo usados com mais frequência no TKO.

## Visão geral

Formatos principais:

1. `tests.toml` para casos de teste compactados.
2. pasta de testes com pares `*.in` e `*.sol`.
3. `programming-languages.toml` para configuração de linguagens.
4. `README.md` de índice/trilha com metadados de quests e tasks.

## Formato `tests.toml`

Uso recomendado:

- distribuição compacta de testes
- versionamento simples
- conversão para outros formatos via `tko tool convert-tests`

Operações comuns:

```bash
tko tool convert-tests pasta -o tests.toml
tko tool convert-tests t.vpl -o tests.toml
```

Observação:

- O conteúdo é tratado pelo TKO como formato de casos de teste serializados.
- Para edição manual de casos, prefira extrair para pasta.

## Pasta de testes (`.in`/`.sol`)

Estrutura esperada:

- `00.in`, `00.sol`
- `01.in`, `01.sol`
- ...

Conversão a partir de `tests.toml`:

```bash
tko tool convert-tests pasta -o tests.toml
```

Personalização de nomes com `-p`:

```bash
tko tool convert-tests pasta -o tests.toml --read-pattern "in.@ out.@"
```

Exemplos de padrão:

- `@.in @.out`
- `in@ out@`

## `programming-languages.toml`

Define build/run/draft por linguagem.

Exemplo mínimo:

```toml
[rs]
build_cmd = '''
rustc {files} -o {output}
'''
run_cmd = '''
{output}
'''
draft = '''
fn main() {
    println!("Hello, World!");
}
'''
```

Placeholders:

- `{files}`
- `{output}`
- `{cache}`
- `{main}`
- `{entry}`

## Índice de tarefas em `README.md`

O README de trilha funciona como índice de quests e tasks.

No início do arquivo, a fonte pode declarar as variáveis usadas para pontuar suas
próprias tarefas e a fórmula de XP:

```md
---
var: [value, depth, scope]
xp: "(value * depth * scope) ** (1 / 3)"
---
```

`var` e `xp` pertencem à fonte. Cada task avaliável fornece os valores como
`value=3 depth=2 scope=1`; o TKO calcula o XP durante o parsing e retém apenas
esse resultado para a gamificação. A fórmula aceita números, variáveis declaradas,
`+`, `-`, `*`, `/`, `**` e parênteses. Fontes sem esses dois campos recebem XP zero
durante a migração. Tarefas `eval=none` continuam com XP zero e não precisam das
variáveis.

Elementos comuns:

1. Cabeçalhos (`##`/`###`) representando quests.
2. Linhas de task com chave e metadados.

Exemplo de linha:

```md
- [ ] `@tres eval=diff value=2 depth=1 scope=1` [Soma de três inteiros](labs/tres/README.md)
```

Semântica resumida:

- o caminho do README identifica a tarefa, por exemplo `labs/tres`; `@chave` é
  metadado legado usado pela [migração dos dados](TASK_DATA_MIGRATION.md);
- `[x]` marca a tarefa como referência para a meta da quest; `[ ]` marca uma alternativa;
- `eval` é obrigatório e pode ser `none`, `self` ou `diff`;
- os pares `nome=valor` são variáveis transitórias declaradas por `var`;
- o XP é definido pela fórmula `xp` da fonte; `eval=none` sempre possui XP zero;
- tarefas externas são materializadas; `eval=none` cria apenas o material,
  `eval=self` cria também um draft, e `eval=diff` cria código e testes;
- `eval=self` usa feedback manual; `eval=diff` usa testes por entrada e saída;
- somente `eval=none` não oferece autoavaliação; as demais usam `src/feedback.toml`;
- o link deve apontar para um `README.md` local ou para um `README.md` no GitHub.

A meta da quest é calculada pela soma do XP das tarefas de referência avaliáveis. Se
nenhuma tarefa for marcada como referência, todas as tarefas avaliáveis entram no cálculo.
Local ou externo altera apenas a forma de obter a pasta materializada, não o contrato
da atividade.

## Referências relacionadas

- [Referência rápida da CLI](REFERENCE.md)
- [Suporte a linguagens](LANGUAGE_SUPPORT.md)
- [Guia para criar repositórios de tarefas](../wiki/Criando-Atividades.md)
- [Criando testes e conversões](../wiki/Criando-Tarefas-e-Testes.md)
- [Marcadores e tipos de tarefas](../wiki/game/tasks.md)
