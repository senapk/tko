# Ubuntu / WSL: Git, Python e TKO

Este guia vale para Ubuntu nativo, Ubuntu dentro do WSL e ambientes Linux equivalentes usados em aula.

Ele define as metas do ambiente e oferece comandos comuns para Ubuntu/WSL. Se algum comando falhar por diferença de versão, distribuição, permissão ou política da máquina, procure a documentação atual da ferramenta específica e volte ao checklist de verificação.

## Meta do ambiente

Ao final, o terminal deve ter:

- Git instalado.
- Nome e e-mail configurados no Git.
- Autenticação com GitHub funcionando.
- Python 3 instalado.
- TKO instalado em ambiente virtual próprio.
- `tko --version` e `tko --help` funcionando.

## Ferramentas básicas

```bash
sudo apt update
sudo apt install -y build-essential git curl ca-certificates python3 python3-venv
```


## Configurar Git

Configure seu nome e e-mail:

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seuemail@example.com"
```

Verifique:

```bash
git config --global user.name
git config --global user.email
```

## Configurar acesso ao GitHub

Para repositórios públicos, HTTPS pode ser suficiente. Para repositórios privados de turma, normalmente é melhor configurar SSH.

Gere uma chave SSH:

```bash
ssh-keygen -t ed25519 -C "seuemail@example.com"
```

Quando pedir o caminho do arquivo, pressione Enter para aceitar o padrão.

Mostre a chave pública:

```bash
cat ~/.ssh/id_ed25519.pub
```

Copie o conteúdo exibido e cadastre no GitHub:

1. Acesse GitHub -> Settings -> SSH and GPG keys.
2. Clique em New SSH key.
3. Cole a chave pública.
4. Salve.

Teste a conexão:

```bash
ssh -T git@github.com
```

Se a autenticação falhar, consulte a documentação atual do GitHub sobre SSH keys. O objetivo é conseguir clonar e enviar alterações para os repositórios da disciplina.

## Instalar TKO

Instale pelo script oficial:

```bash
curl -fsSL https://raw.githubusercontent.com/senapk/tko/main/install.sh | bash
```

Verifique:

```bash
tko --version
tko --help
```

Se o comando `tko` não for encontrado, adicione `~/.local/bin` ao PATH e abra outro terminal:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Instalações via `pipx` continuam suportadas como alternativa: `pipx install tko`.

## Atualizar TKO

```bash
tko config self-update
```

Para uma instalação via `pipx`, use `pipx upgrade tko`.

## Checklist de verificação

Antes de começar as atividades, confira:

```bash
git --version
python3 --version
tko --version
tko --help
```

Se a disciplina usar Java, C, C++, Go ou TypeScript, continue em [Linguagens de programação](Linguagens.md).
