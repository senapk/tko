#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# load all files inside folder src/tko
# and merge them into one file

import os
import shutil
from os.path import isfile, join, isdir

print("Running merge for replit")

class Entry:
    def __init__(self):
        self.path = ""
        self.key = ""
        self.dependencies = []
        self.content = ""
    def __str__(self):
        return f'{self.key}\n    {" ".join(self.dependencies)}'



class Merge:
    def __init__(self, root):
        self.root = root
        self.imports = []
        self.files = []
        self.entries = []
        self.content = ""

    def load_files(self):
        root = self.root
        files = [join(root, file) for file in os.listdir(root) if file.endswith(".py")]
        dirs = [join(root, dir) for dir in os.listdir(root) if isdir(join(root, dir))]

        for dir in dirs:
            files += [join(dir, file) for file in os.listdir(dir) if file.endswith(".py")]

        self.files = files
        return self


    def parse_entry(self, file) -> Entry:
        entry = Entry()
        entry.path = file
        entry.key = file.split("/")[-1].replace(".py", "")


        with open(file, "r") as f:
            content = f.read()
            lines = content.splitlines()
            output = []
            for line in lines:
                if  line.startswith("from __future__") or ("appdirs" in line) or line.startswith("from typing"):
                    pass
                elif line.startswith("from .") or line.startswith("from tko."):
                    line = line.replace("..", ".")
                    dependence_key = line.split(".")[-1].split(" ")[0]
                    if dependence_key not in entry.dependencies:
                        entry.dependencies.append(dependence_key)
                elif line.startswith("import") or line.startswith("from "):
                    if line not in self.imports:
                        self.imports.append(line)
                elif "__name__" in line and not "MERGE_INSERT" in line:
                    break
                else:
                    output.append(line)
            
            entry.content = "\n".join(output)

        return entry
    
    def parse_entries(self):
        for file in self.files:
            entry = self.parse_entry(file)
            if entry.key != "__init__":
                if entry.key in [e.key for e in self.entries]:
                    print(f"Duplicate entry: {entry.key}")
                    exit(1)
                self.entries.append(entry)

    def is_free(self, entry, tree):
        for dep in entry.dependencies:
            if dep in tree.keys():
                return False
        return True

    def extract_one(self, tree) -> Entry:
        for key in tree:
            entry = tree[key]
            if self.is_free(entry, tree):       
                aux = entry
                del tree[key]
                return aux
        print("ERROR: no free entry")
        exit(1)


    def merge(self):
        content = []
        content.append("#!/usr/bin/env python3")
        content.append("# -*- coding: utf-8 -*-")
        content.append("from __future__ import annotations\n\n")
        content.append("from typing import List, Dict, Tuple, Optional, Any, Callable, Union, Set")
        content.append("\n".join(self.imports))
        init = self.parse_entry(f"{self.root}/__init__.py")
        content.append(init.content)

        tree = {}
        for entry in self.entries:
            tree[entry.key] = entry

        index = 0
        while len(tree) > 0:
            free = self.extract_one(tree)
            print(f'{index} - {free.key}')
            index += 1
            content.append(free.content)

        self.content = "\n".join(content)



# get all files inside folder src/tko
merge = Merge("../src/tko")
merge.load_files().parse_entries()
merge.merge()
with open("tko", "w") as f:
    f.write(merge.content)
