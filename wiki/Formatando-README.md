## Tasks

Uma tarefa no README.md segue a seguinte estrutura:

```md
[ ] @label :marcadores [Título](pasta/README.md)

Você pode empacotar as informações dentro de crases para alinhar ou tags html para esconder, mas o formato é sempre o mesmo:
[ ] `@label :marcadores`[Título](pasta/README.md)
[ ] <!-- @label :marcadores -->[Título](pasta/README.md)
```

### Marcadores

Cada marcador representa uma propriedade da questão.

```txt
: [=|+] [#|>] [0..9] [a|u|t] [?|!]
(Ordem Livre)

Pergunta               Categoria   Valores                  Padrão
---------------------- ----------- ------------------------ --------
É Obrigatório?         Prioridade  =:main, +:side           =
Consumir ou Produzir?  Ação        #:edit, >:view           #
Quem avalia?           Avaliação   a:auto, u:user, t:tick   a
Quanto vale?           Nível       0..9                     1
Pode consultar?        Consulta    ?:open, !:exam           ?
```

**Regras:**

- Marcadores omitidos usam o valor padrão. 
- Se não houver ":" a atividade usa todos os valores padrão.
- Caso não existe um marcador para uma categoria, o valor padrão é assumido.
- A ordem dos marcadores é livre.
- Se dois marcadores de mesma categoria forem especificados, o último prevalece.
- Marcadores são case-sensitive.

### Símbolos no TKO

```txt
Categoria   Código   Símbolo   Nome    Significado
----------- -------- --------- ------- ---------------------------------------
Avaliação   a        ●         auto    avaliação automática por testes
            u        ○         user    avaliação feita pelo próprio usuário
            t        ◇         tick    apenas registro de conclusão (sem avaliação)

Ação        #        ✎         edit    editar / produzir conteúdo
            >        ↗         view    visualizar / consumir conteúdo

Prioridade  =        ★         main    tarefas sugeridas
            +        ☆         side    tarefas opcionais

Consulta    ?        ↺         open    consulta permitida
            !        ⊘         exam    consulta proibida
```

**Comportamento da ação view**

Se o view for um link remoto → abre no navegador.
Se o view for um link local → abre o arquivo no editor de código.

**Nível**

O nível representa apenas a dificuldade/peso da atividade e é indicado somente por único número:

:0 :1 ... :9

**Exemplos**

```txt
Marcação   Interpretação
---------- ---------------------------------------------
:          main, edit, nível 1, auto, open
:>         leitura obrigatória
:+>        leitura extra
:2#u       exercício nível 2 com autoavaliação
:3#a!      prova automática nível 3
:0t>       leitura sem pontuação
:1t#       resumo apenas para entrega
:+3u#?     projeto extra com consulta
```

**Restrições**

Ao especificar dois marcadores de mesma categoria, o último prevalece. Exemplo:

```txt
:324ta → nível 3, auto
```

Mesmo que qualquer combinação seja possível, nem todas fazem sentido, pois não vão gerar interações coerentes no sistema. Exemplo:

```txt
:a> → avaliação automática, mas para ser consumida, o que não faz sentido. O ideal seria :a#.
:!> → consulta proibida, mas para ser consumida, o que não faz sentido. O ideal seria :!#.
```

Atividades para serem consumidas, normalmente vão estar como `tick` ou `user`.

Da mesma forma, atividades para serem editadas, normalmente vão estar como `auto` ou `user`.
