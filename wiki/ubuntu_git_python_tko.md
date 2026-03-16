# Setup Básico: GIT, Python, TKO

## Instale o git

```bash
sudo apt update
sudo apt install build-essential git -y

# Verifique a instalação e faça o setup do git
git config --global user.name "Seu Nome"
git config --global user.email "seuemail@example.com"

# Gere a chave SSH para autenticação com o GitHub
ssh-keygen -t ed25519 -C "seu_email@github.com"

# Quando pedir o caminho, apenas pressione **Enter** (gera em `~/.ssh/id_ed25519`).

```

---

Se seu ambiente der suporte a um agente SSH, adicione a chave gerada ao agente para facilitar a autenticação com o GitHub.

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

---

### Copiar a chave pública para o GitHub

```bash
# Exiba o conteúdo da chave pública
cat ~/.ssh/id_ed25519.pub

# Copie o conteúdo exibido.
```

1. Vá em **GitHub → Settings → SSH and GPG keys → New SSH key**
2. Cole a chave copiada.
3. Dê um nome (ex: *Linux laptop*).


```bash
# Teste a conexão com o GitHub
ssh -T git@github.com
```

Se aparecer algo como:

```txt
Hi username! You've successfully authenticated...
```

está tudo certo.

## Python e PIPX

Pipx é o gerenciador de executáveis Python. Ele permite instalar scripts do repositório PyPI.

```bash
# instale o python e o pipx
sudo apt update
sudo apt install base-devel python3 python3-pip -y
# se não funcionar, pesquise como instalar o python e o pip na sua distribuição específica

# vamos configurar o pipx
python -m pip install --upgrade pip
python -m pip install --user pipx
python -m pipx ensurepath

# Adicione o pipx no PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Reinicie o terminal para aplicar as mudanças
# Teste com o comando
pipx --version


## Instalando o tko

```bash
pipx install tko
# Teste a instalação com o comando
tko --version
# Sempre que quiser atualizar o tko, basta executar o comando
pipx upgrade tko
```
