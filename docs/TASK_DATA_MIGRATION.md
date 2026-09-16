# Migração dos dados de tarefas

As identidades persistidas passam a usar a chave completa da atividade no índice,
como `curso@plan/rotulo`. O prefixo é o nome da fonte; o restante vem do caminho
relativo do README da atividade. Não existe equivalência implícita entre `rotulo`,
`labs/rotulo` e `plan/rotulo`.

Workspaces com logs, versões ou estado de seleção sem a versão desse formato
precisam passar pela ferramenta antes de serem abertos. Workspaces novos recebem
o marcador automaticamente na primeira gravação. O marcador `.tko/task-format.json`
é independente da versão da configuração e do campo `v` dos eventos.
O formato atual é a versão 5. Ele usa um histórico unificado em
`.tko/history/<fonte>/<atividade>/`, com snapshots em `files/` e eventos em
`events.jsonl`. Eventos `execution` podem conter o resultado dos testes; eventos
`audit` registram apenas alterações observadas. Quem já executou uma migração
anterior deve executar o comando novamente.

## Aplicar ou simular

Feche os processos TKO que estejam usando o workspace. A operação é offline e
trabalha em um workspace por vez:

```sh
tko tool migrate /caminho/do/workspace
```

Sem opções, o comando aplica a migração após validá-la. Os repositórios dos
alunos já são versionados no Git, portanto a ferramenta não cria uma cópia local
dos dados. Para
revisar correspondências, arquivos afetados e erros sem escrever no workspace,
use `--dry-run`. Sem path, o comando valida e usa o diretório atual.
Também é possível selecionar o diretório com `tko -C /caminho/do/workspace tool migrate`.

```sh
tko tool migrate /caminho/do/workspace --dry-run
```

O mapa automático usa o caminho atual e o antigo `@rotulo`, quando este ainda
está presente na linha do índice. Também reconhece a convenção `labs/`: para uma
referência `poo@animal`, preserva essa chave se ela existir no índice. Caso não
exista, verifica a entrada exata `poo@labs/animal` e a associa automaticamente.
A regra vale para logs diários, `history.csv`, estado salvo e pastas de `track`
e `audit`, mesmo sem `@animal` no índice e sem diretórios de histórico presentes.
Correspondências legadas concorrentes continuam exigindo um mapa explícito;
caminhos de outras fontes ou outros prefixos não são inferidos pelo último
nome da pasta. Para fontes Git, lê o
índice já materializado no workspace; não faz clone, download ou atualização de
cache.

Se nenhuma dessas regras resolver o rótulo, o migrador o move para
`fonte@labs/rotulo` e continua a operação, incluindo as pastas de atividade,
`track` e `audit`. Quando o rótulo apontar para várias atividades, forneça um
arquivo JSON:

```json
{
  "curso@rotulo": "curso@plan/rotulo",
  "outro@exercicio": "outro@modulo/atividade"
}
```

```sh
tko tool migrate /caminho/do/workspace --map mapa.json
tko tool migrate /caminho/do/workspace --map mapa.json --dry-run
```

Destinos explícitos podem representar atividades arquivadas ou fontes cujo índice
não está disponível offline. Uma correspondência de uma chave para ela mesma
confirma que essa identidade deve ser preservada. O mapa não pode trocar a fonte,
renomear uma atividade canônica existente, formar ciclos ou conter cadeias de
renomeações. Logs muito antigos sem fonte podem receber a chave completa pelo mapa.

## O que é preservado

A ferramenta atualiza as chaves nos logs diários e no `history.csv`, as referências
de seleção/fixação/expansão na configuração YAML ou TOML e combina as pastas antigas
de `track` e `audit` no histórico unificado. Reconhece tanto `track/fonte@rotulo`
quanto `track/fonte/rotulo`, com a mesma regra para `audit`. Campos desconhecidos dos logs diários, versões dos eventos,
timestamps e bytes dos snapshots são preservados. Configurações alteradas podem
ser reformatadas, preservando seus campos.

