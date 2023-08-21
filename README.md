# tko - Test Kit Operations

Para rodar os baixar e executar os testes diretamente do seu computador, você precisará do `python` instalado e do `tko` instalado.

O python já vem instalado no linux e no mac. Para instalar no windows, baixe o instalador no site oficial: [https://www.python.org/downloads/](https://www.python.org/downloads/).

Instale o `tko` utilizando o `pip`, o gerenciador de pacotes do python:

```bash
# baixando do repositório oficial
pip install tko

# ou baixar diretamente do github
pip install git+https://github.com/senapk/tko.git 
```

![image](https://user-images.githubusercontent.com/4747652/262040621-1f3166b1-a6e8-47a0-b48c-f86ca45aad83.png)

## Install in Replit

Se não pode instalar o compilador no seu computador, ou vai programar pelo celular, você pode utilizar o replit para rodar os testes. Para isso, siga as instruções do link: [Replit tko Install](replit/Readme.md)

## Para baixar a descrição das atividades e os testes

- Para baixar a atividade do carro do repositório de POO(Programação Orientada a Objetos): [@002 Carro](https://github.com/qxcodepoo/arcade/blob/master/base/002/Readme.md#carro) para `java`:

```bash
# Você informa o repositório `poo`
# a questão `002`
# e a linguagem `java`, `cpp`, `ts`
# tko down _repo_ _questao_ _linguagem_
tko down poo 002 java
```

![image](https://user-images.githubusercontent.com/4747652/262017247-3e765618-19e7-47bb-9e91-ab0b03bc2834.png)

### Para rodar os testes

Você precisará do compilador próprio da linguagem que for programar, instale manualmente no seu sistema. Se estiver no replit, o template da linguagem já vem com o compilador instalado.

- c/c++: `gcc` ou `g++`
- java: `javac`
- python: `python3`
- javascript: `node`
- typescript: `esbuild`

Ao baixar a questão, você terá os seguintes arquivos:

- Readme.md: com a descrição da atividade.
- cases.tio: com os casos de teste.
- draft.ext: com o rascunho da solução.

Renomeie o arquivo `draft.ext` para o nome apropriado e edite com a sua solução. Para rodar os testes, utilize o comando:

```bash
# tko run _arquivos_de_codigo _arquivo_de_casos_de_teste
tko run Solver.java cases.tio
```

![image](https://user-images.githubusercontent.com/4747652/262017881-bdbdeb37-d287-46c4-92fe-d50f279477ae.png)

No exemplo da imagem acima, como o código não compilou corretamente, foram apresentados os erros de compilação.

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

### Listando os testes

- Salve o arquivo `testes.tio`.
- Abra o terminal na pasta onde colocou o arquivo.
- Para simplificar, certifique-se que só existe esse arquivo na pasta.
- O comando `tko` funciona com subcomandos.
- O subcomando `tko list` mostra os testes.
  - Mostrando os testes: `tko list testes.tio`
  - Opções:
    - `-i ou --index`: um índice específico

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
