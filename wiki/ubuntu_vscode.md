# VS Code no Ubuntu / WSL

Este guia define a meta de integração entre VS Code e o ambiente Linux usado pelo TKO.

No Windows, o caminho recomendado é instalar o VS Code no Windows e abrir as pastas do Ubuntu via WSL. No Ubuntu nativo, o VS Code pode ser instalado diretamente no sistema.

## Meta do ambiente

Ao final, você deve conseguir:

- abrir o VS Code;
- abrir uma pasta do Ubuntu/WSL com `code .`;
- usar o terminal integrado do VS Code no mesmo ambiente onde o TKO está instalado;
- editar arquivos da disciplina sem copiar arquivos entre Windows e Linux.

Se algum passo falhar, consulte a documentação atual do VS Code para Ubuntu ou WSL. O objetivo é garantir a integração, não seguir um comando específico.

## Windows com WSL

1. Instale o VS Code no Windows.
2. Instale a extensão WSL:

```powershell
code --install-extension ms-vscode-remote.remote-wsl
```

3. Abra o Ubuntu.
4. Entre na pasta do projeto.
5. Execute:

```bash
code .
```

O VS Code deve abrir mostrando `WSL: Ubuntu` na barra inferior.

## Ubuntu nativo

Instale o VS Code usando um método adequado para sua distribuição:

- pacote `.deb` oficial;
- repositório oficial da Microsoft;
- loja ou gerenciador gráfico da distribuição;
- outro método recomendado pela instituição.

Depois, verifique no terminal:

```bash
code --version
```

Abra a pasta atual:

```bash
code .
```

## Checklist de verificação

No terminal usado pelo aluno:

```bash
code --version
tko --version
```

Dentro do VS Code, abra o terminal integrado e confira:

```bash
pwd
tko --version
```

O terminal integrado deve estar no ambiente Ubuntu/WSL, não no PowerShell do Windows, quando a turma estiver usando WSL.