Configurações antigas são convertidas para `.tko/repository.toml` durante a mesma
aplicação: fontes e fonte de autoria passam para `[profile]`, preferências para
`[preferences]`, seleção para `[state]` e auditoria para `[profile.audit]`.
O arquivo `repository.yaml` é removido depois da conversão. Se YAML e TOML
coexistirem, o TOML tem precedência.
Campos desconhecidos são preservados quando representáveis em TOML; valores
`null` desconhecidos bloqueiam a conversão, pois TOML não possui esse valor.
O carregamento normal não converte mais configurações antigas.

O histórico de execuções `track.csv` é convertido para `events.jsonl`, com um objeto
por linha contendo `timestamp`, `type: "execution"`, `result` e `files`. Se houver históricos antigos e
atuais da mesma atividade, os registros são reunidos e ordenados por horário.
Somente registros inteiramente iguais são reduzidos a uma cópia; execuções
distintas no mesmo segundo permanecem separadas. Arquivos CSV são removidos pela
aplicação. O JSONL de versões de cada
arquivo de solução continua sendo um histórico diferente e não é concatenado.

As pastas antigas de atividades também são movidas: por exemplo, `poo/animal`
passa para `poo/labs/animal`. README, soluções, arquivos ocultos e subpastas vazias
acompanham a atividade, preservando conteúdo, permissões dos arquivos e datas de
modificação. O destino é o caminho usado pela atividade: para fontes externas,
fica sob a pasta da fonte no workspace; para índices locais editáveis, é relativo
ao diretório do índice. O índice em si não é movido nem reescrito.

A simulação mostra cada movimentação como `move directory: origem -> destino`.
Se as duas pastas existirem, arquivos distintos ou idênticos são reunidos;
conteúdos ou permissões diferentes no mesmo arquivo bloqueiam a migração. Não
são seguidos links simbólicos nem movidas pastas que contenham índices ou outras
atividades atuais. As pastas antigas são removidas depois de transferir seus
arquivos. Os resolvedores usam o caminho exato e não acrescentam ou removem
`labs/` durante o uso normal.

Ao reabrir o workspace, a contagem é reconstruída a partir dos eventos em ordem
cronológica, usando a deduplicação e os limites de tempo existentes. Assim,
registros antes separados entre a chave antiga e a atual compõem uma única
atividade. O total corrigido pode aumentar quando recupera intervalos antes
interrompidos pela troca de chave. Os filtros comparam a chave completa, inclusive
a fonte.

O `history.csv` continua sendo um arquivo legado: a migração de identidade não o
importa para os logs diários nem altera quais formatos o logger carrega. O formato
obsoleto `task_log.csv`, sem leitor definido no código atual, bloqueia a operação
para evitar uma conversão especulativa.

## Conflitos e recuperação

Referências ambíguas, logs diários ou registros de execução inválidos e históricos
de versões com conteúdos diferentes no mesmo destino impedem a aplicação.
Arquivos distintos podem ser reunidos na mesma pasta; arquivos idênticos podem compartilhar o destino.
Não há opção para sobrescrever versões divergentes.

A aplicação valida novamente os arquivos inspecionados e escreve o marcador de
formato por último. Ela não cria pastas de backup nem cópias dos dados do aluno;
em caso de interrupção ou erro, restaure o workspace com o Git.

Workspaces que ainda tenham um marcador de migração pendente criado por uma
versão anterior podem ser recuperados com:

```sh
tko tool migrate /caminho/do/workspace --recover
```

A recuperação restaura os arquivos e pastas anteriores usando o manifesto legado e remove o
marcador de operação pendente. Ela também pode ser repetida após interrupção.
Arquivos modificados por outro processo após a migração interrompida fazem a
recuperação parar, para que não sejam sobrescritos. Depois da recuperação,
inspecione e aplique novamente. `--recover` trata somente operações pendentes legadas;
não desfaz automaticamente uma migração já concluída.
