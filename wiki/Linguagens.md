# Linguagens de programação

Instale primeiro o ambiente base do TKO em [Ubuntu / WSL: Git, Python, pipx e TKO](ubuntu_git_python_tko.md). Depois instale apenas as linguagens exigidas pela disciplina.

Este guia define metas e comandos comuns para Ubuntu/WSL. Se algum comando falhar por versão da distribuição, política da máquina ou mudança no instalador da linguagem, consulte a documentação atual da linguagem e volte ao checklist.

## Meta geral

Para cada linguagem usada na disciplina, o aluno deve ter:

- compilador ou interpretador instalado;
- comando disponível no terminal;
- extensão do VS Code instalada, quando a turma usar VS Code;
- um programa simples compilando ou executando;
- o TKO conseguindo executar as tarefas daquela linguagem.

## Java no Linux / WSL

Meta: `java` e `javac` devem funcionar no terminal.

```bash
sudo apt update
sudo apt install default-jre default-jdk -y
code --install-extension redhat.java

java -version
javac -version
``` 

## Go no Linux / WSL

Meta: `go version` deve funcionar no terminal.

Instale Go pelo método recomendado para a turma ou pela documentação oficial da linguagem. Em Ubuntu/WSL, uma instalação por pacote pode ser suficiente quando a versão disponível atende à disciplina:

```bash
sudo apt update
sudo apt install golang-go -y
code --install-extension golang.Go

go version
```

Se a disciplina exigir uma versão mais nova do Go que a disponível no `apt`, use a documentação oficial do Go para instalar a versão adequada.

Para depuração no VS Code, instale o Delve quando necessário:

```bash
go install github.com/go-delve/delve/cmd/dlv@latest
```

Na pasta de projeto, uma configuração de debug pode usar `.vscode/launch.json`:

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

Meta: `node`, `npm`, `tsc` e `esbuild` devem funcionar no terminal.

```bash
sudo apt update
sudo apt install nodejs npm -y
sudo npm install -g typescript esbuild
code --install-extension ms-vscode.vscode-typescript-next

npm install --save-dev @types/node readline-sync

node --version
npm --version
tsc --version
npx esbuild --version
```

Teste uma execução simples quando necessário:

```bash
echo "console.log('Digite algo:'); const input = require('readline-sync').question(); console.log('Você digitou: ' + input);" > test.ts
npx esbuild test.ts  --outfile=test.js --format=cjs --log-level=error
node test.js
```

Se a versão de Node.js do `apt` for antiga para a disciplina, use uma fonte atual indicada pelo professor ou pela documentação do Node.js.

## C e C++ no Linux / WSL

Meta: `gcc`, `g++` e `make` devem funcionar no terminal.

```bash
sudo apt update
sudo apt install build-essential gdb -y

gcc --version
g++ --version
make --version
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
