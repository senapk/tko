# Rebase de links markdown

O comando `tko tool rebase` recalcula links de um markdown para funcionar a partir de um novo arquivo de saída.

## Parâmetros

- `target` pode ser:
  - um markdown local
  - uma URL `https://...` para markdown
  - um alias `@` cadastrado nas configurações (`@fup`, `@ed`, `@poo`), que baixa o `README.md` do repositório associado
- `--output` (`-o`) define o arquivo de saída.

## Exemplos

```bash
# Rebase a partir de arquivo local
tko tool rebase src/myfile.md -o docs/myfile.md

# Com output explícito
tko tool rebase README.md -o docs/README.local.md

# Baixa markdown remoto
tko tool rebase https://github.com/qxcodefup/arcade/blob/main/README.md -o docs/README.fup.md

# Com output explícito
tko tool rebase https://github.com/qxcodefup/arcade/blob/main/README.md -o docs/README.fup.md

# Usa alias configurado em settings
tko tool rebase @fup -o docs/README.fup.md

# Com output explícito
tko tool rebase @fup -o docs/README.fup.md
```

## Saída

Ao final, o comando imprime confirmações como:

- `Arquivo baixado com sucesso`
- `Rebase concluído`
- `Arquivo salvo no path: ...`
