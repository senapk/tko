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
