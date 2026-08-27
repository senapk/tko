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

- `--extract TAG`: extrai exclusivamente o trecho delimitado por `[[TAG]] ... [[TAG]]`. Suporta múltiplas linhas e tags comentadas (ex.: `// [[TAG]]`, `# [[TAG]]`).
- `--filter`: aplica o filtro de visibilidade do TKO (`@KEEP`, `@DROP`, `@COM`, `@UNC`).
- `--rm-comments`: remove linhas que contenham comentários de código no início (`#` para `.py`, `'` para `.puml`, `//` para outras linguagens). *(Alias legado: `--rmcom`)*.
- `--fenced`: envolve o conteúdo carregado em um bloco de código Markdown com linguagem inferida pela extensão do arquivo.
- `--fenced LANG`: envolve o conteúdo carregado em um bloco de código com a linguagem `LANG` especificada explicitamente (ex.: `--fenced py`, `--fenced cpp`, `--fenced ts`).

### 6.2 Opções de Geração de Testes (TOML)

Para arquivos TOML de testes, o `mdpp` oferece duas ações de formato independentes e mutuamente exclusivas:

- `--tests-tio`: gera todos os casos de teste no formato TIO padrão (`>>>>>>>> INSERT ... ======== EXPECT ... <<<<<<<< FINISH`).
- `--tests-tio N`: gera os primeiros `N` casos de teste no formato TIO (`N > 0`; `N = 0` gera todos).
- `--tests-table`: gera todos os casos de teste formatados como tabela Markdown/HTML (`<table>`).
- `--tests-table N`: gera os primeiros `N` casos de teste formatados como tabela Markdown/HTML (`N > 0`; `N = 0` gera todos).

> **Atenção:** As opções `--tests-tio` e `--tests-table` são mutuamente exclusivas. Não utilize ambas no mesmo bloco `load`.

#### Compatibilidade Legada de Testes:
- `--tests` e `--tests N` são aceitos como aliases legados para `--tests-tio` e `--tests-tio N`.
- A antiga combinação `--tests --table` está depreciada e mapeia para `--tests-table` com aviso de depreciação.

### 6.3 Ordem do Pipeline de Transformação

Independentemente da ordem em que as flags são escritas na diretiva, as transformações do `load` são executadas sempre na seguinte ordem fixa:

```text
extract
   ↓
filter
   ↓
remove comments (--rm-comments)
   ↓
tests (--tests-tio OU --tests-table)
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

#### Exemplo com `--extract` e `--fenced`:

Arquivo de origem (`src/app.py`):

```python
# [[solution]]
def soma(a: int, b: int) -> int:
    return a + b
# [[solution]]
```

Markdown:

```md
<!-- load src/app.py --extract solution --fenced -->
<!-- load -->
```

Resultado:

````md
<!-- load src/app.py --extract solution --fenced -->
```py
def soma(a: int, b: int) -> int:
    return a + b
```
<!-- load -->
````

#### Exemplo com `--tests-tio`:

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
<!-- load tests.toml --tests-tio 1 -->
<!-- load -->
```

Resultado:

````md
<!-- load tests.toml --tests-tio 1 -->
```py
>>>>>>>> INSERT
1 2
======== EXPECT
3
<<<<<<<< FINISH
```
<!-- load -->
````

---

## 7. Diretiva SAVE

Permite extrair o conteúdo de um bloco Markdown fenced e salvá-lo em arquivo no disco.

Sintaxe:

~~~md
[](save)[](caminho/do/arquivo.txt)
```text
conteúdo a salvar
```
[](save)
~~~

Comportamento:
- Se o arquivo não existir, é criado.
- Se o arquivo existir e o conteúdo for diferente, é atualizado.
- Se o conteúdo já for idêntico, a gravação é ignorada.
- Caminhos relativos são resolvidos a partir do diretório do arquivo `.md`.

---

## 8. Pipeline Completo do Arquivo

Ao processar um documento `.md` com `tko tool mdpp`, a ordem das diretivas executadas é:

1. `Toc.execute` (`<!-- toc -->`)
2. `TocTable.execute` (`<!-- toc-table -->` e `<!-- toch -->`)
3. `Load.execute` (`<!-- load ... -->`)
4. `Links.execute` (`<!-- links ... -->`)
5. `Save.execute` (`[](save)...[](save)`)

Se houver alterações no texto final, o arquivo Markdown é regravado de forma atômica/segura.

---

## 9. Uso Programático em Python

```python
from pathlib import Path
from tko.feno.mdpp import Mdpp, Action

# Executar transformações
Mdpp.update_file(Path("README.md"), Action.RUN)

# Limpar blocos gerados
Mdpp.update_file(Path("README.md"), Action.CLEAN)
```
