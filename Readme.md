# tko

O TKO é um sistema de testes para programação competitiva. Ele é capaz de rodar testes em várias linguagens de programação e em vários formatos de testes. Ele está integrado com os repositórios de atividades das disciplinas de programação da UFC de Quixadá permitindo baixar as atividades e rodar os testes.

- [FUP - Fundamentos de Programação](https://github.com/qxcodefup/arcade)
- [ED - Estrutura de Dados](https://github.com/qxcodeed/arcade)
- [POO - Programação Orientada a Objetos](https://github.com/qxcodepoo/arcade)

## Instalação

| [Windows](install/windows.md) | [Linux](install/linux.md) | [Replit](replit/Readme.md) | [Codespace](install/codespace.md) |
| ------- | ----- | ------ | --------- |
| [![_](install/windows.jpg)](install/windows.md) | [![_](install/linux.jpg)](install/linux.md)       | [![_](install/replit.jpg)](replit/Readme.md) | [![_](install/codespace.jpg)](install/codespace.md) |

```bash
# instalar utilizando o gerenciador de pacotes do python
pip install tko
```

## Para baixar a descrição das atividades e os testes

- Para baixar a atividade do carro do repositório de POO(Programação Orientada a Objetos): [contrua seu primeiro @carro](https://github.com/qxcodepoo/arcade/blob/master/base/carro/Readme.md) para `java`:

```bash
# Você informa o repositório `poo` o problema `carro`
# tko down _course _activity
tko down poo carro
```

### Para rodar os testes

Você precisará do compilador próprio da linguagem que for programar, instale manualmente no seu sistema. Se estiver no replit, o template da linguagem já vem com o compilador instalado.

- c/c++: `gcc` ou `g++`
- java: `javac`
- python: `python3`
- javascript: `node`
- typescript: `esbuild` e `node`

Ao baixar a questão, você terá os seguintes arquivos:

- Readme.md: com a descrição da atividade.
- cases.tio: com os casos de teste.
- draft.ext: com o rascunho da solução.

Renomeie o arquivo `draft.ext` para o nome apropriado e edite com a sua solução. Para rodar os testes, utilize o comando:

```bash
# tko run _arquivos_de_codigo _arquivo_de_casos_de_teste
tko run Solver.java cases.tio
```

### Verificando o resultado

Após fazer uma parte do código, executamos os testes novamente. Agora ele compila e mostra:

- Quantos testes passaram.
- O nome e o índice dos testes que falharam.
- O diff do primeiro teste que falhou
  - resultado esperado (lado esquerdo), resultado obtido (lado direito).
- O diff da primeira linha diferente renderizando os whitespaces.

![image](https://user-images.githubusercontent.com/4747652/262019524-eef3035a-6132-4151-9f5f-6945294e173d.png)

### Opções extras

- Caso queira rodar apenas um índice de teste, utilize a opção `-i`:

```bash
tko run Solver.java cases.tio -i 1
```

- Caso queira o diff `up down` ao invés de `left right`, utilize a opção `-v`:

```bash
tko run Solver.java cases.tio -v
```

## O que é um teste?

- Um teste define qual o comportamento esperado de um programa determinístico. Para uma determinada entrada, o programa deve gerar **sempre** a mesma saída.
- A entrada e saída e o comportamento esperado devem ser bem definidos, por exemplo:
  - Dados dois números inteiros de entrada, um por linha, mostre o resultado da divisão. Se o resultado for inteiro, mostre o valor inteiro, se for flutuante, mostre com duas casas decimais.

## Formatos de teste

- Um arquivo de texto com vários testes:
  - modelo TIO(test input output).
  - modelo VPL que é utilizado no plugin do moodle.
- Uma pasta com um dois arquivos para cada teste, um arquivo com a entrada e outro com a saída.
  - modelo maratona:
    - Arquivos .in e .out
    - Arquivos .in e .sol

---

### Sintaxe TIO

```txt
>>>>>>>>
entrada
...
========
saída
...
<<<<<<<<

>>>>>>>>
entrada
...
========
saída
...
<<<<<<<<
```

---

### Escrevendo alguns testes

Vamos escrever alguns testes para o problema proposto. Crie um arquivo chamado `testes.tio` e vamos inserir algumas entradas para o problema proposto.

```txt
>>>>>>>>
4
2
========
2
<<<<<<<<

>>>>>>>>
3
2
========
1.50
<<<<<<<<

>>>>>>>>
5
4
========
1.25
<<<<<<<<

>>>>>>>>
1
3
========
0.33
<<<<<<<<
```

---

## Testando um código com erros

- Crie algum código que tenta resolver o problema.

```python
# solver.py
a = int(input())
b = int(input())
print(a/b)
```

```c
// solver.c
#include <stdio.h>
int main(){
    int a = 0, b = 0;
    scanf("%d %d", &a, &b);
    printf("%d\n", (a/b));
}
```

- Rodando diretamente passando o código fonte
  - `tko run solver.c testes.tio`: compila e testa seu código.
  - `tko run solver.py testes.tio`: chama o interpretador e testa o código.
  - `tko run "python2 solver.py" testes.tio`.
- Se pode compilar manualmente e passar o executável em qualquer linguagem. Se passar o código fonte, o script vai compilar com muitos critérios restritivos para garantir que seu código esteja bem feito.

## Executando

- Opções extras:
  - As mesmas do list:
    - `-i ou --index`: roda um índice específico
    - `-a ou --all`: mostra todos os testes que falharam e não apenas o primeiro.

- Vamos consertar nosso código

```c
// solver.c
#include <stdio.h>
int main(){
    int a = 0, b = 0;
    scanf("%d %d", &a, &b);
    if(a % b == 0)
        printf("%d\n", (a/b));
    else
        printf("%.2f\n", (float)a/b);
}
```

- Rode agora e ele deve mostrar que todos os testes foram sucesso.

---

## Convertendo entre formatos

- Gerando um `.vpl`
  - `tko build t.vpl testes.tio`

## Exemplos rápidos

```bash
# mostra os testes
tko list t.tio

# roda o executável solver.c e usa o arquivo t.tio como pacote de testes
tko run solver.c t.tio

# se seus testes estiverem em arquivos com a extensão .tio ou .vpl ou .md
# para listar basta digitar
tko list cases.tio

# roda apenas o teste número 3
tko run solver.py t.tio -i 3

# ou então rodar usando
tko run solver.cpp "testes @.in @.sol"

```
