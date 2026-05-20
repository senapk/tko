# Marcadores e Tipos de Atividades

Uma questão segue a seguinte estrutura:

```md
- [ ] @label :marcadores [Título](pasta/README.md)

# você pode empacotar dentro de crases para alinhas ou tags html para esconder, mas o formato é sempre o mesmo:
- [ ] `@label :marcadores`[Título](pasta/README.md)
- [ ] <!-- @label :marcadores -->[Título](pasta/README.md)
- [ ] @label <!-- :marcadores -->[Título](pasta/README.md)

```

Cada marcador representa uma propriedade da questão.

```txt
Pergunta               Categoria   Valores                      Padrão
---------------------- ----------- -----------------------------------
É Obrigatório?         Prioridade  main, side                   main
Consumir ou Produzir?  Ação        do, read                     do
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
Ação        do      produzir conteúdo
            read    visualizar / consumir conteúdo
Prioridade  main    tarefas sugeridas
            side    tarefas opcionais
Consulta    free    consulta permitida e não afeta a nota
            part    consulta permitida, mas afeta a nota
            zero    consulta proibida, nota zero se for consultada
```

### Comportamento em atividades read

Se o read for um link remoto → abre no navegador.
Se o read for um link local → é aberto automaticamente no editor.

### Comportamento em atividades do

É criado uma pasta com o nome da atividade na pasta do aluno, e o arquivo de descrição, testes(se houverem) e arquivos de rascunho são copiados para essa pasta. Se o read também for `user` para autoavaliação, é criado um `draft.md` para o aluno colocar as respostas.


## Exemplos

```txt
Marcação   Interpretação
---------- ---------------------------------------------
                        main, do, nível 1, auto, open
:1:main:read:user:free  1 ponto, leitura obrigatória 
:1:side:read:user:free  1 ponto, leitura extra
:2:main:do:auto:part  exercício nível 2 com autoavaliação
:3:main:do:auto:zero  prova automática nível 3
:0:side:read:user:free  leitura sem pontuação
:1:side:do:user:free  resumo apenas para entrega
:1:side:do:user:part  projeto extra de código com consulta controlada
```

## Restrições

Utilizar dois marcadores de mesma categoria é permitido, mas o último prevalece. Exemplo:

```txt
:3:auto:user → prevalece user, ou seja, avaliação feita pelo próprio usuário
```

Mesmo que qualquer combinação seja possível, nem todas fazem sentido, pois não vão gerar interações coerentes no sistema. Exemplo:

```txt
:auto:read → avaliação automática, mas para ser consumida, o que não faz sentido. O ideal seria :auto:do.
:zero:read → consulta proibida, mas para ser consumida, o que não faz sentido. O ideal seria :zero:do.
```

Atividades para serem consumidas normalmente vão estar como `free`.
