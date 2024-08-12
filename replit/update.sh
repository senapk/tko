#!/bin/bash

REP="${HOME}/${REPL_SLUG}"
mkdir -p ${REP}/.bin
mkdir -p ${REP}/.config


if [[ "$1" == "--check" ]]; then
    today=$(date +%Y-%m-%d)
    file="$REP/.bin/last_update.txt"
    if [ ! -f "$file" ]; then
        echo "$today" > "$file"
    fi
    last_update=$(cat "$file")
    if [ "$last_update" != "$today" ]; then
        echo "$today" > "$file"
        echo "Checking for updates"
    else
        exit 0
    fi
fi
NIX_FILE="${REP}/replit.nix"
# Verifica se o arquivo replit.nix existe
if [ ! -f "$NIX_FILE" ]; then
    echo "{ pkgs }: {" > $NIX_FILE
    echo "  deps = [" >> $NIX_FILE
    echo "    pkgs.graphviz" >> $NIX_FILE
    echo "    pkgs.python3" >> $NIX_FILE
    echo "  ];" >> $NIX_FILE
    echo "}" >> $NIX_FILE
    echo "Arquivo $NIX_FILE criado com pacotes."
else
    if ! grep -q "pkgs.graphviz" "$NIX_FILE"; then
        sed -i '/deps = \[/a\    pkgs.graphviz' $NIX_FILE
    fi    
    if ! grep -q "pkgs.python3" "$NIX_FILE"; then
        sed -i '/deps = \[/a\    pkgs.python3' $NIX_FILE
    fi
fi

GITHUB="https://raw.githubusercontent.com/senapk/tko/master/replit"

SOURCE="${GITHUB}/bashrc"
TARGET="${REP}/.config/bashrc"
curl -sS ${SOURCE} -o ${TARGET}

SOURCE="${GITHUB}/tko"
TARGET="${REP}/.bin/tko"
curl -sS ${SOURCE} -o ${TARGET}
chmod +x ${TARGET}

SOURCE="${GITHUB}/update.sh"
TARGET="${REP}/.bin/update.sh"
curl  ${SOURCE} -o ${TARGET}
chmod +x ${TARGET}

echo ""
echo "Complete a instalação apertando Control D para reiniciar o sistema"
echo ""
