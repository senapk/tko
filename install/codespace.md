
# Instalação no Codespace

## Criando um Codespace

- Crie um repositório no github.
- Na tela de criação, marque a opção para iniciar o repositório com um Readme.
- Finalize a criação do repositório.
- Clique em Code, depois em iniciar codespace.
- Sempre que quiser acessar o codespace, basta clicar em Code e depois clicar no nome do codespace que você criou.

## Instalando o TKO

Depois de criar o codespace, abra o terminal e execute o comando:

```bash

pip install tko

# depois de instalado, defina a pasta atual 
# como padrão para download

tko config --root .
```

## Instalando ferramentas para linguagens de programação

Python, c, c++, javascript, java e go não precisam de nenhum software adicional.

Para typescript, você precisa instalar o `esbuild`.

```bash
npm install -g esbuild
npm i --save-dev @types/node
```

## Salvando os dados no repositório

- Vá no botão de controle de versão.
- Clique em "Stage All Changes".
- Digite uma mensagem no campo de mensagem.
- Clique em "Commit && Push".

## Adicionando alguns atalhos no bash

Abra o terminal, instale o fzf

```bash
sudo apt install fzf
```

Agora abra o arquivo de configuração do bash

```bash
code ~/.bashrc
```

Vá até o final do arquivo e cole as seguintes linhas

```bash
alias update='pip install tko --upgrade'
alias play='tko play'
alias run='tko run'
alias cz="cd \$(find . -type d | fzf)"
```

Reinicie o terminal com Control D para reiniciar o bash

## Personalizando o seu vscode

Mudando a fonte do editor

Primeiro vamos criar a pasta para instalar nossas fontes personalizadas

```bash
mkdir ~/.fonts
```

- Você pode escolher uma fonte da lista [LISTA](https://www.nerdfonts.com/font-downloads).
- Copie o link de download.
- Abra o terminal
- Navegue até a pasta
- Use o `wget` para baixar o link
- Use o `unzip` para descompactar
- Digite `fc-cache -fv` para atualizar as fontes.
- Abra as configurações do `vscode` usando Control Vírgula
- Digite Font Family
- Adicione o nome da sua fonte tal como no exemplo abaixo.

Exemplo com a fonte ComicShanns

```bash
cd ~/.fonts
wget https://github.com/ryanoasis/nerd-fonts/releases/download/v3.2.1/ComicShannsMono.zip
unzip ComicShannsMono.zip 
fc-cache -fv
```

Abrindo as configurações do vscode e adicionando em FontFamily o valor:

- `'ComicShannsMono Nerd Font', 'Droid Sans Mono', 'monospace', monospace"`
