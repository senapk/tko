# TKO: conceitos e organização

Este documento apresenta o modelo conceitual do TKO para alunos, professores e desenvolvedores.

## Visão geral

O TKO é um ambiente de aprendizagem executado no terminal para organizar, realizar, testar e acompanhar atividades, especialmente atividades de programação.

Seu objetivo não é apenas armazenar a solução final produzida pelo estudante. O TKO também registra o processo de aprendizagem: quais atividades foram abertas, quando o código foi executado, quais testes foram realizados, como a solução evoluiu e quais ações ocorreram durante o trabalho.

O TKO pode ser utilizado por comandos individuais:

```bash
tko task list
tko task down poo@carro
tko run
```

As mesmas operações também podem ser acessadas por uma TUI, uma interface navegável dentro do terminal.

Como a ferramenta não depende da interface de uma IDE específica, o usuário pode editar seus arquivos no VS Code, em uma IDE JetBrains, no Neovim, no Helix ou em qualquer outro editor. O editor cuida da edição; o TKO cuida das atividades, da execução, dos testes, do histórico e das métricas.

## TKO e Git

O TKO e o Git representam duas camadas distintas que normalmente compartilham a mesma pasta de trabalho:

| Camada | Marcador | Responsabilidade |
|---|---|---|
| Repositório Git | `.git/` | Versionamento, backup, sincronização e distribuição dos arquivos |
| Workspace TKO | `.tko/` | Atividades, fontes, execução, progresso, histórico e métricas de aprendizagem |

Uma pasta pode ser simultaneamente um repositório Git e um workspace TKO:

```text
student-repository/
├── .git/
├── .tko/
├── README.md
├── labs/
├── poo/
└── fup/
```

Uma síntese útil é:

> O TKO registra o processo de aprendizagem; o Git preserva, protege e distribui esse registro.

Em princípio, os arquivos do TKO poderiam ser transportados por outros mecanismos. Na prática, o Git faz parte do fluxo operacional recomendado porque oferece histórico, recuperação, sincronização, controle de acesso e clonagem integral do workspace.

## Workspace TKO

Um workspace TKO é uma pasta inicializada por meio de:

```bash
tko init
```

Esse comando cria a pasta `.tko/` e prepara o ambiente no qual o usuário poderá cadastrar fontes, acessar atividades, executar código e registrar seu progresso.

O workspace é a unidade de trabalho do usuário. Ele pode conter simultaneamente:

- atividades propostas por professores;
- cópias de atividades obtidas de fontes externas;
- códigos de estudo;
- experimentos pessoais;
- projetos individuais;
- atividades autorais que futuramente poderão ser publicadas.

## A pasta `.tko`

A pasta `.tko/` contém a estrutura operacional interna do workspace. Entre outras informações, ela pode guardar:

- fontes cadastradas;
- linguagem selecionada;
- estado de navegação;
- progresso nas atividades;
- eventos de abertura, execução e teste;
- resultados de testes;
- histórico de versões monitoradas;
- métricas de aprendizagem;
- dados de auditoria;
- clones usados como cache.

O arquivo `.tko/repository.toml` guarda as principais configurações, fontes, estados e referências internas do workspace.

O histórico do TKO é mais automático e detalhado que o histórico normal do Git:

```text
Git -> registra versões quando o usuário cria commits
TKO -> registra eventos e estados enquanto o usuário trabalha
```

Ao executar um teste, por exemplo, o TKO pode registrar tanto a ocorrência do teste quanto o código existente naquele momento. Em modos de auditoria, a ferramenta também pode observar a pasta de trabalho e registrar alterações em intervalos periódicos.

## Publicação da `.tko`

A pasta `.tko/` não é necessária para que um professor publique uma fonte de atividades. Entretanto, ela é parte importante do repositório entregue pelo aluno.

No fluxo acadêmico habitual, o repositório do aluno é privado e compartilhado com o professor. A `.tko/` é versionada junto com o código para permitir que o professor clone e abra o workspace no estado em que foi entregue.

Com isso, o professor pode consultar:

- tarefas realizadas;
- evolução das soluções;
- histórico de execução;
- tentativas de teste;
- snapshots;
- métricas;
- gráficos;
- evidências do processo de aprendizagem.

Esses registros devem ser entendidos como evidências de aprendizagem, e não como provas forenses invioláveis. A confiabilidade do histórico pode ser fortalecida com repositórios controlados pelo professor, proteção de branches, proibição de force push e coleta periódica.

## Fluxo acadêmico habitual

