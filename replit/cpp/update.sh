#!/bin/bash

REP="${HOME}/${REPL_SLUG}"
mkdir -p ${REP}/.bin
mkdir -p ${REP}/.config

SOURCE="https://raw.githubusercontent.com/senapk/tko/master/replit/bashrc"
TARGET="${REP}/.config/bashrc"
curl  ${SOURCE} -o ${TARGET}

SOURCE="https://raw.githubusercontent.com/senapk/tko/master/replit/tko"
TARGET="${REP}/.bin/tko"
curl  ${SOURCE} -o ${TARGET}
chmod +x ${TARGET}

SOURCE="https://raw.githubusercontent.com/senapk/tko/master/replit/check.py"
TARGET="${REP}/.bin/check.py"
curl  ${SOURCE} -o ${TARGET}

SOURCE="https://raw.githubusercontent.com/senapk/tko/master/replit/cpp/update.sh"
TARGET="${REP}/.bin/update.sh"
curl  ${SOURCE} -o ${TARGET}
chmod +x ${TARGET}

SOURCE="https://raw.githubusercontent.com/senapk/tko/master/replit/cpp/replit"
TARGET="${REP}/.replit"
curl  ${SOURCE} -o ${TARGET}

SOURCE="https://raw.githubusercontent.com/senapk/tko/master/replit/cpp/replit.nix"
TARGET="${REP}/replit.nix"
curl  ${SOURCE} -o ${TARGET}

SOURCE="https://raw.githubusercontent.com/senapk/tko/master/replit/msg.txt"
TARGET="${REP}/.bin/msg.txt"
curl  ${SOURCE} -o ${TARGET}

TARGET="${REP}/.bin/langdef.cfg"
echo "cpp" > ${TARGET}

echo ""
echo "Complete a instalação apertando Control D para reiniciar o sistema"
echo "DEPOIS, você pode iniciar o play apertando o botão verde do Replit"
echo ""
