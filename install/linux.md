# Instalação no Linux

## Ubuntu

### Instalação básica

Para instalar, no ubuntu, debian e derivados, execute o comando:

```bash
sudo apt install python3-pip
pip install tko

echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Atualizar

Para atualizar, basta executar o comando:

```bash
pip install tko --force
```

### Instalando os compiladores

Para instalar com compiladores das linguagens que você for utilizar, execute o comando:

```bash

## se for usar nodejs
sudo apt install nodejs

## se for utilizar typescript
npm install -g esbuild
npm i --save-dev @types/node
npm install readline-sync

## se for utilizar java
sudo apt install openjdk-11-jdk

## se for utilizar g++ ou gcc
sudo apt install build-essential

## se for utilizar python
sudo apt install python3
```

## Arch e Manjaro

### Instalação básica Arch

No arch e manjaro, execute o comando:

```bash
sudo pacman -S python-pip
pipx install tko
```

### Atualizar no arch

Para atualizar, basta executar o comando:

```bash
pipx install tko --force
```

### Instalando os compiladores no Arch

Para instalar com compiladores das linguagens que você for utilizar, execute o comando:

```bash
## nodejs
sudo pacman -S nodejs

## typescript
npm install -g esbuild
npm i --save-dev @types/node
npm install readline-sync

## java
sudo pacman -S jdk-openjdk

## g++ ou gcc
sudo pacman -S base-devel

```
