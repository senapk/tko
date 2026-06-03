# Build index - manter e atualizar indices

Este guia explica o comando:

    tko build index INDEX_MD BASE_DIR

Exemplo:

    tko build index README.md base

Onde:

- INDEX_MD: arquivo markdown de indice (lista de tarefas).
- BASE_DIR: pasta com as subpastas das tarefas (cada uma com README.md).

## O que o comando faz

O comando sincroniza o indice com o conteudo real de BASE_DIR.

Fluxo principal:

1. Varre BASE_DIR e coleta todos os README.md de tarefas diretas.
2. Le o INDEX_MD linha por linha e interpreta entradas de tarefa.
3. Remove do indice entradas locais cujo README.md nao existe mais.
4. Detecta pastas de tarefa existentes em BASE_DIR que nao estao no indice.
5. Adiciona essas entradas faltantes na secao de quest padrao (sandbox).
6. Regrava o arquivo com alinhamento de chaves.

## Como ele adiciona entradas faltantes

Uma entrada e considerada faltante quando:

- existe BASE_DIR/NOME_DA_TAREFA/README.md
- mas a chave @NOME_DA_TAREFA nao aparece nas tarefas do indice

Quando isso acontece, o comando gera automaticamente uma linha de tarefa usando:

- chave: nome da pasta da tarefa
- titulo: primeiro cabecalho de nivel 1 (# Titulo) do README.md da tarefa
- link: caminho relativo para README.md

Se nao existir secao iniciando com:

    ## sandbox

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

    tko build index README.md base --load

Salvar titulo do indice para o README da tarefa:

    tko build index README.md base --save

Resumo:

- --load: atualiza o titulo da linha no indice.
- --save: atualiza o cabecalho # no README da tarefa.

## Boas praticas

- Rode o comando sempre que criar, renomear ou remover tarefas em BASE_DIR.
- Mantenha uma secao sandbox para receber entradas auto-geradas.
- Revise o diff apos rodar para confirmar ordem e agrupamento desejados.

## Exemplo de ciclo de manutencao

1. Criou pasta nova base/nova_tarefa/README.md.
2. Removeu pasta antiga base/tarefa_antiga/.
3. Executou:

    tko build index README.md base

4. Resultado esperado:
- Entrada de @nova_tarefa adicionada.
- Linha da tarefa_antiga removida se o README nao existir.
