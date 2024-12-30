
import unittest
from rota.run.loader import Loader
from rota.run.unit import Unit

readme_text = """
# É positivo

![_](https://raw.githubusercontent.com/qxcodefup/arcade/master/base/positivo/cover.jpg)

## Contexto

Em muitas aplicações, precisamos verificar se um número é positivo ou não para tomar decisões. Por exemplo, ao validar se uma quantidade ou saldo está em condições aceitáveis.

Implemente um programa que recebe um número inteiro e imprime "SIM" se o número for maior ou igual a zero. Caso contrário, o programa apenas imprimirá uma linha vazia.

### Entrada

- Um número inteiro.

### Saída

- "SIM" se o número for maior ou igual a zero, caso contrário, apenas uma quebra de linha.

## Testes

```py
>>>>>>>> INSERT quebra

======== EXPECT

<<<<<<<< FINISH
```

```py
>>>>>>>> INSERT vazios
======== EXPECT
<<<<<<<< FINISH
```

```py
>>>>>>>> INSERT
-3
======== EXPECT

<<<<<<<< FINISH
```

```py
>>>>>>>> INSERT 3
======== EXPECT
SIM
<<<<<<<< FINISH
```

```py
>>>>>>>> INSERT 4
0
======== EXPECT
SIM
<<<<<<<< FINISH
```

"""



class TestSimple(unittest.TestCase):
    def test_tio_loader(self):
        unit_list: list[Unit] = Loader.parse_tio(readme_text, "string")

        assert len(unit_list) == 5
        assert unit_list[0].case == "quebra"
        assert unit_list[0].inserted == "\n"
        assert unit_list[0].expected == "\n"

        assert unit_list[1].case == "vazios"
        assert unit_list[1].inserted == ""
        assert unit_list[1].expected == ""

        assert unit_list[2].case == ""
        assert unit_list[2].inserted == "-3\n"
        assert unit_list[2].expected == "\n"

        assert unit_list[3].case == "3"
        assert unit_list[3].inserted == ""
        assert unit_list[3].expected == "SIM\n"



if __name__ == "__main__":
    unittest.main()
