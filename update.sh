#!/bin/bash
./update_version.py
rm -r dist
uv build
# read token from token.txt
uv publish --token $(cat ~/.pypi_rota.txt)
