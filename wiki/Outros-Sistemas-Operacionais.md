# Outros sistemas operacionais

O suporte principal da documentação do TKO assume Ubuntu, WSL ou Codespaces. Outros sistemas podem funcionar, mas a instalação deve seguir as ferramentas equivalentes da própria plataforma.

## Meta do ambiente

O sistema precisa oferecer:

- terminal compatível com fluxo de desenvolvimento;
- Git instalado;
- autenticação com GitHub funcionando;
- Python 3 compatível com a versão exigida pelo TKO;
- `pipx` instalado e no PATH;
- TKO instalado via `pipx`;
- VS Code ou outro editor configurado;
- compiladores ou interpretadores usados pela disciplina.

## Verificação mínima

No terminal que será usado para resolver as atividades:

```bash
git --version
python3 --version
pipx --version
tko --version
tko --help
```

Se o sistema usa `python` em vez de `python3`, adapte a verificação conforme a plataforma.

## Orientação por plataforma

Use o gerenciador de pacotes recomendado pelo seu sistema:

- macOS: Homebrew, instaladores oficiais ou ferramentas da instituição.
- Arch/Manjaro/EndeavourOS: `pacman`, AUR ou helpers aprovados.
- Fedora: `dnf`.
- Debian/Ubuntu derivados: `apt`.

Evite misturar muitos métodos de instalação para a mesma ferramenta. Por exemplo, prefira uma instalação clara de Python e uma instalação clara de `pipx`.

## Quando procurar outra fonte

Procure a documentação atual da ferramenta específica quando:

- o pacote não existir com o nome usado no guia;
- a versão do Python for incompatível;
- o PATH não reconhecer `pipx` ou `tko`;
- o GitHub recusar autenticação;
- a linguagem da disciplina exigir uma versão específica.

Depois de resolver o problema específico, volte ao checklist de verificação.
