#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from pathlib import Path
import argparse
from tko.util.decoder import Decoder

class FileLine:
    def __init__(self, index_path: Path | None = None):
        self.line: str = ""
        self.isTask: bool = False
        self.pre: str = ""
        self.title: str | None = None
        self.folder: Path | None = None
        self.pos: str = ""
        self.index_path: Path | None = index_path
    
    def init_by_line(self, line: str):
        self.line = line
        regex = r'- \[ \](.*)\[(.+)\]\((.+)\)(.*)'
        match = re.search(regex, self.line)
        if match:
            self.isTask = True
            self.pre = match.group(1)
            self.title = match.group(2)
            file = Path(match.group(3))
            if file.is_absolute():
                self.folder = file.parent
            else:
                if self.index_path is None:
                    raise ValueError("index_path is required for relative paths")
                self.folder = (self.index_path.parent / file).parent
            self.pos = match.group(4)
        return self

    def init_by_folder(self, folder: Path):
        self.isTask = True
        self.folder = folder
        self.pre = f" `@{folder.name}` "
        self.title = FileLine.load_markdown_title_from_file(folder / 'README.md')
        return self

    def get_label(self) -> None | str:
        if self.title is None:
            return None
        line = self.pre + " " + self.title + " " + self.pos
        if "@" not in line:
            return None
        label = line.split('@')[1]
        valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
        valid_label = ""
        for char in label:
            if char in valid_chars:
                valid_label += char
            else:
                break
        if len(valid_label) == 0:
            print("fail: error in", line)
            return None
        return valid_label
    
    def load_title_from_file_and_recreate_line(self) -> str | None:
        if not self.isTask:
            print("fail: not a task line")
            return ""
        if self.folder is None:
            print("folder is None")
            return None
        label = self.get_label()
        pre = self.pre
        pos = self.pos
        if label is not None:
            if label != self.folder.name:
                print(f"Warning: label:{label}, hook:{self.folder.name}")
        readme = (self.folder / 'README.md').resolve()
        title = FileLine.load_markdown_title_from_file(readme)
        if title is None:
            print(f"fail: could not load title from {readme}", self.line)
            return None
        if self.index_path is None:
            print("fail: index_path is required to load title from file")
            return None
        readme = readme.relative_to(self.index_path.parent, walk_up=True)
        return f"- [ ]{pre}[{title}]({readme}){pos}"

    @staticmethod
    def load_markdown_title_from_file(path: Path) -> str | None:
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("---"):
                    continue
                if len(line.split(":")) > 1:
                    continue
                line = line.strip()
                if line.startswith("#"):
                    return line.lstrip("#").strip()
                if line.strip() != "":
                    return line
        return "NÃO TEM TÍTULO"


def found_unused_hooks(task_lines: list[FileLine], base_dir: Path, index: Path) -> list[str]:
    key_all: list[str] = []
    for tline in task_lines:
        if tline.isTask:
            folder = tline.folder
            if folder is not None:
                key_all.append(folder.name)
    # create a set of hooks
    hooks = set(key_all)

    # create a list with folders in base dir if base/folder/README.md exists
    folders: list[Path] = []
    for task in base_dir.iterdir():
        if (task / 'README.md').exists():
            folders.append(task)

    missing = [f for f in folders if f.name not in hooks]
    output: list[str] = []
    if len(missing) > 0:
        for m in missing:
            task_line = FileLine(index_path=index).init_by_folder(m)
            line = task_line.load_title_from_file_and_recreate_line()
            if line is not None:
                output.append(line)
        return output
    return []


def find_unused(index: Path, base: Path) -> list[str]:
    content = Decoder.load(index)
    task_lines = [FileLine(index_path=index).init_by_line(line) for line in content.splitlines()]
    return found_unused_hooks(task_lines, base, index)

# - create file if not exists
# - remove lines with broken links
# - check if last ## is the default quest, if not, create a new one with missing hooks
#   - else add only the missing hooks to the default quest
def fix_readme(index: Path, base: Path, default_quest_name: str = "Sem Quest", verbose: bool = True) -> None:
    index = index.resolve()
    content = Decoder.load(index)
    file_lines: list[FileLine] = []
    for line in content.splitlines():
        file_line = FileLine(index_path=index).init_by_line(line)
        if file_line.isTask:
            if file_line.folder is not None and not file_line.folder.exists():
                # print(f"Warning: folder {file_line.folder} does not exist, removing line: {line}")
                continue
        file_lines.append(file_line)
    
    missing = found_unused_hooks(file_lines, base, index)
    quest_lines: list[list[str]] = []
    found_index = -1
    if file_lines:
        quest_lines.append([file_lines[0].line])
    for line in file_lines[1:]:
        if line.line.startswith("## "):
            quest_lines.append([line.line])
            if line.line.startswith(f"## {default_quest_name}"):
                found_index = len(quest_lines) - 1
        else:
            if line.line.strip() != "":
                quest_lines[-1].append(line.line)

    if found_index == -1:
       quest_lines.append([f"## {default_quest_name}"])
       found_index = len(quest_lines) - 1
    if missing and verbose:
        print(f"Found {len(missing)} missing hooks, adding to quest '{default_quest_name}':")
    for m in missing:
        if verbose:
            print(m)
        quest_lines[found_index].append(m)
    with open(index, "w", encoding="utf-8") as f:
        for q in quest_lines:
            f.write(q[0] + '\n\n')
            if len(q) > 1:
                f.write('\n'.join(q[1:]) + '\n\n')
    

def index_main(args: argparse.Namespace):
    fix_readme(Path(args.index), Path(args.base), "sandbox", verbose=False)
    return 0
