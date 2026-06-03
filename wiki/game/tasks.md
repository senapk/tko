# Marcadores e Tipos de Tarefas

Uma tarefa é definida em uma linha markdown com checkbox e link:

```md
- [ ] `@t1 xp=9 tier=3 type=make eval=test loss=part` [Implementar função soma](t1/README.md)
- [ ] `@t2 xp=5 tier=2 type=read` [Ler artigo sobre listas](https://exemplo.com/material)
```

O identificador `@chave` é obrigatório. Os demais campos podem ser omitidos e assumem valores padrão.


## Atualização automática do README.md

O comando `tko build index README.md <pasta>` atualiza as tarefas do README.md utilizando a pasta especificada com a fonte das tarefas. Ele atualiza automaticamente os campos:

- título: o texto do link é atualizado para o título encontrado no arquivo `README.md` da tarefa, ou permanece o mesmo se não houver título.
- eval: tipo de avaliação
  - `test` se ele encontrar um arquivo de teste `tests.toml` na pasta da tarefa.
  - `self` caso contrário.

O script vai inserir todos os outros parâmetros com os valores default, para serem ajustados manualmente depois, se necessário. Ele não remove ou altera os campos que já existem, apenas adiciona os que estão faltando e ordena os campos na ordem padrão.

O usuário pode definir manualmente os campos:
  - type: tipo da tarefa (make ou read)
  - xp: pontuação da tarefa
  - tier: nível de dificuldade

xp e tier são diferentes porque nem tudo que é difícil é valioso. Algumas atividas podem ser desafiadoras por lógica ou curiosidade, mas não necessariamente são o foco do curso, e vice-versa.

Para tarefas do tipo `make` existem duas opções extras:
  - loss: política de penalidade por consulta, o usuário pode escolher entre:
    - `zero`: consulta proibida; se houver consulta, o progresso fica zerado.
    - `part`: consulta permitida, mas com penalidade parcial.
    - `free`: consulta permitida sem penalidade.
  - eval: tipo de avaliação, é preenchido automaticamente pelo `tko build index`.
    - `test`: avaliação automática por testes, se houver um arquivo `tests.toml` na pasta.
    - `self`: autoavaliação pelo próprio aluno, se não houver um arquivo `tests.toml` na pasta.

## Campos Suportados

| Campo | Valores possíveis | Padrão | Descrição |
|-------|-------------------|--------|-----------|
| `@chave` | `@t1`, `@foo`, ... | obrigatório | Identificador único da tarefa |
| `xp=` | números inteiros | `1` | Pontuação/XP da tarefa |
| `tier=` | números inteiros | `1` | Nível de dificuldade da tarefa |
| `type=` | `make`, `read` | `make` | Tipo da tarefa |
| `loss=` | `zero`, `part`, `free` | part| Política de penalidade por consulta |

Os campos podem aparecer antes do link, dentro do título ou depois do link. O parser também reconhece campos entre crases e comentários HTML, porque esses delimitadores são ignorados na leitura dos marcadores.

## Valores Padrão

- `xp=1`
- `tier=1`
- `type=make`
- Para `type=make`: `loss=part`

Quando a tarefa é `type=read`, `eval` e `loss` são sempre ajustados para `self` e `free`.

## Tipos

- `type=make`: tarefa de produção, normalmente editável, como programar, escrever ou resolver um exercício.
- `type=read`: tarefa de consumo, como ler, assistir ou explorar um material externo.

Links externos `http`/`https` seguem uma regra especial:

- `type=read` mantém o link como URL externa.
- `type=make` aceita URLs do GitHub e extrai o repositório/caminho.
- `type=make` com URL externa que não seja GitHub vira uma tarefa de leitura.

## Avaliação e Penalidade

- `eval=test`: avaliação automática por testes.
- `eval=self`: autoavaliação pelo próprio aluno.
- `loss=zero`: consulta proibida; se houver consulta, o progresso fica zerado.
- `loss=part`: consulta permitida, mas com penalidade parcial.
- `loss=free`: consulta permitida sem penalidade.

## Sintaxe Antiga

A sintaxe antiga com `:` ainda é aceita por compatibilidade, mas será automaticamente atualizada na execução do `tko build index`

```md
- [ ] `@t1 :10:test:zero` [Implementar função soma](t1/README.md)
- [ ] [@video_intro :read Vídeo de introdução](https://exemplo.com/video)
```


## Recomendações

- Prefira o formato chave-valor para clareza e manutenção futura.
- Use nomes de campos e valores em minúsculas.
