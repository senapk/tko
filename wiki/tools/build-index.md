# Build index - manter e atualizar indices

Este guia explica o comando:

    tko index build INDEX_MD --from SOURCE [--from SOURCE...]

Exemplo:

    tko index build README.md --from labs --from wiki

Onde:

- INDEX_MD: arquivo markdown de indice (lista de tarefas).
- SOURCE: pasta com as subpastas das tarefas (cada uma com README.md). A opção
  pode ser repetida para várias fontes.

## O que o comando faz

O comando sincroniza o indice com o conteudo real de todas as fontes.

Fluxo principal:

1. Varre cada SOURCE e coleta todos os README.md de tarefas diretas.
2. Le o INDEX_MD linha por linha e interpreta entradas de tarefa.
3. Remove do indice entradas locais cujo README.md nao existe mais.
4. Detecta tarefas existentes em qualquer SOURCE que nao estao no indice.
5. Adiciona entradas faltantes em uma secao por fonte.
6. Atualiza `xpgoal` das quests quando houver tarefas marcadas como referencia.
7. Regrava o arquivo com alinhamento de chaves.

## Como ele adiciona entradas faltantes

Uma entrada e considerada faltante quando:

- existe SOURCE/NOME_DA_TAREFA/README.md
- mas o caminho SOURCE/NOME_DA_TAREFA nao aparece nas tarefas do indice

Quando isso acontece, o comando gera automaticamente uma linha de tarefa usando:

- chave: nome da pasta da tarefa
- titulo: primeiro cabecalho de nivel 1 (# Titulo) do README.md da tarefa
- link: caminho relativo para README.md

Se nao existir secao com o nome da fonte, por exemplo:

    ## labs

ela e criada e as novas entradas sao inseridas nela.

## Como ele remove links inexistentes

Ao ler o indice, para cada tarefa local (link de arquivo):

- se o caminho do README.md nao existir no disco, a linha e descartada
- no final, o indice e salvo sem essas linhas quebradas

Importante:

- Isso vale para tarefas locais (links de arquivo).
- Linhas com URL externa nao sao removidas por esse criterio.

## Sincronizacao de titulos

O comando possui duas opcoes para sincronizar titulo entre indice e README da tarefa.

Carregar titulo do README para o indice:

    tko index build README.md --from labs --from wiki --load

Salvar titulo do indice para o README da tarefa:

    tko index build README.md --from labs --from wiki --save

Resumo:

- --load: atualiza o titulo da linha no indice.
- --save: atualiza o cabecalho # no README da tarefa.

## Calculando `xpgoal` com `[x]`

O `xpgoal` de uma quest pode ser informado manualmente no cabecalho:

```md
## Vetores <!-- key=@vetores xpgoal=12 min=70% -->
```

Quando voce nao quiser contar esse total manualmente, marque com `[x]` as tarefas que fazem parte da meta esperada daquela quest:

```md
## Vetores <!-- key=@vetores min=70% -->

- [x] `@soma     gain=2 cost=1 size=1 eval=diff` [Soma](labs/soma/README.md)
- [x] `@media    gain=3 cost=1 size=1 eval=diff` [Media](labs/media/README.md)
- [ ] `@desafio  gain=5 cost=3 size=2 eval=diff` [Desafio](labs/desafio/README.md)
```

Ao executar:

```bash
tko index build README.md --from labs --from wiki
```

o indexer soma o `gain` das tarefas marcadas com `[x]` e grava esse valor em `xpgoal`:

```md
## Vetores <!-- @vetores xpgoal=5 min=70% -->
```

Regras importantes:

- Apenas tarefas marcadas com `[x]` entram nessa soma.
- A soma usa o campo `gain`, nao `cost` nem `size`.
- Se a quest ja tiver `xpgoal`, o valor sera substituido pela soma dos `[x]`.
- Se nenhuma tarefa da quest estiver marcada com `[x]`, o `xpgoal` existente nao e recalculado por essa regra.
- Em tempo de execucao, se uma quest ficar sem `xpgoal`, o TKO usa a soma de todas as tasks da quest como meta disponivel.

## Boas praticas

- Rode o comando sempre que criar, renomear ou remover tarefas em qualquer SOURCE.
- Use `[x]` para marcar as tarefas que contam para a meta principal da quest, deixando tarefas extras ou desafios com `[ ]`.
- Mantenha uma secao sandbox para receber entradas auto-geradas.
- Revise o diff apos rodar para confirmar ordem e agrupamento desejados.

## Exemplo de ciclo de manutencao

1. Criou pasta nova labs/nova_tarefa/README.md.
2. Criou pasta nova wiki/nova_referencia/README.md.
3. Removeu pasta antiga labs/tarefa_antiga/.
3. Executou:

    tko index build README.md --from labs --from wiki

4. Resultado esperado:
- Entradas de labs/nova_tarefa e wiki/nova_referencia adicionadas.
- Linha da tarefa_antiga removida se o README nao existir.
