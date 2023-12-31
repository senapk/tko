#!/bin/bash

REP="${HOME}/${REPL_SLUG}"
mkdir -p ${REP}/.bin

SOURCE="https://raw.githubusercontent.com/senapk/tko/master/replit/bashrc"
TARGET="${REP}/.bashrc"
curl  ${SOURCE} -o ${TARGET}

SOURCE="https://raw.githubusercontent.com/senapk/tko/master/replit/py/replit"
TARGET="${REP}/.replit"
curl  ${SOURCE} -o ${TARGET}

SOURCE="https://raw.githubusercontent.com/senapk/tko/master/replit/py/update.sh"
TARGET="${REP}/.bin/update.sh"
curl  ${SOURCE} -o ${TARGET}
chmod +x ${TARGET}

