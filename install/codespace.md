
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

## Adicionando alguns atalhos no bash

Abra o arquivo de configurações do bash

```bash
code ~/.bashrc
```

Vá até o final do arquivo e cole as seguintes linhas

```bash
alias update='pip install tko --upgrade'
alias play='tko play'
alias run='tko run'
```

Reinicie o terminal com Control D para reiniciar o bash

## Salvando os dados no repositório

- Vá no botão de controle de versão.
- Clique em "Stage All Changes".
- Digite uma mensagem no campo de mensagem.
- Clique em "Commit && Push".
