#!/bin/bash
./update_version.py
rm -rf dist
uv build
# read token from token.txt
uv publish --token $(cat ~/.pypi_tko.txt)