O fluxo mais comum envolve dois repositórios Git.

### Repositório do professor

O professor:

1. cria ou seleciona atividades;
2. organiza essas atividades em um índice;
3. publica o conteúdo em um repositório Git;
4. fornece aos alunos o endereço do índice.

Esse repositório pode conter:

```text
teacher-content/
├── README.md
├── labs/
└── wiki/
```

Ele não precisa conter `.tko/`, pois seu objetivo principal é publicar conteúdo. Se o produtor executar `tko init`, o mesmo diretório também se torna um workspace pessoal, sem que a `.tko/` passe a integrar obrigatoriamente o formato público do conteúdo.

### Repositório do aluno

O aluno:

1. recebe ou cria um repositório Git, normalmente privado;
2. executa `tko init`;
3. escolhe a linguagem de trabalho;
4. adiciona o índice do professor como fonte;
5. realiza as atividades;
6. envia periodicamente código, artefatos e `.tko/` para o Git.

O professor, como responsável pelo repositório, pode cloná-lo e abrir o workspace com o TKO para analisar todo o ambiente.

```text
Professor publica atividades
            ↓
Aluno cadastra a fonte
            ↓
Aluno realiza as atividades
            ↓
TKO registra código e interações
            ↓
Git preserva e entrega o workspace
            ↓
Professor abre e analisa o ambiente
```

## Modelo conceitual mínimo

Para o usuário, o modelo pode ser resumido em quatro elementos:

```text
Workspace -> Fontes -> Índices -> Atividades
```

- O workspace reúne o trabalho e o histórico do usuário.
- Uma fonte cadastra um índice sob uma chave local.
- O índice organiza e descreve as atividades.
- A atividade é algo que o estudante deve consultar ou realizar.

O Git e o cache sustentam esse modelo, mas não precisam aparecer como conceitos pedagógicos principais.

## Fonte

Uma fonte é um índice cadastrado no workspace sob uma chave curta.

Conceitualmente:

```text
fonte = chave local + URI do índice
```

Exemplos de chaves:

```text
labs
fup
poo
ed
```

A chave funciona como:

- alias local;
- namespace das atividades;
- prefixo usado nos comandos;
- nome convencional da área de trabalho associada à fonte.

O mesmo índice pode ser adicionado por usuários diferentes com chaves diferentes. A chave não é uma identidade global publicada pelo autor; ela pertence ao cadastro local.

## Identidade das atividades

Cada entrada de um índice possui uma chave única dentro daquele índice. No workspace, a identidade lógica da atividade é composta por:

```text
fonte@atividade
```

Exemplos:

```text
poo@carro
fup@vetores
labs@meu-jogo
```

Duas fontes podem empregar a mesma chave sem colisão:

```text
fup@carro
poo@carro
```

Essa identidade composta pode ser utilizada para localizar a atividade, executar comandos, associar resultados e métricas, organizar snapshots e reconstruir o progresso do usuário.

## Fontes gerenciadas e externas

A classificação da fonte diz respeito ao índice, não necessariamente a todas as atividades referenciadas por ele.

Uma fonte gerenciada tem índice editável dentro do workspace. A fonte gerenciada padrão usa a chave `labs` e normalmente emprega o `README.md` da raiz como índice. Ela permite que o usuário registre códigos de estudo, experimentos, projetos pessoais e atividades autorais.

Uma fonte externa possui um índice fora do workspace, obtido de um repositório Git, uma pasta local externa ou outro local acessível pela ferramenta. O índice externo é tratado como somente leitura. O usuário pode realizar as atividades descritas por ele, mas não altera o índice original por meio do fluxo normal de consumo.

## Origem e atividade de trabalho

É importante não confundir o conteúdo oferecido por uma fonte com o elemento editável no workspace.

- Origem: conteúdo apontado pelo índice.
- Atividade de trabalho: elemento editável acompanhado pelo TKO.
- Materialização: criação de uma cópia local a partir de uma origem externa.
- Procedência: relação entre a atividade de trabalho e sua origem.

Para atividades produtivas, a regra pode ser expressa assim:

```text
direct = índice gerenciado AND destino dentro do workspace
```

| Índice | Destino | Comportamento |
|---|---|---|
| Gerenciado | Dentro do workspace | Trabalha diretamente no original |
| Gerenciado | Fora do workspace | Materializa uma cópia |
| Externo | Fora do workspace | Materializa uma cópia |

