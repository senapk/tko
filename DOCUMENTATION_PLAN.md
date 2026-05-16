# Plano de Documentação para Nível Professional Open Source

## 📊 Análise Atual

### ✅ Pontos Fortes
1. **Wiki estruturada** - Cobre bem os públicos: alunos, professores, devs
2. **README organizado** - Links claros para tópicos específicos
3. **Cobertura de instalação** - Instruções para múltiplos SOs
4. **Orientado a múltiplos públicos** - Alunos, professores, desenvolvedores
5. **Exemplos práticos** - Comandos com output esperado

### ❌ Lacunas Críticas

| Categoria | Problema | Impacto |
|-----------|----------|---------|
| **Visão Geral** | Falta introdução arquitetural e visão filosófica | Novos usuários não entendem o propósito |
| **Contribuição** | Sem `CONTRIBUTING.md` | Difícil para contribuidores iniciar |
| **Arquitetura** | Sem documentação técnica para devs | Refatoração e porting difíceis |
| **FAQ/Troubleshooting** | Não existe | Usuários ficam presos em problemas comuns |
| **API/CLI Reference** | Incompleto, sem especificação formal | Difícil entender todas as opções |
| **Especificações** | Sem definição de formatos (TIO, TOML, etc) | Implementadores não têm referência |
| **Roadmap** | Não existe | Comunidade não sabe direção futura |
| **Badges/Status** | Não existem no README | Desconfiança sobre qualidade |
| **Changelog** | Muito informal | Difícil rastrear mudanças |
| **Exemplos End-to-End** | Faltam tutoriais práticos | Usuários novos não sabem começar |
| **Internacionalização** | Totalmente em português | Limita audiência global |

---

## 🎯 Plano de Implementação

### **Fase 1: Core Documentation (2-3 semanas)**

#### 1.1 README.md - Reescrita
**Objetivo**: Fazer dele o "landing page" profissional

**Adicionar**:
- [ ] Badges (license, tests, version, downloads, python version)
- [ ] "Why TKO?" - proposta de valor em 3 linhas
- [ ] Visão geral com diagrama ASCII
- [ ] Quick start (copiar/colar para começar em 2 min)
- [ ] Screenshots/GIFs de uso
- [ ] Features checklist
- [ ] Comparação com alternativas (se houver)
- [ ] Link claro para CONTRIBUTING
- [ ] Table of Contents

**Exemplo de estrutura**:
```markdown
# TKO — Deliberate Practice Environment for Competitive Programming

[badges]

## 🎯 What is TKO?

[one paragraph with value proposition]

## ✨ Features

- [ ] Feature 1
- [ ] Feature 2

## 🚀 Quick Start

[3 commands, 2 min to see it working]

## 📚 Documentation

- Installation
- Usage
- Contributing

## License
```

#### 1.2 CONTRIBUTING.md - Novo
**Para**: Desenvolvedores que querem contribuir

