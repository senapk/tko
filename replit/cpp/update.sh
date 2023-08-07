#!/bin/bash

REP="${HOME}/${REPL_SLUG}"
mkdir -p ${REP}/.bin
mkdir -p ${REP}/.include

SOURCE="https://raw.githubusercontent.com/senapk/tko/master/replit/tko"
TARGET="${REP}/.bin/tko"
curl  ${SOURCE} -o ${TARGET}
chmod +x ${TARGET}

SOURCE="https://raw.githubusercontent.com/senapk/tko/master/replit/bashrc"
TARGET="${REP}/.bashrc"
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

SOURCE="https://raw.githubusercontent.com/senapk/cppaux/master/fn.hpp"
TARGET="${REP}/.include/fn.hpp"
curl ${SOURCE} -o ${TARGET}

