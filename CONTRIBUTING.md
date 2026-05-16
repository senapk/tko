# Contribuindo com o TKO

Obrigado por contribuir com o TKO.

Este guia descreve o fluxo recomendado para abrir issues, propor mudanças e enviar pull requests.

## Antes de começar

1. Leia o README e os guias da wiki para entender o fluxo atual.
2. Verifique se já existe issue ou PR relacionado.
3. Prefira mudanças pequenas e focadas.

## Tipos de contribuição

- Correção de bugs
- Melhorias na documentação
- Novas funcionalidades
- Refatorações
- Testes

## Configuração local

Requisitos:

- Python 3.10+
- uv
- Git

Passos:

```bash
uv sync
uv run pytest -q
```

Se os testes falharem, não abra PR antes de resolver ou documentar claramente a causa.

## Fluxo de branch

Padrão sugerido:

- `feat/<nome-curto>` para funcionalidades
- `fix/<nome-curto>` para correções
- `refactor/<nome-curto>` para refatorações
- `docs/<nome-curto>` para documentação

## Padrão de commits

Use mensagens claras e no imperativo, por exemplo:

- `fix: normalize runner stderr decoding`
- `docs: improve README quick start`
- `refactor: decouple run executor from tester`

## Pull Request

Antes de abrir PR:

1. Rode testes locais.
2. Revise os arquivos alterados para remover mudanças acidentais.
3. Atualize documentação se o comportamento para usuário mudou.

Template de PR:

- O repositório possui checklist de documentação em `.github/pull_request_template.md`.
- Preencha os itens com atenção.

## Regras de documentação

Sempre que houver mudança de fluxo de uso:

1. Atualize `README.md` se afetar onboarding, instalação ou quick start.
2. Atualize wiki se afetar guias detalhados.
3. Verifique links quebrados.
4. Padronize nomes de tecnologia (VS Code, TypeScript, GitHub Classroom).

## Testes

Comando principal:

```bash
uv run pytest -q
```

Quando aplicável, adicione testes cobrindo:

- cenário feliz
- bordas
- regressão do bug corrigido

## Reporte de bugs

Para problemas de documentação, use o template de issue:

- `.github/ISSUE_TEMPLATE/documentation_bug.yml`

Para bugs de código, inclua:

- passos para reproduzir
- comportamento esperado
- comportamento observado
- ambiente (SO, Python, shell)

## Código de conduta

Mantenha comunicação respeitosa, objetiva e colaborativa.
