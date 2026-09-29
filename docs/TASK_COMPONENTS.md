# Componentes de uma tarefa TKO

Este documento define a unidade de informação que um integrador deve extrair
de um repositório de conteúdo TKO. Ele complementa o [guia para criar
repositórios de tarefas](../wiki/Criando-Atividades.md) e a [especificação de
formatos](FORMATS.md).

## Princípio geral

Uma tarefa TKO não é apenas o seu `README.md`. Ela é formada por:

```text
entrada no índice + contexto da quest + pasta da atividade + artefatos opcionais
```

O índice fornece identidade, título, quest, modo de avaliação e parâmetros. A
pasta da atividade fornece o enunciado, os assets, os testes e os arquivos de
código. Alguns arquivos são fontes de autoria; outros são artefatos gerados
para distribuição.

## Estrutura esperada

Um repositório de conteúdo normalmente possui esta forma:

```text
README.md                         # índice de quests e tasks
labs/
└── soma/
    ├── README.md                 # descrição da tarefa
    ├── assets/                   # imagens e outros recursos do enunciado
    ├── tests.toml                # testes, quando houver
    ├── src/
    │   ├── py/solver.py          # solução ou fonte para gerar starter
    │   └── feedback.toml         # feedback/autoavaliação, quando usado
    └── .cache/
        ├── README.md             # README com arquivos locais embutidos, opcional
        ├── README.html           # enunciado publicado, opcional
        ├── tests.vpl             # testes convertidos, opcional
        └── starter/
            └── py/solver.py      # starter gerado, opcional
```

O diretório não precisa se chamar `labs`. O caminho pode ser qualquer diretório
relativo ao README de índice, desde que a entrada aponte para o
`<tarefa>/README.md`.

## Componentes da tarefa

| Componente | Obrigatório | Origem | Conteúdo a preservar |
| --- | --- | --- | --- |
| Identidade | Sim | índice e caminho do README | fonte, chave, caminho, título e revisão do repositório |
| Contexto pedagógico | Não | quest no índice | quest, tags, linguagem, meta, ordem e `[x]`/`[ ]` |
| Configuração de avaliação | Sim | linha da task | `eval`, parâmetros e valores calculados, como XP |
| Descrição | Sim | `<tarefa>/README.md` | Markdown original, versão processada e hash |
| Assets | Não | `<tarefa>/assets/` e links do README | arquivos binários/textuais, caminho e hash |
| Testes | Não | TOML, TIO, VPL, Markdown ou diretório | arquivo original, formato e casos normalizados |
| Código de autoria | Não | `<tarefa>/src/<linguagem>/` | arquivos de referência, solução ou draft |
| Starter distribuído | Não | `<tarefa>/.cache/starter/<linguagem>/` | arquivos entregues ao aluno e origem do filtro |
| Feedback | Não | `<tarefa>/src/feedback.toml` | regras de feedback/autoavaliação |
| Artefatos de publicação | Não | `<tarefa>/.cache/` | README autocontido, HTML e testes VPL |
| Proveniência | Sim | Git e comentário `source` | URL, commit, caminho, data e hash dos arquivos |

`README.md` da raiz é o índice do repositório de conteúdo. Ele não deve ser
confundido com o `README.md` dentro da pasta da tarefa, que é o enunciado. No
repositório deste projeto, o README raiz descreve o próprio TKO; as tarefas de
exemplo ficam em fixtures de teste, como
`tests/autoload/baruel_sem_rep/`.

## 1. Identidade e contexto do índice

Para cada linha de task, extraia os dados do índice que a contém:

```text
README.md
└── quest
    └── task line -> labs/soma/README.md
```

Campos recomendados:

| Campo | Descrição |
| --- | --- |
| `source_name` | nome local da fonte, quando o TKO estiver consumindo um workspace |
| `source_url` | URL do repositório ou origem remota |
| `source_revision` | commit, tag ou outro identificador imutável da coleta |
| `index_path` | caminho do README de índice |
| `line_number` | linha da task no índice |
| `task_path` | diretório da tarefa relativo ao índice |
| `task_key` | chave lógica da tarefa; para tarefas locais, o caminho é a referência mais estável |
| `full_key` | chave no workspace, normalmente `source_name@task_key` |
| `title` | texto entre colchetes na linha da task |
| `quest_key` | chave da quest que contém a task |
| `is_reference` | se a linha usa `[x]` e conta para a meta da quest |
| `eval` | `none`, `self` ou `diff` |
| `parameters` | pares `nome=valor` da linha |
| `raw_index_line` | linha original, útil para auditoria e reprocessamento |

A chave `@...` usada em sintaxes antigas não deve ser a única identidade do
registro. Para evitar colisões, use pelo menos `source + revision + task_path`.

## 2. Descrição e assets

O arquivo `<tarefa>/README.md` é obrigatório. O importador deve armazenar:

- caminho relativo;
- conteúdo Markdown original;
- conteúdo após `mdpp`, se esse processamento tiver sido executado;
- título extraído;
- links e imagens referenciados;
- hash, tamanho e codificação;
- assets existentes, especialmente em `assets/`.

Não substitua o Markdown original pelo HTML. O HTML e o README autocontido são
representações derivadas e devem ser armazenados separadamente.

## 3. Testes

Não procure somente por `tests.toml`. O TKO pode carregar testes de:

