#!/usr/bin/env bash
set -eu

INSTALL_URL="https://raw.githubusercontent.com/senapk/tko/main/install.sh"
TKO_HOME="${TKO_HOME:-$HOME/.local/share/tko}"
TKO_BIN_DIR="${TKO_BIN_DIR:-$HOME/.local/bin}"
VENV="$TKO_HOME/venv"
LAUNCHER="$TKO_BIN_DIR/tko"
PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "Python 3 não encontrado. Instale python3 e python3-venv antes de instalar o TKO." >&2
    exit 1
fi

if command -v pipx >/dev/null 2>&1 && pipx list 2>/dev/null | grep -q "package tko "; then
    echo "Foi encontrada uma instalação do TKO via pipx. Ela não será alterada."
fi

if [ -e "$LAUNCHER" ] && ! grep -Fq "$VENV/bin/tko" "$LAUNCHER" 2>/dev/null; then
    echo "Já existe um launcher em $LAUNCHER. Ele não será sobrescrito." >&2
    echo "Continue usando a instalação atual ou remova esse launcher antes de usar o instalador do TKO." >&2
    exit 1
fi

mkdir -p "$TKO_HOME" "$TKO_BIN_DIR"
if ! "$PYTHON" -m venv "$VENV"; then
    echo "Não foi possível criar o ambiente virtual. Instale o pacote python3-venv e tente novamente." >&2
    exit 1
fi

"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install --upgrade tko

temporary="$TKO_HOME/.install.toml.$$"
printf 'method = "managed"\nvenv = "%s"\nlauncher = "%s"\ninstaller_url = "%s"\n' \
    "$VENV" "$LAUNCHER" "$INSTALL_URL" > "$temporary"
mv "$temporary" "$TKO_HOME/install.toml"

temporary="$TKO_BIN_DIR/.tko.$$"
printf '#!/usr/bin/env sh\nexec "%s" "$@"\n' "$VENV/bin/tko" > "$temporary"
chmod 755 "$temporary"
mv "$temporary" "$LAUNCHER"

echo "TKO instalado em $TKO_HOME"
if case ":$PATH:" in *":$TKO_BIN_DIR:"*) true ;; *) false ;; esac; then
    echo "Execute: tko --version"
else
    echo "Adicione $TKO_BIN_DIR ao PATH e abra um novo terminal:"
    echo "export PATH=\"$TKO_BIN_DIR:\$PATH\""
fi