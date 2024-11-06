# Instalação no Linux

## Instalação básica

```bash
# instalando o python
sudo apt install python3 python3-pip # no ubuntu e derivados
sudo pacman -S python-pip            # arch e derivados

# instalando o tko
pip  install tko  # versões antigas do ubuntu
pipx install tko  # arch e versões mais novas do ubuntu

# Em algumas distros, o pip(x) não adiciona o path dos binários instalados localmente.
# Se ao executar o comando tko você receber um erro de comando não encontrado
# execute o comando abaixo
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Atualizando seu tko

Para atualizar, basta executar o comando:

```bash
pip install tko --upgrade # versões antigas do ubuntu
pipx upgrade tko          # arch e versões mais novas do ubuntu
```

### Instalando os compiladores (node, c, c++ e java)

Para instalar com compiladores das linguagens que você for utilizar, execute o comando apropriado

- Ubuntu

```bash
## se for usar nodejs
sudo apt install nodejs
## se for utilizar java
sudo apt install openjdk-11-jdk
## se for utilizar g++ ou gcc
sudo apt install build-essential
```

- Arch

Para instalar com compiladores das linguagens que você for utilizar, execute o comando:

```bash
## nodejs
sudo pacman -S nodejs
## java
sudo pacman -S jdk-openjdk
## g++ ou gcc
sudo pacman -S base-devel

```

### Typescript

Navegue até a pasta onde quer instalar os módulos do node e execute os comandos.

```bash
npm install --save-dev @types/node
npm install typescript esbuild readline-sync
```
