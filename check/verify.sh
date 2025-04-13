#!/bin/bash
./merge.py
mypy tko --check-untyped-defs
rm tko
