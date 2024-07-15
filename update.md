# update

## Deploy

```bash
rm -rf build dist && python -m build && python -m twine upload dist/*
```

## Setup

```bash
python -m pip install -U pip
pip install -r requirements.txt

python -m venv venv
source ./venv/bin/activate
pip install -e .
```

## Test

```bash
pip install -e . # se necessario
pip install pytest
pytest # from root repo dir
```

## Before publish

- remove icecream from code
- insert __init__.py inside modules
- uncomment except in __main__.py
