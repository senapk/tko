# Instalação no Linux

## Instalação básica

### Instalando o Python e o pipx

```bash
# ubuntu e wsl
sudo apt install -y python3-pip pipx
# arch
sudo pacman -S python-pipx
```

### Instalando o tko

```bash
# instalando o tko
pip  install tko  # versões antigas do ubuntu
pipx install tko  # arch e versões mais novas do ubuntu

# Em algumas distros, o pip(x) não adiciona o path dos binários instalados localmente.
# Se ao executar o comando tko você receber um erro de comando não encontrado
# execute o comando abaixo
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

## Atualizando seu tko

Para atualizar, basta executar o comando:

```bash
pip install tko --upgrade # versões antigas do ubuntu
pipx upgrade tko          # arch, ubuntu e wsl
```

## Instalando os compiladores

- Você pode utilizar qualquer outra linguagens que quiser, basta instalar o compilador correspondente e definir o comando de compilação e execução correspondentes.

### WSL e Ubuntu

```bash
# C e C++
sudo apt install build-essential
# Python
sudo apt install python3
# Java
sudo apt install openjdk-11-jdk
# Typescript
sudo apt install nodejs
npm install --save-dev @types/node
npm install typescript esbuild readline-sync
```

### Arch

```bash
# C e C++
sudo pacman -S base-devel
# Python
sudo pacman -S python3
# Java
sudo pacman -S jdk-openjdk
# Typescript
sudo pacman -S nodejs
npm install --save-dev @types/node
npm install typescript esbuild readline-sync
```
