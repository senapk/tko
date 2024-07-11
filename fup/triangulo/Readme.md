# L1 - @triangulo - Imprimindo ao contrário $required

- Veja a versão online: [aqui.](https://github.com/qxcodeed/arcade/blob/master/base/triangulo/Readme.md)
- Para programar na sua máquina (local/virtual) use:
  - `tko down ed triangulo`
- Se não tem o `tko`, instale pelo [LINK](https://github.com/senapk/tko#tko).

---

![_](https://raw.githubusercontent.com/qxcodeed/arcade/master/base/triangulo/cover.jpg)

Dado um vetor de inteiros A, imprima um triângulo de números tal que na base do triângulo estejam todos os elementos do vetor original, e tal que, a cada i-ésimo nível acima da base, o número de elementos seja um a menos que no nível inferior e cada elemento do i-ésimo nível seja a soma de dois elementos consecutivos do nível inferior.

- Entrada
  - Os elementos da base.
- Saída
  - O triângulo.

## Dica

Veja a resolução da atividade "Empilhamento da Recursão" para entender como funciona a impressão de trás pra frente.

## Arquivos

Você deve implementar a função `processa` no arquivo `lib.cpp`.

<!-- links .cache/draft -->
- cpp
  - [lib.cpp](https://github.com/qxcodeed/arcade/blob/master/base/triangulo/.cache/draft/cpp/lib.cpp)
  - [lib.hpp](https://github.com/qxcodeed/arcade/blob/master/base/triangulo/.cache/draft/cpp/lib.hpp)
  - [main.cpp](https://github.com/qxcodeed/arcade/blob/master/base/triangulo/.cache/draft/cpp/main.cpp)
<!-- links -->

## Testes

```txt

>>>>>>>> 01
1 2 3
========
[ 8 ]
[ 3 5 ]
[ 1 2 3 ]
<<<<<<<<

>>>>>>>> 02
3 2 1
========
[ 8 ]
[ 5 3 ]
[ 3 2 1 ]
<<<<<<<<

>>>>>>>> 03
4 3 2 1
========
[ 20 ]
[ 12 8 ]
[ 7 5 3 ]
[ 4 3 2 1 ]
<<<<<<<<

>>>>>>>> 04
1 1 2 3 5 8
========
[ 89 ]
[ 34 55 ]
[ 13 21 34 ]
[ 5 8 13 21 ]
[ 2 3 5 8 13 ]
[ 1 1 2 3 5 8 ]
<<<<<<<<

```