**Seções obrigatórias**:
- [ ] Código de Conduta
- [ ] Como relatar bugs (template)
- [ ] Como sugerir features
- [ ] Setup local (dev environment)
- [ ] Estrutura de branches (refactor/*, feat/*, fix/*)
- [ ] Processo de PR (revisão, testes, etc)
- [ ] Padrões de código (style guide)
- [ ] Commit message convention
- [ ] Testing requirements
- [ ] Documentação obrigatória para changes

#### 1.3 ARCHITECTURE.md - Novo
**Para**: Devs que querem entender a codebase

**Conteúdo**:
- [ ] Diagrama: camadas (CLI → Run → Tester → Services)
- [ ] Componentes principais (30-40 linhas cada):
  - CLI (tko.cli.*)
  - Run Engine (tko.run.*)
  - Tester/TUI (tko.tester.*)
  - Game/Tasks (tko.game.*)
  - Repository (tko.repository.*)
- [ ] Data flow: tarefa → execution → resultado
- [ ] Extension points: como adicionar linguagens
- [ ] Design decisions: por que cada componente é assim
- [ ] Dependencies: quais pacotes, por quê

**Exemplo**:
```markdown
## Architecture Overview

### Layers

1. **CLI Layer** (tko.cli)
   - Parses commands
   - Routes to subcommands
   - Handles user I/O

2. **Run Layer** (tko.run)
   - Orchestrates test execution
   - No UI concerns
   - Can be used by other tools

3. **TUI Layer** (tko.tester)
   - Curses-based interface
   - Consumes Run layer
   - User interaction

### Data Flow

```

---

### **Fase 2: Reference Documentation (2-3 semanas)**

#### 2.1 API Reference / CLI Reference
**Arquivo**: `docs/REFERENCE.md`

**Conter**:
- [ ] Todos os comandos com `--help`
- [ ] Todas as opções
- [ ] Exemplos para cada comando
- [ ] Exit codes

**Auto-gerar** a partir de `--help`:
```bash
tko --help > docs/cli-help.txt
tko task --help >> docs/cli-help.txt
```

#### 2.2 File Format Specifications
**Arquivo**: `docs/FORMATS.md`

**Especificar**:
- [ ] `.tio` format (test input/output)
- [ ] `languages.toml` schema
- [ ] `README.md` task structure
- [ ] Manifest files
- [ ] `.cache/` directory structure

**Exemplo**:
```markdown
## TIO Format

The `.tio` file is a binary format that stores:
- Version header
- Test cases (input, expected output, metadata)
- Compression metadata

### Structure

Byte 0-3: Magic header (0x54494F00)
Byte 4-5: Version
...
```

#### 2.3 FAQ & Troubleshooting
**Arquivo**: `docs/FAQ.md`

**Cobrir**:
- [ ] "Why does tko say 'solver not found'?"
- [ ] "How do I add a new language?"
- [ ] "What's the difference between .tio and separate files?"
- [ ] "How do I debug test failures?"
- [ ] "Can I use tko with CI/CD?"
- [ ] Performance issues
- [ ] Platform-specific issues (Windows, Mac, Linux)

#### 2.4 Examples & Tutorials
**Arquivo**: `docs/EXAMPLES.md`

**Criar step-by-step**:
- [ ] "Create a simple task from scratch"
- [ ] "Set up a programming course"
- [ ] "Integrate with GitHub Classroom"
- [ ] "Add custom language support"
- [ ] "Extend with plugins/tools"

---

### **Fase 3: Developer Guides (1-2 semanas)**

#### 3.1 Task Lifecycle Documentation
**Arquivo**: `docs/TASK_LIFECYCLE.md`

```
Task Creation → Validation → Publishing → Student Download 
→ Student Submission → Testing → Grading → Analytics
```

#### 3.2 Language Support Guide
**Arquivo**: `docs/LANGUAGE_SUPPORT.md`

**Seções**:
- [ ] How to add a language via `languages.toml`
- [ ] Examples: Python, Java, Go, Rust, C
- [ ] Macro preprocessing for complex flows
- [ ] Build vs run separation
- [ ] Debugging language issues

#### 3.3 Testing & QA Guide
**Arquivo**: `docs/TESTING.md`

**Conter**:
- [ ] Running test suite: `pytest`
- [ ] Coverage: `pytest --cov`
- [ ] Common test patterns
- [ ] Writing tests for new features
- [ ] Integration tests

---

### **Fase 4: Project Management (1 semana)**

#### 4.1 ROADMAP.md
**Objetivo**: Comunicar direção futura

**Seções**:
- [ ] Short-term (próximas 2-3 releases)
- [ ] Medium-term (próximos 6 meses)
- [ ] Long-term (visão > 1 ano)
- [ ] Known limitations
- [ ] Breaking changes planned

**Exemplo**:
```markdown
## Roadmap

### Upcoming (v10.x)
- [ ] Multi-language support for macOS
- [ ] Better error messages
- [ ] Plugin system

### Future (v11+)
- [ ] Web UI (experimental)
- [ ] Rewrite in Go/Rust
```

#### 4.2 CHANGELOG - Reformat
**Melhorar** estrutura:
```markdown
# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [9.2.0] - 2025-01-15

### Added
- Feature X
```

---

### **Fase 5: Organization & Maintenance (ongoing)**

#### 5.1 Docs Directory Structure
```
docs/
├── README.md (docs index)
├── CONTRIBUTING.md
├── ARCHITECTURE.md
├── REFERENCE.md (CLI reference)
├── FORMATS.md (file format specs)
├── FAQ.md
├── EXAMPLES.md
├── TASK_LIFECYCLE.md
├── LANGUAGE_SUPPORT.md
├── TESTING.md
└── images/ (screenshots, diagrams)

wiki/
├── Installation/
│   ├── Windows-WSL.md
│   ├── Linux.md
│   └── Others.md
├── Users/
│   ├── Students.md
│   ├── Teachers.md
│   └── FAQ.md
├── Developers/
│   ├── Setup.md
│   └── Troubleshooting.md
└── Tools/
    ├── mdpp.md
    ├── filter.md
    └── build-all.md
```

#### 5.2 Documentation Maintenance
- [ ] Docstring standards (all public functions)
- [ ] Code comment guidelines
- [ ] Keep docs in sync with code
- [ ] Review docs in every PR
- [ ] Run `markdownlint` on all markdown

---

## 📋 Checklist de Implementação

### Imediato (This Week)
- [ ] Create `CONTRIBUTING.md`
- [ ] Create `ARCHITECTURE.md`
- [ ] Create `docs/FAQ.md`
- [ ] Create `ROADMAP.md`
- [ ] Update `README.md` with badges

### Curto Prazo (Week 2-3)
- [ ] Create `docs/REFERENCE.md`
- [ ] Create `docs/FORMATS.md`
- [ ] Create `docs/EXAMPLES.md`
- [ ] Reformat `CHANGELOG.md`

### Médio Prazo (Week 4-5)
- [ ] Create `docs/LANGUAGE_SUPPORT.md`
- [ ] Create `docs/TESTING.md`
- [ ] Create `docs/TASK_LIFECYCLE.md`
- [ ] Reorganize wiki files

### Longo Prazo
- [ ] Add docstrings to all public APIs
- [ ] Add inline code comments for complex logic
- [ ] Create video tutorials (optional)
- [ ] Setup documentation site (optional, using MkDocs/Sphinx)

---

## 🎯 Success Metrics

| Métrica | Target |
|---------|--------|
| **Onboarding time** | < 5 min to first test run |
| **First PR time** | < 30 min from `git clone` to ready PR |
| **Docs completeness** | 100% public APIs documented |
| **Contributing clarity** | 80%+ of contributors follow guidelines |
| **FAQ coverage** | Reduce issues by 30% |

---

## 💡 Nice-to-Have (Future)

- [ ] Interactive tutorial (in-browser simulation)
- [ ] YouTube channel with walkthroughs
- [ ] Documentation website (mkdocs, sphinx)
- [ ] Generated API docs (sphinx/pdoc)
- [ ] Community matrix/discord channel
- [ ] Localization (English, Spanish, French)
- [ ] GraphQL API documentation (if exposed)

---

## 📝 Notes for Language Consideration

**Current**: Entirely Portuguese
**Recommendation**: English as primary, Portuguese as secondary

**Why**: 
- Open source projects thrive with English
- Larger contributor pool
- Better SEO
- More institutional adoption

**Strategy**:
1. Translate `README.md` first (most impactful)
2. Translate `CONTRIBUTING.md` 
3. Translate `ARCHITECTURE.md`
4. Keep wiki in Portuguese with English headers for reference

Alternative: Keep Portuguese but add English subtitles/translations for critical sections.

---

## Summary

**This plan elevates tko from an academic tool to a professional open source project.**

Estimated effort: **4-6 weeks** for one person
Output quality: **Ready for major adoption, enterprise use, and community contributions**

Start with Phase 1 (README + CONTRIBUTING + ARCHITECTURE) for immediate impact.
