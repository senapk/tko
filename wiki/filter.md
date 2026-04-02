# Documentação -- Operadores de Corte (ADD, DEL, COM, ACT)

A ferramenta utiliza **marcadores em comentários** para definir como
partes do código serão tratadas durante a filtragem.

Os operadores funcionam por **escopo de indentação**.\
Ou seja, o comando é **persistente** e continua valendo para todas as
linhas abaixo **até que a indentação diminua**, encerrando o bloco onde
o operador foi definido.

Exemplo: se um `DEL!` for colocado no início de uma função, todo o
conteúdo da função será removido. Quando a indentação voltar ao nível
anterior (fim da função), o efeito do `DEL!` termina.

------------------------------------------------------------------------

## Operadores disponíveis

  Operador   Nome       Função
  ---------- ---------- ---------------------
  ADD!       Add        Mantém o código
  DEL!       Delete     Remove o código
  COM!       Comment    Comenta o código
  ACT!       Activate   Descomenta o código

Os marcadores devem ser escritos como comentário da linguagem:

Exemplo em Python:

``` python
# ADD!
# DEL!
# COM!
# ACT!
```

Exemplo em C/Java/Go:

``` c
// ADD!
// DEL!
// COM!
// ACT!
```

------------------------------------------------------------------------

## Escopo por indentação (Persistência)

O operador continua ativo até que a indentação diminua.

### Exemplo

Entrada:

``` python
def exemplo():
    # DEL!
    print("linha 1")
    print("linha 2")
    if True:
        print("linha 3")

print("fora da função")
```

Saída:

``` python
print("fora da função")
```

O `DEL!` afetou toda a função porque foi definido dentro do escopo dela.

------------------------------------------------------------------------

## ADD! -- Manter código

Mantém o código normalmente no arquivo final.

Entrada:

``` python
# ADD!
print("Esse código aparece")
```

Saída:

``` python
print("Esse código aparece")
```

------------------------------------------------------------------------

## DEL! -- Remover código

Remove todas as linhas dentro do escopo.

Entrada:

``` python
# DEL!
print("Esse código será removido")
```

Saída:

``` python
# removido
```

------------------------------------------------------------------------

## COM! -- Comentar código

Comenta todas as linhas do escopo.

Entrada:

``` python
# COM!
print("Linha 1")
print("Linha 2")
```

Saída:

``` python
# print("Linha 1")
# print("Linha 2")
```

------------------------------------------------------------------------

## ACT! -- Ativar código (Descomentar)

Remove o comentário das linhas do escopo.

Entrada:

``` python
# ACT!
# print("Linha 1")
# print("Linha 2")
```

Saída:

``` python
print("Linha 1")
print("Linha 2")
```

------------------------------------------------------------------------

## Operador inline (apenas uma linha)

Também é possível aplicar o operador apenas a uma linha colocando o
marcador no final da linha.

Entrada:

``` python
print("Normal")
print("Remover")  # DEL!
print("Comentar") # COM!
# print("Ativar") # ACT!
```

Saída:

``` python
print("Normal")
# print("Comentar")
print("Ativar")
```

------------------------------------------------------------------------

## Resumo rápido

  Operador   Efeito
  ---------- ------------
  ADD!       Mantém
  DEL!       Remove
  COM!       Comenta
  ACT!       Descomenta

------------------------------------------------------------------------

## Uso típico

-   Criar versões diferentes do mesmo código
-   Material didático (professor vs aluno)
-   Feature flags
-   Ocultar soluções
-   Gerar drafts automaticamente
