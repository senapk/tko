# Outros sistemas operacionais

Você vai precisar descobrir como instalar o git, python, o pipx, o vscode e os compiladores. Tudo precisa estar no path do sistema.

## Exemplo de instalação no Arch Linux e Derivados:

```bash

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
```
