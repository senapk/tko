---
name: tko-commit
description: Aumentar a versão do TKO e criar um commit descritivo das alterações concluídas neste repositório. Use quando o usuário pedir para fazer um commit do TKO.
---

# Commit do TKO

Execute este fluxo a partir da raiz do repositório, somente quando houver um pedido de commit.

1. Examine `git status`, os diffs staged e unstaged e os arquivos novos. Identifique as alterações que pertencem ao pedido; preserve alterações alheias. Se o escopo do commit estiver incerto, peça esclarecimento antes de incluir esses arquivos.
2. Se não houver alterações para registrar, informe isso e não aumente a versão. Caso contrário, aumente `__version__` em `src/tko/__init__.py`. Por padrão, incremente o número de patch em uma unidade; respeite uma versão ou tipo de incremento especificado pelo usuário. Se a versão já tiver sido aumentada nas alterações atuais, aproveite esse incremento sem duplicá-lo.
3. Execute `./update_version.py` na raiz do repositório. Confirme que a versão em `pyproject.toml` ficou igual a `__version__`.
4. Inclua no stage apenas os arquivos do commit e os dois arquivos de versão. Revise o diff staged e execute `git diff --cached --check`. Se houver falha ou alteração inesperada, corrija antes de continuar.
5. Faça o commit com uma mensagem curta que descreva o que mudou de fato. Use o texto fornecido pelo usuário, se houver. Não use apenas a atualização de versão como descrição quando o commit também inclui funcionalidades ou correções.
6. Informe a nova versão, o hash e o resumo do commit. Não publique nem envie o commit ao remoto, salvo pedido explícito.
