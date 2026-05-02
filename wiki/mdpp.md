# mdpp - Guia Completo de Uso

O `mdpp` e um pre-processador de Markdown usado para atualizar blocos dinamicos em arquivos `.md`.

No TKO, ele esta disponivel no comando:

```bash
tko tool mdpp [targets...] [--clean] [--quiet]
```

Se nenhum `target` for passado, o comportamento padrao e processar `README.md` no diretorio atual.

---

## 1. Comando e Modos

### Comando

```bash
tko tool mdpp README.md
```

Ou varios arquivos:

```bash
tko tool mdpp README.md docs/aula.md docs/guia.md
```

### Modo RUN (padrao)

Atualiza/gera conteudo entre marcadores.

```bash
tko tool mdpp README.md
```

### Modo CLEAN

Limpa os blocos gerados, mantendo apenas os marcadores.

```bash
tko tool mdpp README.md --clean
```

### Quiet

Existe a flag `--quiet` na CLI, mas no fluxo atual ela nao altera a saida do `mdpp`.

---

## 2. Diretiva TOC

Gera uma lista hierarquica com base em cabecalhos Markdown (`##`, `###`, ...).

Marcador:

```md
<!-- toc -->
<!-- toc -->
```

Exemplo:

```md
# Titulo

<!-- toc -->
<!-- toc -->

## Secao 1
### Subsecao 1.1
## Secao 2
```

Saida gerada:

```md
<!-- toc -->
- [Secao 1](#secao-1)
	- [Subsecao 1.1](#subsecao-11)
- [Secao 2](#secao-2)
<!-- toc -->
```

Observacoes:

- Linhas de cabecalho dentro de code fences sao ignoradas.
- Cabecalhos que contenham `[]()` sao ignorados no TOC.
- O `# Titulo` (nivel 1) nao entra na lista final de `toc`.

---

## 3. Diretiva TOCH

Gera uma tabela horizontal de links somente com cabecalhos de nivel 2 (`##`).

Marcador:

```md
<!-- toch -->
<!-- toch -->
```

Exemplo de saida:

```md
<!-- toch -->
[Secao 1](#secao-1) | [Secao 2](#secao-2)
-- | --
<!-- toch -->
```

Observacao:

- Cabecalhos `###` ou maiores nao entram no `toch`.

---

## 4. Diretiva LINKS

Lista arquivos e subpastas de um diretorio com links relativos ao diretorio do arquivo Markdown processado.

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

Com uma estrutura:

```text
README.md
exemplos/
	base.md
	avancado/
		lista.md
```

Saida:

```md
<!-- links exemplos -->
- [base.md](exemplos/base.md)
- avancado
	- [lista.md](exemplos/avancado/lista.md)
<!-- links -->
```

Observacoes:

- Entradas iniciadas com `.` (ocultas) sao ignoradas.
- Em `--clean`, o bloco volta para:

```md
<!-- links exemplos -->
<!-- links -->
```

---

## 5. Diretiva LOAD

Carrega conteudo de arquivo para dentro do Markdown, com opcoes de transformacao.

Sintaxe base:

```md
<!-- load caminho/do/arquivo -->
<!-- load -->
```

Exemplo simples:

```md
<!-- load src/main.py -->
<!-- load -->
```

### 5.1 Flags de LOAD

Use flags apos o caminho:

```md
<!-- load src/main.py --fenced --rmcom -->
<!-- load -->
```

Flags disponiveis:

- `--fenced`: envolve a saida em code fence com linguagem baseada na extensao do arquivo.
- `--extract TAG`: extrai somente o trecho entre `[[TAG]] ... [[TAG]]`.
- `--rmcom`: remove linhas de comentario no inicio da linha (apos espacos).
	- `.py` usa `#`
	- `.puml` usa `'`
	- outros usam `//`
- `--filter`: aplica o filtro do `tko.feno.filter` no conteudo.
- `--tests N`: interpreta arquivo como TOML de testes e gera tabela HTML Entrada/Saida.
	- `N = 0`: usa todos os casos
	- `N > 0`: limita aos primeiros `N`

