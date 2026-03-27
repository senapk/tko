# Marcadores e Tipos de Atividades

Uma questão segue a seguinte estrutura:

```md
[ ] @label :marcadores [Título](pasta/README.md)

# você pode empacotar dentro de crases para alinhas ou tags html para esconder, mas o formato é sempre o mesmo:
[ ] `@label :marcadores`[Título](pasta/README.md)
[ ] <!-- @label :marcadores -->[Título](pasta/README.md)
```

Cada marcador representa uma propriedade da questão.

```txt
Pergunta               Categoria   Valores                      Padrão
---------------------- ----------- -----------------------------------
É Obrigatório?         Prioridade  main, side                   main
Consumir ou Produzir?  Ação        edit, view                   edit
Formato de avaliação   Avaliação   auto, user                   auto
Quanto vale?           Nível       0..9                         1
Consultar muda nota?   Consulta    free, part, zero             part
```

## Regras

- A ordem dos marcadores é livre.
- Marcadores omitidos usam o valor padrão. 
- Se não houver ":" a atividade usa todos os valores padrão.
- Caso não existe um marcador para uma categoria, o valor padrão é assumido.
- A ordem dos marcadores é livre.
- Se dois marcadores de mesma categoria forem especificados, o último prevalece.
- Marcadores são case-sensitive.

## Significados e interações

```txt
Categoria   Nome    Significado
----------- ------- ---------------------------------------
Avaliação   auto    avaliação automática por testes
            user    avaliação feita pelo próprio usuário
Ação        edit    editar / produzir conteúdo
            view    visualizar / consumir conteúdo
Prioridade  main    tarefas sugeridas
            side    tarefas opcionais
Consulta    free    consulta permitida e não afeta a nota
            part    consulta permitida, mas afeta a nota
            zero    consulta proibida, nota zero se for consultada
```

### Comportamento em atividades view

Se o view for um link remoto → abre no navegador.
Se o view for um link local → é aberto automaticamente no editor.

### Comportamento em atividades edit

É criado uma pasta com o nome da atividade na pasta do aluno, e o arquivo de descrição, testes(se houverem) e arquivos de rascunho são copiados para essa pasta. Se o view também for `user` para autoavaliação, é criado um `draft.md` para o aluno colocar as respostas.


## Exemplos

```txt
Marcação   Interpretação
---------- ---------------------------------------------
                        main, edit, nível 1, auto, open
:1:main:view:user:free  1 ponto, leitura obrigatória 
:1:side:view:user:free  1 ponto, leitura extra
:2:main:edit:auto:part  exercício nível 2 com autoavaliação
:3:main:edit:auto:zero  prova automática nível 3
:0:side:view:user:free  leitura sem pontuação
:1:side:edit:user:free  resumo apenas para entrega
:1:side:edit:user:part  projeto extra de código com consulta controlada
```

## Restrições

Utilizar dois marcadores de mesma categoria é permitido, mas o último prevalece. Exemplo:

```txt
:3:auto:user → prevalece user, ou seja, avaliação feita pelo próprio usuário
```

Mesmo que qualquer combinação seja possível, nem todas fazem sentido, pois não vão gerar interações coerentes no sistema. Exemplo:

```txt
:auto:view → avaliação automática, mas para ser consumida, o que não faz sentido. O ideal seria :auto:edit.
:zero:view → consulta proibida, mas para ser consumida, o que não faz sentido. O ideal seria :zero:edit.
```

Atividades para serem consumidas normalmente vão estar como `free`.
