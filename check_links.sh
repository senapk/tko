#!/usr/bin/env bash
set -euo pipefail
lychee --verbose --no-progress --root-dir "$PWD" README.md wiki/*.md