Essa regra cria uma fronteira simples: conteúdos pertencentes ao workspace podem ser gerenciados diretamente; conteúdos externos são preservados e originam cópias de trabalho.

## Área de trabalho associada à fonte

Cada chave de fonte define um namespace e, convencionalmente, uma pasta local onde ficam suas atividades de trabalho.

```text
workspace/
├── labs/       # originais associados à fonte gerenciada labs
├── poo/        # cópias de trabalho provenientes da fonte poo
└── fup/        # cópias de trabalho provenientes da fonte fup
```

Assim:

```text
poo@carro -> poo/carro/
fup@vetor -> fup/vetor/
```

A pasta `poo/` não é a fonte externa original. Ela é a área local que contém as atividades materializadas a partir da fonte chamada `poo`.

Para `labs`, a convenção reúne o namespace da fonte gerenciada e a pasta dos conteúdos autorais. Nesse caso, origem e área de trabalho normalmente coincidem.

## Índice

O índice é um arquivo Markdown que funciona simultaneamente como:

- apresentação humana;
- catálogo de atividades;
- plano pedagógico;
- arquivo processável pelo TKO.

O índice informa ao TKO:

- a chave de cada atividade;
- o que o aluno deve fazer;
- onde o conteúdo pode ser encontrado;
- como as atividades são agrupadas;
- quais regras de progressão e gamificação se aplicam.

O índice não precisa armazenar fisicamente as atividades. Ele apenas referencia seus destinos.

## `README.md` como índice padrão

O índice padrão de uma fonte publicável é o `README.md`.

Essa escolha permite que o mesmo arquivo:

1. apresente o repositório automaticamente no GitHub;
2. documente o plano de estudo para pessoas;
3. seja interpretado pelo TKO como índice.

## Entradas de atividade

Uma entrada contém, no mínimo:

```text
chave + tipo + link
```

Exemplo:

```md
- [ ] `@carro type=make gain=2 hard=3 size=1 eval=test` [Um carro simples](labs/carro/README.md)
```

Uma entrada pode declarar chave, tipo de ação, utilidade, dificuldade, tamanho, forma de avaliação e outros metadados pedagógicos.

Normalmente, a chave é igual ao nome da pasta da atividade. Essa é uma convenção útil, mas a chave continua explícita no índice e não precisa ser derivada obrigatoriamente do caminho.

O tipo da atividade e sua forma de avaliação são dimensões independentes:

```text
type=make -> o aluno deve produzir alguma coisa
eval=self -> o aluno avalia quanto conseguiu realizar
eval=test -> o resultado é verificado por testes cadastrados
```

Assim, `make` não implica necessariamente a existência de testes automáticos.

## Atividades `read` e `make`

O índice distingue dois comportamentos principais.

`type=read` indica uma atividade ou recurso destinado à consulta. Markdown pode ser aberto diretamente no editor, e vídeos, páginas e URLs externas podem ser abertos no navegador. O conteúdo não é materializado como uma atividade editável.

`type=make` indica que o estudante deve produzir ou modificar algum artefato: código, relatório, resumo, diagrama, projeto, experimento ou qualquer outro produto previsto pela atividade. Se o destino estiver dentro do workspace e pertencer a um índice gerenciado, o TKO trabalha diretamente no original. Caso contrário, cria uma cópia de trabalho.

Uma atividade `make` pode ser avaliada de diferentes formas. Com `eval=self`, o aluno atribui a própria avaliação de acordo com o que conseguiu realizar. Com `eval=test`, o TKO utiliza os testes fornecidos pelo autor.

## Por que o tipo pertence ao índice

O produtor conhece a intenção pedagógica da atividade, mas o indexador não deve tentar inferi-la analisando o conteúdo.

O mesmo arquivo pode ser utilizado de formas distintas:

```md
- [ ] `@heranca type=read` [Herança](wiki/heranca/README.md)
- [ ] `@resumo-heranca type=make eval=self` [Resumo de herança](wiki/heranca/README.md)
```

No primeiro caso, o aluno apenas consulta o texto. No segundo, deve produzir um resumo a partir dele.

O indexador precisa confiar no contrato declarado pelo autor:

- não deve baixar a atividade durante a indexação;
- não deve interpretar o enunciado;
- não deve procurar marcadores internos;
- não deve inferir a intenção por nomes de arquivos ou pastas.

Isso torna a indexação rápida, determinística e independente da disponibilidade imediata dos destinos remotos.

Uma regra fundamental é:

> O conteúdo informa o que existe; o índice informa o que o aluno deve fazer com esse conteúdo.

