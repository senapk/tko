<!-- markdownlint-configure-file {
  "MD033": false,
  "MD041": false
} -->

# tko

O tko é um sistema de testes para programação competitiva. Ele é capaz de rodar testes em várias linguagens de programação e em vários formatos de testes. Ele está integrado com os repositórios de atividades das disciplinas de programação da UFC de Quixadá permitindo baixar as atividades e rodar os testes.

- [FUP - Fundamentos de Programação](https://github.com/qxcodefup/arcade)
- [ED - Estrutura de Dados](https://github.com/qxcodeed/arcade)
- [POO - Programação Orientada a Objetos](https://github.com/qxcodepoo/arcade)

## Instalação

### Windows SEM WSL

- Instale o python pelo instalador do site oficial.
- Marque a caixinha opção para adicionar o python ao path quando for instalar. `Add python.exe to PATH`
- Abra o powershell e digite:

```bash
pip install pipx
pipx install tko
pipx ensurepath
```

- Reinicie o powershell. Sempre que quiser atualizar o `tko`, basta executar o comando `pipx upgrade tko`.
- Sem o WSL, você precisará instalar manualmente os compiladores que precisar, por exemplo, o `g++` para C++, o `javac` para Java, o `python` para Python e o `node e npm` para Typescript.

### Windows via WSL

- Vamos instalar o WSL. Abra o powershell e digite

```bash
wsl --install
```

- Aceite as opções e espere terminar a instalação. Reinicie o computador.
- Agora vamos configurar o vscode pra funcionar com o WSL.
- Instale o vscode normalmente pelo windows.
- Abra o vscode pelo windows e instale a extensão WSL com 30 M de downloads
- No lançador de aplicativos do windows, procure por "WSL" e abra o terminal do ubuntu
- Digite o comando abaixo em qualquer pasta para configurar vscode no ubuntu

```bash
code .
```

- Esse comando irá instalar os componenetes necessários para abrir o vscode pelo wsl.
- Agora, sempre que quiser abrir um repositório, abra o terminal do ubuntu, navegue até a pasta do repositório e execute o comando `code .`
- Vamos seguir para falta o tko e os compiladores no seu novo linux ubuntu no wsl.

### Instalando o Python, pipx e o tko e ferramentas básicas de desenvolvimento

#### Windows com WSL e Ubuntu

```bash
# Instalando as ferramentas básicas de desenvolvimento
sudo apt update && sudo apt install -y build-essential pipx wslu
# Configurando o web browser
grep -qxF 'export BROWSER="wslview"' ~/.bashrc || echo 'export BROWSER="wslview"' >> ~/.bashrc
# Instalando o tko
pipx install tko
# Adicionando o tko no path
grep -qxF 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
# Reinicie o terminal
# Teste a instalação com o comando
tko --version

# Instale os compiladores que você precisar
# C, C++, Python já vem com o build-essential
# Java
sudo apt install openjdk-11-jdk
# Node e npm
sudo apt install nodejs npm
# Typescript
sudo apt install nodejs npm
npm install --save-dev @types/node
npm install typescript esbuild readline-sync
# Go
sudo apt install golang -y
```

#### Arch Linux e Derivados

```bash
# Instalando as ferramentas básicas de desenvolvimento
sudo pacman -S --noconfirm base-devel python-pipx
# Adicionando o tko no path
grep -qxF 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
# Reinicie o terminal
# Instalando o tko
pipx install tko
# Teste a instalação com o comando
tko --version

# Instale os compiladores que você precisar
# C, C++, Python já vem com o base-devel

# Java
sudo pacman -S jdk-openjdk
# Node e npm
sudo pacman -S nodejs npm
# Typescript
sudo pacman -S nodejs npm
npm install --save-dev @types/node
npm install typescript esbuild readline-sync
# Go
sudo pacman -S go
```

#### Codespaces

```bash
sudo apt update && sudo apt install -y python3-pip && pip install pipx && pipx install tko
# Os compiladores, você pode usar os comandos do wsl/ubuntu
```

### Outros sistemas operacionais

- Basta instalar o python e o pipx. Depois, instale o tko com o comando `pipx install tko`.
- Para instalar os compiladores, você pode usar o gerenciador de pacotes do seu sistema operacional. Por exemplo, no MacOS, você pode usar o Homebrew para instalar o python, g++, java, node e npm.

## Atualizando o tko

Para atualizar o tko para versão mais recente, basta executar o comando:

```bash
pipx upgrade tko          # windows, codespace, arch, ubuntu e wsl
```

## Para interagir com os repositórios, navegar, baixar, testar

Os `[]` e `<>` indicam onde devem ser colocados os parâmetros. Os `|` indicam opções.

```bash
# primeiro crie um repositório local na pasta local
tko init --remote [poo | fup | ed]
# exemplo tko init --remote fup

# agora abra o repositório para interagir com ele
tko open <pasta_do_repositório>
# exemplo: tko open fup

```

## Programando em uma linguagem diferente de C, C++, Java, Python e Typescript

- Qual for escolher a linguagem que deseja utilizar, escolha `yaml`. Na pasta de cada atividade será criado um arquivo de rascunho chamado `draft.yaml` com os seguintes campos:

```yaml
build:
run:
```

- Preencha os campos `build` e `run` com os comandos de compilação e execução da sua linguagem. Exemplo, em c++ para um arquivo fonte chamado solver.cpp, o `draft.yaml` ficaria assim:

```yaml
build: g++ -Wall solver.cpp -o solver.out
run: ./solver.out
```

Adapte para os comandos da sua linguagem e o nome dos arquivos da pasta.

## Criando os testes

### Descompactando os testes

Se preferir trabalhar com o modelo de testes em arquivos separados, você pode descompactar o arquivo `cases.tio` para uma pasta com os arquivos de entrada e saída. Será gerado um arquivo `.in` e um `.sol` para cada teste.

```bash
$ mkdir pasta
$ tko build pasta cases.tio
$ ls pasta
00.in 00.sol 01.in 01.sol 02.in 02.sol 03.in 03.sol 04.in 04.sol
```

Para rodar a partir da pasta com os testes descompactados, basta passar o nome da pasta como parâmetro.

```bash
tko run Solver.java pasta
```

Se quiser utilizar um nome padrão diferente para leitura ou escrita das pastas, veja a seção de [Convertendo entre formatos](#convertendo-entre-formatos).

## Convertendo entre formatos

- Gerando um `t.vpl`
  - `tko build t.vpl testes.tio`
- Gerando um `t.tio` a partir do `Readme.md`e de um `extra.tio`.
  - `tko build t.tio Readme.md extra.tio`
- Para extrair os testes para uma pasta com um arquivo para entrada e outro para saída, crie uma pasta vazia e passe para o primeiro parâmetro do `tko build`.

```bash
$ ls
cases.tio  draft.c  Readme.md
$ mkdir pasta
$ tko build pasta cases.tio 
$ ls pasta/
00.in   02.sol  05.in   07.sol  10.in   12.sol  15.in   17.sol  20.in   22.sol
00.sol  03.in   05.sol  08.in   10.sol  13.in   15.sol  18.in   20.sol  23.in
01.in   03.sol  06.in   08.sol  11.in   13.sol  16.in   18.sol  21.in   23.sol
01.sol  04.in   06.sol  09.in   11.sol  14.in   16.sol  19.in   21.sol
02.in   04.sol  07.in   09.sol  12.in   14.sol  17.in   19.sol  22.in
```

- Você pode definir o padrão de nome dos arquivos gerados com `-p "@ @"`, sendo @ o wildcard que representa a numeração dos arquivo.
  - Vamos refazer o comando acima, mas colocando "-p in.@ out.@"

```bash
$ tko build pasta/ cases.tio -p "in.@ out.@"
$ ls pasta/
in.00  in.05  in.10  in.15  in.20   out.01  out.06  out.11  out.16  out.21
in.01  in.06  in.11  in.16  in.21   out.02  out.07  out.12  out.17  out.22
in.02  in.07  in.12  in.17  in.22   out.03  out.08  out.13  out.18  out.23
in.03  in.08  in.13  in.18  in.23   out.04  out.09  out.14  out.19
in.04  in.09  in.14  in.19  out.00  out.05  out.10  out.15  out.20
```

- O `pattern` é útil para converter os formatos de Maratona, que vem em múltiplos arquivos para o `.tio`. Basta fazer o `match` do modelo que eles utilizarem.
  - `-p "@.in @.out"`
  - `-p "in@ out@"`
  - entre outros.
