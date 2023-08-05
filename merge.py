#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# load all files inside folder src/tko
# and merge them into one file

import os
import shutil

# get all files inside folder src/tko
files = [
"colored", 
"symbol", 
"enums", 
"unit", 
"param", 
"solver", 
"vpl_parser", 
"loader",
"wdir",
"label_factory",
"runner",
"execution",
"report",
"diff",
"pattern_loader",
"writer",
"replacer",
"actions",
"down",
"__init__",
"__main__",
]


imports = []
output = []

# read all files
for file in files:
    with open("src/tko/" + file + ".py", "r") as f:
        lines = f.read().split("\n")
        for line in lines:
            if line.startswith("from ."):
                pass
            elif line.startswith("import"):
                if line not in imports:
                    imports.append(line)
            else:
                output.append(line)

with open("tko.py", "w") as f:
    f.write("#!/usr/bin/env python3\n")
    f.write("# -*- coding: utf-8 -*-\n")
    f.write("\n".join(imports))
    f.write("\n")
    f.write("\n".join(output))
    f.write("\n")

