# Outros sistemas operacionais

O suporte principal da documentação do TKO assume Ubuntu, WSL ou Codespaces. Outros sistemas podem funcionar, mas a instalação deve seguir as ferramentas equivalentes da própria plataforma.

## Meta do ambiente

O sistema precisa oferecer:

- terminal compatível com fluxo de desenvolvimento;
- Git instalado;
- autenticação com GitHub funcionando;
- Python 3 compatível com a versão exigida pelo TKO;
- TKO instalado pelo script oficial ou via `pipx`;
- VS Code ou outro editor configurado;
- compiladores ou interpretadores usados pela disciplina.

## Verificação mínima

No terminal que será usado para resolver as atividades:

```bash
git --version
python3 --version
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

Em Linux e macOS, o instalador oficial cria um ambiente virtual próprio:

```bash
curl -fsSL https://raw.githubusercontent.com/senapk/tko/main/install.sh | bash
```

Instalações existentes via `pipx` continuam suportadas. Evite manter dois launchers `tko` ativos no mesmo PATH.

## Quando procurar outra fonte

Procure a documentação atual da ferramenta específica quando:

- o pacote não existir com o nome usado no guia;
- a versão do Python for incompatível;
- o PATH não reconhecer `tko`;
- o GitHub recusar autenticação;
- a linguagem da disciplina exigir uma versão específica.

Depois de resolver o problema específico, volte ao checklist de verificação.
