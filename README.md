# tko - Test Engine for Judge Operations


## Configure the environment variables in the .env file

```bash
python -m venv venv
source ./venv/bin/activate (Linux, macOS) or ./venv/Scripts/activate (Win)
pip install -e .
```

## Install from git

```bash
pipx install git+https://github.com/senapk/tko.git 
```

## Requirements

Python 3.8 or later with all [requirements.txt](https://github.com/ultralytics/pip/blob/master/requirements.txt)
dependencies installed, including `build` and `twine`. To install run:

```bash
python -m pip install -U pip
pip install -r requirements.txt
```

## Pip Package Steps

### https://pypi.org/

```bash
# Build and upload https://pypi.org/
rm -rf build dist && python -m build && python -m twine upload dist/*
# username: __token__
# password: pypi-AgENdGVzdC5weXBpLm9yZ...

# Download and install
pip install -U ultralytics

# Import and test
python -c "from ultralytics import simple; print(simple.add_one(10))"
sample_script
```

### https://test.pypi.org/

```bash
# Build and upload https://test.pypi.org/
rm -rf build dist && python -m build && python -m twine upload --repository testpypi dist/*
# username: __token__
# password: pypi-AgENdGVzdC5weXBpLm9yZ...

# Download and install
pip install -U --index-url https://test.pypi.org/simple/ --no-deps ultralytics2==0.0.9

# Import and test
python -c "from ultralytics import simple; print(simple.add_one(10))"
sample_script
```