### 5.2 Exemplo com --fenced

Entrada:

```md
<!-- load script.py --fenced -->
<!-- load -->
```

Saida:

~~~md
<!-- load script.py --fenced -->
```py
print('hello')
```

<!-- load -->
~~~

### 5.3 Exemplo com --extract

Arquivo origem:

```text
linha fora
[[demo]]
apenas este bloco
[[demo]]
linha fora
```

Markdown:

```md
<!-- load origem.txt --extract demo -->
<!-- load -->
```

Resultado: somente `apenas este bloco`.

### 5.4 Exemplo com --tests

Arquivo TOML:

```toml
[[tests]]
input = '''
1
2
'''
output = '''
3
'''

[[tests]]
input = '''
a
'''
output = '''
b
'''
```

Markdown:

```md
<!-- load tests.toml --tests 1 -->
<!-- load -->
```

Saida: uma tabela HTML com a primeira dupla Entrada/Saida.

Observacoes de LOAD:

- O caminho e relativo ao diretorio do `.md` processado.
- Se o arquivo nao existir, o bloco fica vazio e um warning e emitido.
- Em `--clean`, o bloco volta para:

```md
<!-- load ... -->
<!-- load -->
```

---

## 6. Diretiva SAVE

Permite salvar em arquivo o conteudo de um bloco fenced dentro do Markdown.

Sintaxe:

~~~md
[](save)[](caminho/do/arquivo.txt)
```text
conteudo a salvar
```
[](save)
~~~

Comportamento:

- Se arquivo nao existir, cria.
- Se existir e o conteudo for diferente, atualiza.
- Se for igual, nao regrava.

Observacao:

- O padrao de linguagem do fence aceita somente letras minusculas (`[a-z]*`).

---

## 7. Regras de Links e Anchors

No TOC/TOCH, os anchors sao gerados por normalizacao:

- remove prefixo de `#` do cabecalho
- converte para minusculas
- espaco/hifen viram `-`
- `_` e preservado
- caracteres nao alfanumericos (exceto `_` e `-`) sao removidos
- comentarios HTML e `[](...)` na linha sao removidos antes

Exemplo:

```text
### Title With <!-- comment -->
```

Anchor:

```text
title-with-
```

---

## 8. Pipeline Interno do Mdpp

Para cada arquivo `.md`, a ordem de processamento e:

1. `Toc.execute`
2. `Toch.execute`
3. `Load.execute`
4. `Links.execute`
5. `Save.execute`

Se o conteudo final mudar, o arquivo Markdown e regravado.

---

## 9. Erros e Warnings Comuns

- Arquivo alvo sem extensao `.md`:
	- `Warning: File ... is not a markdown file`
- Arquivo alvo inexistente:
	- `Warning: File ... not found`
- `--extract` sem valor:
	- `warning: missing value for --extract`
- `--tests` invalido:
	- `warning: invalid or missing integer for --tests`
- Flag desconhecida em `load`:
	- `warning: unrecognized tag '--alguma-coisa'`
- Arquivo de `load` inexistente:
	- `warning: file ... not found`

---

## 10. Exemplo Completo

~~~md
# Minha Tarefa

<!-- toc -->
<!-- toc -->

<!-- toch -->
<!-- toch -->

## Codigo

<!-- load src/solver.py --fenced --rmcom -->
<!-- load -->

## Casos

<!-- load tests.toml --tests 0 -->
<!-- load -->

## Materiais

<!-- links docs -->
<!-- links -->

[](save)[](docs/trecho.txt)
```text
Gerado automaticamente
```
[](save)
~~~

Rodando:

```bash
tko tool mdpp README.md
```

Limpando blocos gerados:

```bash
tko tool mdpp README.md --clean
```

---

## 11. Uso Programatico (Python)

```python
from pathlib import Path
from tko.feno.mdpp import Mdpp, Action

Mdpp.update_file(Path("README.md"), Action.RUN)
Mdpp.update_file(Path("README.md"), Action.CLEAN)
```

Retorno:

- `True` se o arquivo foi modificado
- `False` se nao houve alteracao ou ocorreu validacao que impediu processamento
