# Especificação de formatos

Este documento descreve os formatos de arquivo usados com mais frequência no TKO.

## Visão geral

Formatos principais:

1. `cases.tio` para casos de teste compactados.
2. pasta de testes com pares `*.in` e `*.sol`.
3. `languages.toml` para configuração de linguagens.
4. `README.md` de índice/trilha com metadados de quests e tasks.

## Formato `cases.tio`

Uso recomendado:

- distribuição compacta de testes
- versionamento simples
- conversão para outros formatos via `tko build`

Operações comuns:

```bash
tko build tests pasta cases.tio
tko build tests t.vpl cases.tio
```

Observação:

- O conteúdo é tratado pelo TKO como formato de casos de teste serializados.
- Para edição manual de casos, prefira extrair para pasta.

## Pasta de testes (`.in`/`.sol`)

Estrutura esperada:

- `00.in`, `00.sol`
- `01.in`, `01.sol`
- ...

Conversão a partir de `cases.tio`:

```bash
tko build tests pasta cases.tio
```

Personalização de nomes com `-p`:

```bash
tko build tests pasta cases.tio -p "in.@ out.@"
```

Exemplos de padrão:

- `@.in @.out`
- `in@ out@`

## `languages.toml`

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

Elementos comuns:

1. Cabeçalhos (`##`/`###`) representando quests.
2. Linhas de task com chave e metadados.

Exemplo de linha:

```md
- [ ]`@tres :1:main`[Soma de três inteiros](base/tres/README.md)
```

Semântica resumida:

- `@chave` identifica task
- `:1` define XP
- `:main` define trilha

## Referências relacionadas

- docs/REFERENCE.md
- docs/LANGUAGE_SUPPORT.md
- wiki/Criando-Tarefas-e-Testes.md
- wiki/Marcadores-e-Tipos.md
