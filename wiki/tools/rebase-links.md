# Rebase de links markdown

O comando `tkm tool rebase` recalcula links de um markdown para funcionar a partir de um novo arquivo de saída.
Ao rebasear um índice vindo do GitHub, as linhas de tarefa passam ao formato
materializável: o link aponta para o `README.md` local e a URL remota é
registrada em `<!-- source=... -->`. Os demais links continuam absolutos.

## Parâmetros

- `target` pode ser:
  - um markdown local
  - uma URL `https://...` para markdown
  - um alias `@` cadastrado nas configurações (`@fup`, `@ed`, `@poo`), que baixa o `README.md` do repositório associado
- `--output` (`-o`) define o arquivo de saída.

## Exemplos

```bash
# Rebase a partir de arquivo local
tkm tool rebase src/myfile.md -o docs/myfile.md

# Com output explícito
tkm tool rebase README.md -o docs/README.local.md

# Baixa markdown remoto
tkm tool rebase https://github.com/qxcodefup/arcade/blob/main/README.md -o docs/README.fup.md

# Com output explícito
tkm tool rebase https://github.com/qxcodefup/arcade/blob/main/README.md -o docs/README.fup.md

# Usa alias configurado em settings
tkm tool rebase @fup -o docs/README.fup.md

# Com output explícito
tkm tool rebase @fup -o docs/README.fup.md
```

## Saída

Ao final, o comando imprime confirmações como:

- `Arquivo baixado com sucesso`
- `Rebase concluído`
- `Arquivo salvo no path: ...`
