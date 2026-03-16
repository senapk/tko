# Instale o VS Code

## Ubuntu e derivados (Debian, Mint, Pop!_OS, etc)

Instalação rápida e limpa do **VS Code** no **Ubuntu**:

---

### 🧰 1. Atualize os pacotes

```bash
sudo apt update
```

---

### 🧩 2. Instale dependências

```bash
sudo apt install -y wget gpg apt-transport-https
```

---

### 🧾 3. Adicione o repositório oficial da Microsoft

```bash
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null
echo "deb [arch=$(dpkg --print-architecture)] https://packages.microsoft.com/repos/code stable main" | \
sudo tee /etc/apt/sources.list.d/vscode.list
```

---

### 📦 4. Instale o VS Code

```bash
sudo apt update
sudo apt install -y code
```

---

### 🚀 5. Abrir

```bash
code
```

---

## Instalando em derivados do Arch Linux (Manjaro, EndeavourOS, etc)

```bash
sudo pacman -S yay
yay -S visual-studio-code-bin
```
