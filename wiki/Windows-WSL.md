# Windows - Vscode e WSL

## Visual Studio Code  

O Visual Studio Code (VS Code) é um editor de código fonte utilizado por programadores para escrever, editar depurar e organizar projetos de software em diversas linguagens.  


1. Acesse: [Visual Studio Code Download](https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user)
2. Execute o instalador
3. Siga as instruções do instalador

**Atenção!:** certifique-se de que as duas últimas opções estão marcadas, elas te pouparão muito trabalho no futuro.

![vsc](Images/VSC.jpg)

Abra o powershell para testar a instalação e instalar a extensão do WSL para o vscode. Digite o comando abaixo:

```bash
code --install-extension ms-vscode-remote.remote-wsl
```

## WSL (Windows Subsystem for Linux)

O WSL (Windows Subsystem for Linux) é um recurso do Windows que permite rodar uma distribuição Linux (como Ubuntu) diretamente dentro do Windows, sem precisar de máquina virtual ou dual boot. Neste guia mostrarei como habilitar o WSL no Windows e instalar uma distribuição Linux. Para realizar a instalação do WSL será necessário seguir os seguintes passos

- Abra o terminal **PowerShell como Administrador**.
- Digite o comando abaixo e aperte Enter:

```powershell
wsl --install
```

Esse comando instala o WSL2 com a distribuição Ubuntu por padrão.

- **Reinicie** seu computador após a instalação.
- Abra e configure o Ubuntu
- Na primeira vez que abrir o Ubuntu, ele vai pedir para criar um nome de usuário e senha Linux. Pode ser qualquer um (não precisa ser igual ao do Windows).

### Configurações extras

Para verificar e instalar as atualizações, abra o terminal Ubuntu (digite "Ubuntu" no menu Iniciar) e execute:

```bash
sudo apt update && sudo apt upgrade -y
# Agora abra o vscode para finalizar a integração
code .
# ferramentas básicas de desenvolvimento e integração do wsl com o navegador
sudo apt update && sudo apt install -y build-essential wslu
# Configurando o web browser
grep -qxF 'export BROWSER="wslview"' ~/.bashrc || echo 'export BROWSER="wslview"' >> ~/.bashrc
```
