#!/bin/env python

version = ""
with open("src/tko/__init__.py") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"')
            break
print(version)
with open("pyproject.toml") as f:
    lines = f.readlines()
    output: list[str] = []
    for line in lines:
        if line.startswith("version = "):
            output.append(f'version = "{version}"\n')
        else:
            output.append(line)
with open("pyproject.toml", "w") as f:
    f.writelines(output)