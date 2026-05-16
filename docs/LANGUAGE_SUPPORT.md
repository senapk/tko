# Suporte a linguagens no TKO

Este guia descreve como configurar e manter suporte a linguagens no TKO.

## Visão geral

No fluxo atual, o TKO usa configuração declarativa para build/run e geração de rascunhos.

Estratégias principais:

1. Configuração global via `languages.toml`.
2. Fluxo específico por tarefa via markdown e artefatos locais da atividade.

## Quando usar cada estratégia

Use `languages.toml` quando:

- a linguagem segue fluxo padrão de compilação e execução
- você quer suporte reaproveitável em várias tarefas

Use fluxo por tarefa quando:

- a atividade exige pipeline customizado
- há etapas não triviais de build, preparação ou validação

## Estrutura de entrada em languages.toml

Exemplo mínimo:

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

Placeholders comuns:

- `{files}`: lista de arquivos fonte
- `{output}`: executável de saída
- `{cache}`: pasta de build/cache
- `{main}`: nome do arquivo principal sem extensão
- `{entry}`: entrada JS principal

## Fluxo recomendado para adicionar linguagem

1. Definir entrada da linguagem em `languages.toml`.
2. Validar build e run com exemplo mínimo.
3. Validar geração de rascunho (`draft`).
4. Criar ou ajustar testes cobrindo o novo fluxo.
5. Atualizar documentação relevante (README/wiki/docs).

## Exemplos de stack comuns

### Python

- Normalmente sem etapa de build dedicada.
- Validar execução direta e encoding de saída.

### C/C++

- Definir `build_cmd` com compilador explícito.
- Garantir flags estáveis para ambiente de correção.

### Java

- Compilação e execução separadas.
- Atenção para classe principal e estrutura de arquivos.

### Go

- Preferir `go build` para saída determinística.
- Validar execução do binário gerado.

### TypeScript

- Definir transpile (ex.: esbuild/tsc) e execução via node.
- Garantir resolução de entrypoint.

## Troubleshooting

### Comando de build falha

- Verifique ferramenta instalada (`javac`, `gcc`, `go`, etc.).
- Verifique placeholders e paths no comando.

### Comando de run não encontra artefato

- Confirme se `build_cmd` gerou `{output}`.
- Revise separação entre build e run.

### Draft não é gerado como esperado

- Revise bloco `draft` na configuração.
- Valide extensão/linguagem da tarefa.

## Boas práticas

1. Evitar comandos específicos de shell sem necessidade.
2. Priorizar comandos portáveis em Linux/WSL.
3. Manter exemplos mínimos e reproduzíveis.
4. Documentar limitações por linguagem.

## Guias relacionados

- wiki/Linguagens.md
- docs/REFERENCE.md
- docs/TESTING.md
- CONTRIBUTING.md
