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

## Trabalhando com outras linguagens

O modelo legado com `solver.yaml` foi removido. Para linguagens/fluxos fora do padrao, use uma destas abordagens:

### 1) Definir no `languages.toml`

Use quando sua linguagem segue o fluxo normal de compilacao/execucao.

Exemplo de entrada:

```toml
[rs]
build_cmd = '''
rustc {files} -o {output}
'''
run_cmd = '''
{output}
'''
draft = '''
fn main() {
    println!("Hello, World!");
}
'''
```

Placeholders disponiveis:

- `{files}`: lista de arquivos fonte
- `{output}`: executavel de saida
- `{cache}`: pasta de build
- `{main}`: nome do arquivo principal sem extensao
- `{entry}`: entrada JS principal (uso comum em TypeScript)

### 2) Metodo Markdown (com `README.md` da tarefa)

Use quando voce quer documentar e executar um fluxo customizado no proprio material da tarefa.

Fluxo recomendado:

1. Descreva o processo no markdown da tarefa (`README.md`) com blocos `bash` em `Shell`.
2. Gere/atualize os casos com o fluxo de markdown da disciplina (mdpp/tio/toml, conforme seu repositorio).
3. Execute usando arquivos de codigo suportados pelo `languages.toml` ou um `solver.mk` quando precisar de orquestracao customizada.

Resumo pratico:

- Para adicionar uma linguagem nova de forma global: `languages.toml`.
- Para conduzir um fluxo especifico de uma tarefa: markdown + artefatos da propria tarefa.
