# Modo de Auditoria no TKO

O modo de auditoria registra snapshots periodicos dos arquivos que o aluno edita dentro da atividade.

Hoje o comportamento e:

- A auditoria so funciona enquanto o aluno estiver com `tko open` em execucao.
- Os snapshots sao gerados periodicamente pelo watcher do repositorio.
- Apenas arquivos dentro de `src/lang/...` da tarefa entram na auditoria.
- Cada snapshot e uma copia completa do arquivo, sem diff incremental.
- Os arquivos ficam em `.tko/audit/<source@task>/`.

## Criando um repositorio ja com auditoria ligada

Para criar um repositorio novo com auditoria ativada desde o inicio:

```bash
tko init --audit
```

Se quiser evitar a pergunta sobre repositorios remotos padrao:

```bash
tko init --audit --skip-remotes
```

Depois disso, a configuracao do repositorio passa a incluir a secao `audit` no arquivo `.tko/repository.yaml`.

## Ligando e desligando a auditoria em um repositorio existente

Dentro do repositorio, use:

```bash
tko config audit --on
```

Para desligar:

```bash
tko config audit --off
```

Para verificar o estado atual:

```bash
tko config audit
```

## Configurando o tempo entre snapshots

O tempo entre snapshots e controlado no arquivo:

```text
.tko/repository.yaml
```

Exemplo:

```yaml
audit:
	enabled: true
	interval_seconds: 60
```

Nesse exemplo, o watcher tenta salvar um novo snapshot a cada `60` segundos.

Observacoes:

- O valor deve ser inteiro positivo.
- Hoje nao existe ainda um comando `tko config audit --interval ...`.
- Para mudar o intervalo, edite o `repository.yaml` manualmente.

## Condicao necessaria: o aluno precisa manter o `tko open` rodando

A auditoria depende do watcher iniciado no comando:

```bash
tko open
```

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

Os nomes seguem o formato:

```text
YYYY-MM-DD_HH-MM-SS_nome-do-arquivo
```

Exemplo:

```text
2026-06-09_10-11-12_solver.py
2026-06-09_10-12-12_solver.py
2026-06-09_10-13-12_solver.py
```

Isso facilita comparar a evolucao do codigo ao longo do tempo.

## Como o professor analisa os arquivos com `fzf-preview`

O script `tools/fzf-preview.sh` pode ser usado para navegar pelos snapshots e comparar um arquivo com a versao anterior.

Exemplo entrando na pasta de auditoria de uma tarefa:

```bash
cd .tko/audit/fup@soma
../../../tools/fzf-preview.sh
```

Como os snapshots ficam ordenados pelo timestamp no nome, o preview mostra a diferenca entre um arquivo e o imediatamente anterior.

Atalhos uteis dentro do `fzf-preview`:

- `Alt+1`: diff com contexto normal.
- `Alt+2`: diff com contexto maior.
- `Alt+3`: diff completo.
- `Left` e `Right`: navegar entre entradas.

## Filtrando a analise para um unico arquivo

O script tambem aceita arquivos como parametros. Quando voce passa argumentos, ele usa apenas aqueles arquivos como entrada do `fzf`.

Exemplo para analisar apenas os snapshots do `solver.py`:

```bash
cd .tko/audit/fup@soma
../../../tools/fzf-preview.sh *_solver.py
```

Ou explicitando caminhos:

```bash
../../../tools/fzf-preview.sh \
	2026-06-09_10-11-12_solver.py \
	2026-06-09_10-12-12_solver.py \
	2026-06-09_10-13-12_solver.py
```

Se nenhum parametro for informado, o script usa todos os arquivos da pasta atual.

## Fluxo recomendado para avaliacao

Para o aluno:

1. Entrar no repositorio da disciplina.
2. Garantir que a auditoria esteja ativa.
3. Executar `tko open`.
4. Resolver a atividade com o `tko open` ainda aberto.

Para o professor:

1. Abrir a pasta `.tko/audit/<source@task>` do aluno.
2. Rodar `tools/fzf-preview.sh` nessa pasta.
3. Navegar pelos snapshots para observar a evolucao da solucao.
4. Comparar o ritmo das alteracoes com o historico esperado da resolucao.

## Resumo

Use o modo de auditoria quando quiser evidencias temporais do processo de construcao da resposta, e nao apenas o arquivo final entregue.

Os pontos principais sao:

- criar o repositorio com `tko init --audit` ou ligar depois com `tko config audit --on`;
- ajustar `audit.interval_seconds` no `.tko/repository.yaml`;
- manter o `tko open` rodando durante a resolucao;
- analisar os snapshots gerados com `tools/fzf-preview.sh`.
