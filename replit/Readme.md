# Replit tko Install

- Crie um Replit com a linguagem desejada.
- Copie o comando de instalação abaixo:

```bash
curl -sSL https://raw.githubusercontent.com/senapk/tko/master/replit/update.sh | bash
```

- Abra o Shell do replit, cole o comando com `Control Shift V` e dê enter.
- Dê Control D e espere a instalação terminar.
- Inicie o aplicativo digitando `tko play [fup | ed | poo]`
- Por exemplo, se sua disciplina é fup, digite `tko play fup`.

<!--
## C++

```bash
curl -sSL https://raw.githubusercontent.com/senapk/tko/master/replit/cpp/update.sh | bash
```

## C

```bash
curl -sSL https://raw.githubusercontent.com/senapk/tko/master/replit/c/update.sh | bash
```

## Java

```bash
curl -sSL https://raw.githubusercontent.com/senapk/tko/master/replit/java/update.sh | bash
```

## Javascript

```bash
curl -sSL https://raw.githubusercontent.com/senapk/tko/master/replit/js/update.sh | bash
```

## Typescript

```bash
curl -sSL https://raw.githubusercontent.com/senapk/tko/master/replit/ts/update.sh | bash
```

## Python

```bash
curl -sSL https://raw.githubusercontent.com/senapk/tko/master/replit/py/update.sh | bash
```

## Configuração genérica para qualquer linguagem

- Crie um replit da linguagem desejada
- Abra o arquivo `replit.nix`, se não existir, crie:

```bash
code replit.nix
```

Se não existir, coloque esse conteúdo no arquivo. Se já existir, adicione os pacotes abaixo.

```bash
### 
{pkgs}: {
  deps = [
    pkgs.graphviz
    pkgs.python310Full
  ];
}
```

Após isso, salve o arquivo, e execute a seguinte linha no terminal.

```bash
curl -sSL https://raw.githubusercontent.com/senapk/tko/master/replit/update.sh | bash
```

Execute o comando:
-->
