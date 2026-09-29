#!/usr/bin/env bash
set -eu

INSTALL_URL="https://raw.githubusercontent.com/senapk/tko/main/install.sh"
TKO_HOME="${TKO_HOME:-$HOME/.local/share/tko}"
TKO_BIN_DIR="${TKO_BIN_DIR:-$HOME/.local/bin}"
VENV="$TKO_HOME/venv"
LAUNCHER="$TKO_BIN_DIR/tko"
TKM_LAUNCHER="$TKO_BIN_DIR/tkm"
LEGACY_SOIN="$TKO_BIN_DIR/soin"
LEGACY_TEJO="$TKO_BIN_DIR/tejo"
LEGACY_KOA="$TKO_BIN_DIR/koa"
PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "Python 3 não encontrado. Instale python3 e python3-venv antes de instalar o TKO." >&2
    exit 1
fi

if command -v pipx >/dev/null 2>&1 && pipx list 2>/dev/null | grep -q "package tko "; then
    echo "Foi encontrada uma instalação do TKO via pipx. Ela não será alterada."
fi

is_managed_launcher() {
    case "$1" in
        "$LAUNCHER") grep -Fq "$VENV/bin/tko" "$1" 2>/dev/null || grep -Fq "$VENV/bin/soin" "$1" 2>/dev/null ;;
        "$TKM_LAUNCHER") grep -Fq "$VENV/bin/tkm" "$1" 2>/dev/null || grep -Fq "$VENV/bin/tejo" "$1" 2>/dev/null ;;
        "$LEGACY_SOIN") grep -Fq "$VENV/bin/soin" "$1" 2>/dev/null ;;
        "$LEGACY_TEJO"|"$LEGACY_KOA") grep -Fq "$VENV/bin/tejo" "$1" 2>/dev/null ;;
        *) return 1 ;;
    esac
}

for existing in "$LAUNCHER" "$TKM_LAUNCHER" "$LEGACY_SOIN" "$LEGACY_TEJO" "$LEGACY_KOA"; do
    if [ -e "$existing" ] && ! is_managed_launcher "$existing"; then
        echo "Já existe um launcher em $existing. Ele não será sobrescrito." >&2
        echo "Continue usando a instalação atual ou remova esse launcher antes de usar o instalador do TKO." >&2
        exit 1
    fi
done

mkdir -p "$TKO_HOME" "$TKO_BIN_DIR"
if ! "$PYTHON" -m venv "$VENV"; then
    echo "Não foi possível criar o ambiente virtual. Instale o pacote python3-venv e tente novamente." >&2
    exit 1
fi

"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install --upgrade tko

temporary="$TKO_HOME/.install.toml.$$"
printf 'method = "managed"\nvenv = "%s"\nlauncher = "%s"\naliases = ["%s"]\ninstaller_url = "%s"\n' \
    "$VENV" "$LAUNCHER" "$TKM_LAUNCHER" "$INSTALL_URL" > "$temporary"
mv "$temporary" "$TKO_HOME/install.toml"

for name in tko tkm; do
    binary="$name"
    temporary="$TKO_BIN_DIR/.$name.$$"
    printf '#!/usr/bin/env sh\nexec "%s/bin/%s" "$@"\n' "$VENV" "$binary" > "$temporary"
    chmod 755 "$temporary"
    mv "$temporary" "$TKO_BIN_DIR/$name"
done

for legacy in "$LEGACY_SOIN" "$LEGACY_TEJO" "$LEGACY_KOA"; do
    if [ -f "$legacy" ] && { grep -Fq "$VENV/bin/soin" "$legacy" || grep -Fq "$VENV/bin/tejo" "$legacy"; }; then
        rm "$legacy"
    fi
done

echo "TKO e TKM instalados em $TKO_HOME"
if case ":$PATH:" in *":$TKO_BIN_DIR:"*) true ;; *) false ;; esac; then
    echo "Execute: tko --version"
else
    echo "Adicione $TKO_BIN_DIR ao PATH e abra um novo terminal:"
    echo "export PATH=\"$TKO_BIN_DIR:\$PATH\""
fi
