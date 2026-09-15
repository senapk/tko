# Criando Testes e Conversoes

Este guia complementa o [guia para criar repositorios de tarefas](Criando-Atividades.md).
Use-o quando precisar escrever, converter ou publicar casos de teste.

Para estrutura do repositorio, formato de quests, formato de tasks e checklist
de publicacao, consulte primeiro o guia principal.

## Onde colocar testes

Uma tarefa com avaliacao automatica normalmente usa `eval=diff` na linha do
indice e possui casos de teste na propria pasta da tarefa:

```txt
labs/soma/
├── README.md
└── tests.toml
```

O TKO tambem aceita casos em formatos `.tio`, `.vpl` ou em pastas com pares de
entrada e saida.

## Formato `tests.toml`

`tests.toml` e o formato compacto recomendado para tarefas novas.

```toml
[[tests]]
input = '1 2\n'
output = '3\n'

[[tests]]
input = '''
10
20
'''
output = '''
30
'''
```

Boas praticas:

- Cubra pelo menos um caso simples.
- Inclua casos de borda quando eles forem relevantes para o enunciado.
- Mantenha entradas e saidas exatamente como o programa deve ler e imprimir.
- Prefira casos pequenos e legiveis no material publico.

## Testes no README com mdpp

Quando o enunciado precisa mostrar exemplos gerados a partir dos testes, use o
preprocessador Markdown:

```bash
tko tool mdpp README.md
```

Ele pode carregar testes de `tests.toml` e inserir blocos renderizados no
`README.md`. A referencia completa esta em [Markdown Preprocessor](tools/mdpp.md).

## Convertendo entre formatos

O destino pode ser omitido. Nesse caso, o resultado é escrito como TOML na
saída padrão:

```bash
tko tool convert-tests tests.toml > normalized.toml
```

Gerar `t.vpl` a partir de `tests.toml`:

```bash
tko tool convert-tests tests.toml -o t.vpl
```

Gerar `t.tio` a partir de `README.md` e `extra.tio`:

```bash
tko tool convert-tests README.md extra.tio -o t.tio
```

Extrair testes para uma pasta:

```bash
mkdir pasta
tko tool convert-tests tests.toml -o pasta
```

Extrair de `cases.tio`:

```bash
mkdir pasta
tko tool convert-tests cases.tio -o pasta
```

## Testes em pasta

Ao converter para pasta, o TKO gera pares de entrada e saida, como:

```txt
pasta/
├── 00.in
├── 00.sol
├── 01.in
└── 01.sol
```

Para rodar uma solucao usando essa pasta:

```bash
tko run Solver.java pasta
```

## Padrao de nomes com `--write-pattern`

Use `--write-pattern` para escolher os nomes dos arquivos gerados. O caractere `@` funciona
como marcador da numeracao.

```bash
tko tool convert-tests cases.tio -o pasta/ --write-pattern "in.@ out.@"
```

Padroes comuns:

- `--write-pattern "@.in @.out"`
- `--write-pattern "in@ out@"`
- `--write-pattern "in.@ out.@"`

## Gerando rascunhos para alunos

Quando a disciplina mantem uma solucao completa do professor e precisa gerar
arquivos iniciais para alunos, use:

```bash
tko tool filter
```

Os arquivos de solucao costumam ficar em `src/<lang>/...`, conforme convencao
da disciplina. Veja [Filtragem e rascunhos](tools/filter.md).

## Pipeline de publicacao da tarefa

Para tarefas que usam preprocessamento de Markdown, rebase de links, VPL ou
rascunhos, o comando mais conveniente e:

```bash
tko task build
```

Ele executa a preparacao da tarefa e gera artefatos de publicacao quando
aplicavel. Veja [Build task](tools/build-all.md).

## Checklist de testes

- A linha da task usa `eval=diff`.
- O arquivo de testes esta na pasta da tarefa ou foi referenciado pelo fluxo de build.
- Os exemplos do enunciado batem com os testes publicos.
- A solucao de referencia passa nos testes.
- Conversoes para `.tio`, `.vpl` ou pasta foram revisadas quando usadas.
- O guia principal foi seguido para atualizar o indice do repositorio.
