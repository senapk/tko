#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# load all files inside folder src/tko
# and merge them into one file

import os
import shutil

# get all files inside folder src/tko
files = [
"settings",
"runner",
"format", 
"basic", 
"diff",
"down",
"solver", 
"pattern",
"loader",
"writer",
"wdir",
"actions",
"guide",
"__init__",
"__main__",
]


imports = []
output = []

# read all files
for file in files:
    with open("../src/tko/" + file + ".py", "r") as f:
        lines = f.read().split("\n")
        for line in lines:
            if line.startswith("from .") or line.startswith("from __future__"):
                pass
            elif line.startswith("import") or line.startswith("from "):
                if line not in imports:
                    imports.append(line)
            else:
                output.append(line)

with open("tko", "w") as f:
    f.write("#!/usr/bin/env python3\n")
    f.write("# -*- coding: utf-8 -*-\n")
    f.write("from __future__ import annotations\n\n")
    f.write("\n".join(imports))
    f.write("\n")
    f.write("\n".join(output))
    f.write("\n")

