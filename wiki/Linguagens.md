# Instando os compiladores e interpretadores

## Java no Linux / WSL

```bash
# instalando o JDK e JRE
sudo apt install default-jre default-jdk -y
code --install-extension redhat.java

# reinicie o terminal e teste a instalação
java -version
javac -version
``` 

## Go no Linux / WSL

```bash
curl -fsSL https://go.dev/dl/go1.26.0.linux-amd64.tar.gz -o ~/go.tar.gz
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf ~/go.tar.gz

grep -qxF 'export PATH=$PATH:/usr/local/go/bin' ~/.bashrc || \
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc

code --install-extension golang.Go

# reinicie o terminal e teste a instalação
go version

# instale o pacote para debug
go install github.com/go-delve/delve/cmd/dlv@latest
# configure o vscode para usar o dlv como depurador rodando o arquivo individual
```

Na sua pasta de projeto, crie uma pasta .vscode e dentro dela um arquivo launch.json com a seguinte configuração. Ela vai permitir utilizar o terminal integrado do vscode para depurar seus arquivos go usando o dlv.

```bash
mkdir -p .vscode
code .vscode/launch.json
```

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug current file",
            "type": "go",
            "request": "launch",
            "mode": "debug",
            "program": "${file}",
            "console": "integratedTerminal",
            "env": {
                "GO111MODULE": "off"
            }
        }
    ]
}
```

## Typescript no Linux / WSL

```bash
# Instale o vscode extension para typescript
code --install-extension ms-vscode.vscode-typescript-next

# Instale o nodejs e npm
sudo apt install nodejs npm -y
sudo npm install -g typescript esbuild

# Dê o comando abaixo na sua pasta de usuário ou na sua pasta de projeto
npm install --save-dev @types/node readline-sync

# reinicie o terminal e teste a instalação
tsc --version
npx esbuild --version

# Vamos testar agora a leitura síncrona
echo "console.log('Digite algo:'); const input = require('readline-sync').question(); console.log('Você digitou: ' + input);" > test.ts
npx esbuild test.ts  --outfile=test.js --format=cjs --log-level=error
node test.js
```