- `tests.toml`;
- arquivos `.tio`, `.vpl` e `.cases`;
- diretórios com pares de entrada e saída, como `00.in`/`00.sol`;
- blocos de teste no próprio `README.md`;
- arquivos convertidos ou gerados durante o build.

Para cada conjunto de testes, preserve duas camadas:

1. **Fonte original**: caminho, formato, conteúdo e hash.
2. **Casos normalizados**: identificador, entrada, saída esperada e, quando
   existir, nota/grade ou metadados do formato.

O campo `eval` ajuda a interpretar a ausência de testes:

- `none`: material de leitura ou consulta; normalmente não possui testes;
- `self`: atividade com autoavaliação/feedback; pode não possuir casos de
  entrada e saída;
- `diff`: atividade com avaliação automatizada por comparação de entrada e
  saída; espera-se um conjunto de testes.

Um teste embutido no README deve continuar associado ao README original, mesmo
que também seja convertido para uma representação normalizada.

## 4. Código, drafts e starters

É necessário distinguir a fonte de autoria do arquivo entregue ao aluno:

```text
src/<linguagem>/...              # fonte mantida pelo autor
.cache/starter/<linguagem>/...   # resultado filtrado para distribuição
```

O diretório `src/` pode conter uma solução completa, código de apoio ou
marcadores usados pelo filtro. O diretório `.cache/starter/` contém o resultado
gerado por `tko build task` ou pelo filtro equivalente.

Recomenda-se registrar cada arquivo de starter com:

- linguagem;
- caminho relativo;
- conteúdo ou referência ao blob armazenado;
- hash;
- tipo (`reference_source`, `draft` ou `student_starter`);
- caminho da fonte que o gerou;
- revisão e comando/processamento usado para gerá-lo.

Se `.cache/starter` não existir, registre o starter como ausente. Não trate
automaticamente todo arquivo em `src/` como starter distribuído.

O arquivo `src/feedback.toml`, quando presente, deve ser armazenado como
componente separado: ele configura feedback/autoavaliação e não é um caso de
teste comum.

## 5. Artefatos derivados

Quando o pipeline `tko build task --moodle` for executado, podem existir:

- `.cache/README.md`: README com referências a arquivos locais embutidas em Base64;
- `.cache/README.html`: versão HTML do enunciado;
- `.cache/tests.vpl`: testes convertidos para VPL;
- `.cache/starter/<linguagem>/...`: starters filtrados.

Para publicação no Moodle pelo Mula, o pacote mínimo é:

```text
.cache/README.html
.cache/tests.vpl
.cache/starter/<linguagem>/   # quando a atividade usa starters
```

O Mula recebe um clone local, usa o caminho relativo da tarefa como chave e
executa `tko build task --moodle` quando esses artefatos ainda não existem.
Não é necessário gerar nem consumir `.cache/mapi.json` no fluxo atual.

Esses arquivos não substituem as fontes originais. O banco deve indicar
claramente `is_generated=true`, `generated_from` e, se possível, o comando e a
revisão que produziram o artefato.

## Modelo de payload recomendado

Uma representação inicial, antes de normalizar em tabelas, pode ser:

```json
{
  "identity": {
    "source_url": "https://github.com/org/course",
    "source_revision": "<commit>",
    "index_path": "README.md",
    "task_path": "labs/soma",
    "task_key": "labs/soma",
    "title": "Soma",
    "quest_key": "@basic",
    "line_number": 12
  },
  "metadata": {
    "eval": "diff",
    "is_reference": true,
    "parameters": {"value": 1},
    "xp": 1.0
  },
  "description": {
    "path": "labs/soma/README.md",
    "markdown": "...",
    "rendered_markdown": null,
    "sha256": "..."
  },
  "tests": [
    {
      "path": "labs/soma/tests.toml",
      "format": "toml",
      "cases": [{"id": "0", "input": "1 2\n", "output": "3\n"}]
    }
  ],
  "starters": [
    {
      "language": "py",
      "path": "labs/soma/.cache/starter/py/solver.py",
      "kind": "student_starter",
      "sha256": "..."
    }
  ],
  "assets": [],
  "generated_artifacts": [],
  "provenance": {
    "collected_at": "2026-01-01T00:00:00Z"
  }
}
```

Se a base for relacional, uma divisão prática é `tasks`, `task_files`,
`task_tests`, `task_test_cases`, `task_starters` e `task_artifacts`. O conteúdo
binário pode ficar em object storage; mantenha na base o caminho lógico, hash,
tamanho, MIME e a referência ao blob.

## Fluxo de ingestão

1. Fixe a revisão do repositório antes de ler arquivos.
2. Leia o README de índice e identifique quest e task.
3. Resolva o link para o README da tarefa, local ou GitHub.
4. Colete o README, Markdown relacionado e assets.
5. Descubra os testes em todos os formatos suportados e normalize os casos.
6. Colete `src/` e `.cache/starter/` sem misturar fonte e artefato gerado.
7. Registre hashes e proveniência de todos os arquivos.
8. Faça upsert usando `source_revision + task_path` como identidade da coleta.

O comportamento de materialização e os artefatos por modo de avaliação estão
descritos em [TASK_LIFECYCLE.md](TASK_LIFECYCLE.md). A implementação dos
carregadores de testes fica em `src/tko/loader/`.
