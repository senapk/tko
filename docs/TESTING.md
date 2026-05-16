# Guia de testes e QA

Este guia define como validar alterações no TKO com segurança.

## Comandos principais

Suite completa:

```bash
uv run pytest -q
```

Com cobertura (quando necessário):

```bash
uv run pytest --cov=src --cov-report=term-missing
```

Executar teste específico:

```bash
uv run pytest tests/caminho/do/teste.py -q
```

## Estratégia de validação por tipo de mudança

### Mudança de documentação

1. Revisar links e comandos.
2. Garantir coerência com README/wiki/docs.
3. Rodar checks de links no CI (workflow docs-check).

### Mudança de lógica de execução

1. Rodar suite completa.
2. Garantir que snapshots e outputs esperados estão consistentes.
3. Validar cenários de erro e timeout.

### Mudança em parsing/configuração

1. Adicionar testes unitários para parsing.
2. Cobrir fallback/defaults.
3. Cobrir casos inválidos.

## Padrões de testes no projeto

Cobertura mínima recomendada por feature:

1. cenário feliz
2. caso de borda
3. regressão do bug corrigido

Quando aplicável, incluir:

- integração de CLI
- integração de carregamento de repositório
- validação de mensagens de erro

## Checklist pré-PR

1. Rode `uv run pytest -q` localmente.
2. Revise mudanças acidentais no diff.
3. Atualize documentação quando houver mudança de comportamento.
4. Se alterou comandos, confirme exemplos no README/docs/wiki.

## Diagnóstico rápido de falhas

### Falha de ambiente

- Verifique Python e `uv`.
- Reinstale dependências com `uv sync`.

### Falha em testes de output

- Compare saída real vs esperada.
- Cheque diferenças de ambiente (encoding, stderr, path).

### Falha apenas em CI

- Verifique logs do workflow.
- Reproduza com comandos equivalentes localmente.
- Confirme consistência de versões de ferramenta.

## Relação com CI

Workflows relevantes:

- `.github/workflows/tests.yml`
- `.github/workflows/docs-check.yml`

Objetivo:

- `tests.yml`: validar comportamento funcional.
- `docs-check.yml`: validar links de documentação.

## Guias relacionados

- CONTRIBUTING.md
- docs/REFERENCE.md
- docs/FAQ.md
