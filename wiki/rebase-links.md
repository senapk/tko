# Rebase de links markdown

O comando `tko tool rebase-links` recalcula links de um markdown para funcionar a partir de um novo arquivo de saída.

## Parâmetros

- `target` pode ser:
  - um markdown local
  - uma URL `https://...` para markdown
  - um alias `@` cadastrado nas configurações (`@fup`, `@ed`, `@poo`), que baixa o `README.md` do repositório associado
- `--output` (`-o`) é opcional. Se não for informado:
  - para URLs ou `@alias`: salva na pasta local com o nome `README.md`
  - para arquivo local: salva na pasta local com o mesmo nome do arquivo original

## Exemplos

```bash
# Rebase a partir de arquivo local (salva como myfile.md na pasta local)
tko tool rebase-links src/myfile.md

# Com output explícito
tko tool rebase-links README.md -o docs/README.local.md

# Baixa markdown remoto (salva como README.md na pasta local)
tko tool rebase-links https://github.com/qxcodefup/arcade/blob/master/README.md

# Com output explícito
tko tool rebase-links https://github.com/qxcodefup/arcade/blob/master/README.md -o docs/README.fup.md

# Usa alias configurado em settings (salva como README.md na pasta local)
tko tool rebase-links @fup

# Com output explícito
tko tool rebase-links @fup -o docs/README.fup.md
```

## Saída

Ao final, o comando imprime confirmações como:

- `Arquivo baixado com sucesso`
- `Rebase concluído`
- `Arquivo salvo no path: ...`
