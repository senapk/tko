# Modo de Auditoria no TKO

O modo de auditoria registra snapshots periodicos dos arquivos que o aluno edita dentro da atividade.

Hoje o comportamento e:

- A auditoria funciona enquanto houver um watcher ativo, seja pelo `tko open --audit`, pela auditoria persistente ligada com `tko audit on`, ou pelo monitor em foreground iniciado com `tko audit start`.
- Os snapshots sao gerados periodicamente pelo watcher do repositorio.
- Apenas arquivos dentro de `src/lang/...` da tarefa entram na auditoria.
- O historico de cada arquivo auditado e salvo em um arquivo `.jsonl`.
- Os arquivos ficam em `.tko/audit/<source@task>/`.

## Configurando o tempo entre snapshots

No modo explícito de auditoria, use `--interval` no comando:

```bash
tko audit start --interval 60
```

Se o parâmetro não for informado, o TKO usa o intervalo configurado no repositorio ou o valor padrão da ferramenta.

Observacoes:

- O valor deve ser inteiro positivo.

## Condicao necessaria: o aluno precisa manter o `tko open` rodando

A auditoria depende do watcher iniciado no comando:

```bash
tko open --audit
```

Tambem e possivel habilitar a auditoria persistente no repositorio e depois abrir o TKO normalmente:

```bash
tko audit on --interval 20
tko open
```

Se quiser iniciar auditoria explícita em foreground (com logs de snapshots no terminal), use `tko audit start`.

## Modo manual em foreground (`tko audit start`)

Quando quiser transparência total no terminal, use:

```bash
tko audit start
```

Esse comando inicia o watcher com auditoria ligada e fica em foreground mostrando os snapshots salvos, por exemplo:

```text
[audit] 10:11:12 fup@soma
```

Para encerrar, use `Ctrl+C`.

Tambem e possivel ajustar o intervalo apenas para a sessao manual:

```bash
tko audit start --interval 60
```

## Protecao contra multiplos watchers (lock)

Agora o sistema usa lock por repositorio em:

```text
.tko/watcher.lock
```

Com isso, se ja houver um `tko open`/`tko audit start` ativo no mesmo repositorio, uma segunda tentativa de iniciar watcher falha com aviso, evitando snapshots duplicados e redundancia de copia.

Se o aluno fechar o `tko open`, o watcher para e nenhum novo snapshot sera criado.

Na pratica, isso significa:

- o aluno deve abrir o repositorio com `tko open` antes de comecar a resolver;
- o `tko open` deve permanecer ativo durante a edicao;
- se o aluno editar os arquivos fora desse fluxo, essas alteracoes nao serao observadas pelo modo de auditoria.

## Onde os snapshots ficam salvos

Os snapshots sao gravados em:

```text
.tko/audit/<source@task>/
```

Exemplo:

```text
.tko/audit/fup@soma/
```

Dentro dessa pasta, cada arquivo auditado tem seu proprio historico:

```text
nome-do-arquivo.jsonl
```

Exemplo:

```text
solver.py.jsonl
main.cpp.jsonl
```

Esses arquivos armazenam a sequencia de versoes capturadas pelo watcher e permitem comparar a evolucao do codigo ao longo do tempo.

## Como o professor analisa os arquivos com `tko audit preview`

O comando `tko audit preview` abre uma timeline interativa para navegar pelos snapshots e comparar um arquivo com a versao anterior.

Exemplo entrando na pasta de auditoria de uma tarefa:

```bash
tko audit preview .tko/audit/fup@soma
```

Como cada arquivo `.jsonl` guarda as versoes em ordem temporal, o preview mostra a diferenca entre um snapshot e o imediatamente anterior.

Atalhos uteis dentro do preview:

- `Alt+1`: diff com contexto normal.
- `Alt+2`: diff com contexto maior.
- `Alt+3`: diff completo.
- `Left` e `Right`: navegar entre entradas.

## Filtrando a analise para um unico arquivo

O comando tambem aceita arquivos `.jsonl` como parametros.

Exemplo para analisar apenas os snapshots do `solver.py`:

```bash
tko audit preview .tko/audit/fup@soma/solver.py.jsonl
```

Se nenhum parametro for informado, o comando procura a auditoria do repositorio atual.

## Fluxo recomendado para avaliacao

Para o aluno:

1. Entrar no repositorio da disciplina.
2. Garantir que a auditoria esteja ativa, com `tko audit on` ou `tko open --audit`.
3. Executar `tko open`, se a auditoria persistente estiver habilitada.
4. Resolver a atividade com o `tko open` ainda aberto.

Para o professor:

1. Abrir a pasta `.tko/audit/<source@task>` do aluno.
2. Rodar `tko audit preview` nessa pasta.
3. Navegar pelos snapshots para observar a evolucao da solucao.
4. Comparar o ritmo das alteracoes com o historico esperado da resolucao.

## Resumo

Use o modo de auditoria quando quiser evidencias temporais do processo de construcao da resposta, e nao apenas o arquivo final entregue.

Os pontos principais sao:

- iniciar auditoria explicitamente com `tko audit start` (ou `tko audit start --interval ...`);
- habilitar auditoria persistente com `tko audit on`;
- manter o processo de auditoria ativo durante a resolucao;
- analisar os snapshots gerados com `tko audit preview`.
