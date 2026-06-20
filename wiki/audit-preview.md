# Visualizando timelines de auditoria

O comando `tko audit preview` abre uma timeline interativa no `fzf` para navegar por versões salvas de um arquivo e comparar cada snapshot com o snapshot anterior.

Ele substitui o fluxo manual:

```bash
tko audit unpack arquivo.jsonl
tools/fzf-preview.sh pasta-extraida
```

Na prática, o comando faz essa preparação automaticamente e abre o preview em uma única etapa.

## Onde os dados ficam

O TKO registra dois tipos diferentes de histórico dentro da pasta `.tko`.

### Execuções e testes

As execuções de código e testes ficam em:

```text
.tko/track/<source@task>/
```

Exemplo:

```text
.tko/track/fup@soma/
```

Essa pasta guarda o histórico associado às execuções da tarefa. Normalmente aparecem arquivos como:

```text
track.csv
solver.py.json
```

O `track.csv` registra timestamps e resultados de execução. Os arquivos `.json` guardam versões dos arquivos monitorados naquele fluxo de execução/teste.

### Auditoria periódica

Quando o módulo de auditoria está habilitado, os snapshots periódicos ficam em:

```text
.tko/audit/<source@task>/
```

Exemplo:

```text
.tko/audit/fup@soma/
```

Dentro dessa pasta, cada arquivo auditado tem um histórico próprio em `.jsonl`:

```text
solver.py.jsonl
main.cpp.jsonl
```

Esses arquivos `.jsonl` armazenam a sequência de versões capturadas pelo watcher de auditoria. O `tko audit preview` lê esses históricos, materializa snapshots temporários ordenados e mostra os diffs no `fzf`.

## Ferramentas externas

Para usar o preview com a melhor experiência, instale:

- `git`: usado para gerar diffs entre snapshots.
- `delta`: usado para renderizar diff colorido, lado a lado e com numeração.
- `bat`: usado para mostrar o primeiro snapshot com syntax highlight.
- `fzf`: usado para navegação interativa.

Exemplos de instalação:

```bash
# macOS
brew install git git-delta bat fzf

# Ubuntu/Debian
sudo apt install git fzf bat
# delta pode estar disponível como git-delta, dependendo da versão/distribuição.

# Fedora
sudo dnf install git git-delta bat fzf

# Arch
sudo pacman -S git git-delta bat fzf
```

Se `delta` ou `bat` não estiverem instalados, o preview ainda funciona, mas perde parte da formatação. O `fzf` é necessário para a interface interativa.

## Habilitando auditoria

Para ativar auditoria persistente no repositório:

```bash
tko audit set --on
```

Para definir um intervalo entre snapshots:

```bash
tko audit set --on --interval 20
```

Depois, rode o TKO normalmente mantendo o watcher ativo:

```bash
tko open
```

Também é possível iniciar a auditoria explicitamente em foreground:

```bash
tko audit init
```

Com intervalo específico:

```bash
tko audit init --interval 20
```

## Usando o preview

Para abrir a timeline padrão do repositório atual:

```bash
tko audit preview
```

Sem argumentos, o comando procura a pasta:

```text
.tko/audit/
```

Para abrir a auditoria de uma tarefa específica:

```bash
tko audit preview .tko/audit/fup@soma
```

Para abrir um arquivo `.jsonl` específico:

```bash
tko audit preview .tko/audit/fup@soma/solver.py.jsonl
```

Também é possível passar uma pasta já extraída ou arquivos comuns:

```bash
tko audit preview /tmp/tko-audit-unpack-abc123
tko audit preview snapshot-1.py snapshot-2.py snapshot-3.py
```

## Atalhos no preview

Dentro do `fzf`:

- `Left` e `Right`: navegam entre snapshots.
- `Up` e `Down`: rolam o painel de preview.
- `PgUp` e `PgDn`: rolam o preview por páginas.
- `Alt+1`: diff com contexto normal.
- `Alt+2`: diff com contexto maior.
- `Alt+3`: diff completo.

No topo do preview aparece:

```text
Elapsed=00:01:20 | Mode=diff | Shortcuts=...
```

`Elapsed` mostra o tempo entre o snapshot atual e o snapshot anterior. O primeiro snapshot aparece como `--:--:--`, porque ainda não há versão anterior para comparar.

## Comparando com o fluxo manual

O fluxo manual continua possível:

```bash
tko audit unpack .tko/audit/fup@soma/solver.py.jsonl
tools/fzf-preview.sh /tmp/tko-audit-unpack-...
```

Mas, para o uso comum, prefira:

```bash
tko audit preview .tko/audit/fup@soma/solver.py.jsonl
```

Esse comando evita a etapa manual de extração e abre diretamente a mesma ideia de timeline navegável.
