#!/bin/bash

REP="${HOME}/${REPL_SLUG}"
mkdir -p ${REP}/.bin
mkdir -p ${REP}/.include

SOURCE="https://raw.githubusercontent.com/senapk/tko/master/replit/tko"
TARGET="${REP}/.bin/tko"
curl  ${SOURCE} -o ${TARGET}
chmod +x ${TARGET}

SOURCE="https://raw.githubusercontent.com/senapk/cppaux/master/fn.hpp"
TARGET="${REP}/.include/fn.hpp"
curl ${SOURCE} -o ${TARGET}

