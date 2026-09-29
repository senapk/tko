# mdpp - Guia Completo de Uso

O `mdpp` é um pré-processador de Markdown usado para atualizar blocos dinâmicos em arquivos `.md`.

No TKO, ele está disponível no comando:

```bash
tko tool mdpp [targets...] [--clean] [--quiet]
```

Se nenhum `target` for passado, o comportamento padrão é processar `README.md` no diretório atual.

---

## 1. Visão Geral da DSL

O `mdpp` oferece ações e diretivas estruturadas:

- `toc` — gera sumário hierárquico
- `toc-table` — gera sumário horizontal em tabela (alias legado: `toch`)
- `links PATH` — insere links para arquivos e diretórios
- `load PATH [OPTIONS]` — carrega e transforma conteúdo de arquivos
- `tests PATH [--limit N]` — apresenta os casos de teste como tabela
- `save` — grava blocos de código Markdown de volta em arquivos
- `clean` — limpa o conteúdo gerado, preservando os marcadores

---

## 2. Comando e Modos

### Modo RUN (padrão)

Atualiza e gera o conteúdo dinâmico entre os marcadores:

```bash
tko tool mdpp README.md
```

Ou em múltiplos arquivos:

```bash
tko tool mdpp README.md docs/aula.md docs/guia.md
```

### Modo CLEAN

Limpa os blocos gerados, mantendo apenas os marcadores iniciais e finais:

```bash
tko tool mdpp README.md --clean
```

---

## 3. Diretiva TOC

Gera uma lista hierárquica com base em cabeçalhos Markdown (`##`, `###`, ...).

Marcador:

```md
<!-- toc -->
<!-- toc -->
```

Exemplo:

```md
# Título Principal

<!-- toc -->
<!-- toc -->

## Seção 1
### Subseção 1.1
## Seção 2
```

Saída gerada:

```md
<!-- toc -->
- [Seção 1](#secao-1)
  - [Subseção 1.1](#subsecao-11)
- [Seção 2](#secao-2)
<!-- toc -->
```

Observações:
- Linhas de cabeçalho dentro de blocos de código (code fences) são ignoradas.
- Cabeçalhos que contenham `[]()` são ignorados no TOC.
- O cabeçalho de nível 1 (`# Título`) não entra na lista final de `toc`.

---

## 4. Diretiva TOC-TABLE

Gera uma tabela horizontal de links contendo exclusivamente cabeçalhos de nível 2 (`##`).

Marcador recomendado:

```md
<!-- toc-table -->
<!-- toc-table -->
```

*(Marcador legado `<!-- toch -->` continua sendo suportado como alias).*

Exemplo de saída:

```md
<!-- toc-table -->
[Seção 1](#secao-1) | [Seção 2](#secao-2)
-- | --
<!-- toc-table -->
```

Observação:
- Cabeçalhos `###` ou maiores não entram no `toc-table`.

---

## 5. Diretiva LINKS

Lista recursivamente arquivos e subpastas de um diretório com links relativos ao diretório do arquivo Markdown.

Sintaxe:

```md
<!-- links caminho/relativo -->
<!-- links -->
```

Exemplo:

```md
<!-- links exemplos -->
<!-- links -->
```

Com a estrutura de arquivos:

```text
README.md
exemplos/
    base.md
    avancado/
        lista.md
```

Saída gerada:

```md
<!-- links exemplos -->
- [base.md](exemplos/base.md)
- avancado
  - [lista.md](exemplos/avancado/lista.md)
<!-- links -->
```

Observações:
- Arquivos e diretórios ocultos (iniciados com `.`) são ignorados.
- Em modo `--clean`, o bloco retorna para `<!-- links exemplos -->\n<!-- links -->`.

---

## 6. Diretiva LOAD

Carrega o conteúdo de um arquivo para dentro do Markdown, aplicando opções e transformações opcionais.

Sintaxe base:

```md
<!-- load caminho/do/arquivo [OPCOES] -->
<!-- load -->
```

### 6.1 Opções de Modificação

- `--filter`: aplica o filtro de visibilidade do TKO (`@KEEP`, `@DROP`, `@COM`, `@UNC`).
- `--rm-comments`: remove linhas que contenham comentários de código no início (`#` para `.py`, `'` para `.puml`, `//` para outras linguagens). *(Alias legado: `--rmcom`)*.
- `--fenced`: envolve o conteúdo carregado em um bloco de código Markdown com linguagem inferida pela extensão do arquivo.
- `--fenced LANG`: envolve o conteúdo carregado em um bloco de código com a linguagem `LANG` especificada explicitamente (ex.: `--fenced py`, `--fenced cpp`, `--fenced ts`).

As opções `--extract`, `--tests`, `--tests-table` e `--tests-tio` não são
aceitas em `load`; use a diretiva `tests` para gerar tabelas de teste.

### 7. Diretiva TESTS

As diretivas de testes são independentes de `load`.

```md
<!-- tests cases.toml -->
<!-- tests -->
```

`tests` renderiza entrada e saída em uma tabela HTML. Sem `--limit`, todos os
casos são exibidos. Use `--limit N` para mostrar os primeiros `N` casos;
`--limit 0` também exibe todos.

### Ordem do Pipeline de Transformação

Independentemente da ordem em que as flags são escritas na diretiva, as transformações do `load` são executadas sempre na seguinte ordem fixa:

```text
extract
   ↓
filter
   ↓
remove comments (--rm-comments)
   ↓
fenced (--fenced / --fenced LANG)
```

Exemplo de equivalência:

```md
<!-- load src/solver.py --filter --rm-comments --fenced -->
```

possui o mesmo resultado que:

```md
<!-- load src/solver.py --fenced --rm-comments --filter -->
```

### 6.4 Exemplos de LOAD

#### Exemplo com `--fenced`:

Arquivo de origem (`src/app.py`):

```python
def soma(a: int, b: int) -> int:
    return a + b
```

Markdown:

```md
<!-- load src/app.py --fenced -->
<!-- load -->
```

Resultado:

````md
<!-- load src/app.py --fenced -->
```py
def soma(a: int, b: int) -> int:
    return a + b
```
<!-- load -->
````

#### Exemplo com `tests`:

Arquivo `tests.toml`:

```toml
[[tests]]
input = "1 2"
output = "3"

[[tests]]
input = "4 5"
output = "9"
```

Markdown:

```md
<!-- tests tests.toml -->
<!-- tests -->
```

Resultado:

````md
<!-- tests tests.toml --limit 1 -->
<table>...</table>
<!-- tests -->
````

---

## 7. Pipeline Completo do Arquivo

Ao processar um documento `.md` com `tko tool mdpp`, a ordem das diretivas executadas é:

1. `Toc.execute` (`<!-- toc -->`)
2. `TocTable.execute` (`<!-- toc-table -->` e `<!-- toch -->`)
3. `Tests.execute` (`<!-- tests ... -->`)
4. `Load.execute` (`<!-- load ... -->`)
5. `Links.execute` (`<!-- links ... -->`)

Se houver alterações no texto final, o arquivo Markdown é regravado de forma atômica/segura.

---

## 8. Uso Programático em Python

```python
from pathlib import Path
from tko.feno.mdpp import Mdpp, Action

# Executar transformações
Mdpp.update_file(Path("README.md"), Action.RUN)

# Limpar blocos gerados
Mdpp.update_file(Path("README.md"), Action.CLEAN)
```
