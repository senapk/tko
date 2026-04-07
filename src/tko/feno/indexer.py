#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from pathlib import Path
import argparse
from tko.util.decoder import Decoder
from tko.util.rtext import RText

def load_title_from_markdown_file(path: Path) -> str | None:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
    return "NÃO TEM TÍTULO"

class IndexLine:
    def __init__(self, index_path: Path, base_dir: Path):
        self.__line: str = ""
        self.isTask: bool = False
        self.pre: str = ""
        self.title: str = ""
        self.readme_file: Path = Path()
        self.pos: str = ""
        self.index_path: Path = index_path.resolve()
        self.base_dir: Path = base_dir.resolve()
    
    def init_by_line(self, line: str):
        self.__line = line
        regex = r'^(- \[ \].*?)\[(.*?)\]\(([^()]*)\)(.*)$'
        match = re.search(regex, self.__line)
        if match:
            self.isTask = True
            self.pre = match.group(1)
            self.title = match.group(2)
            file = Path(match.group(3))
            if file.is_absolute():
                self.readme_file = Path(file).resolve()
            else:
                self.readme_file = (self.index_path.parent / file).resolve()
            self.pos = match.group(4)
        return self

    def init_by_readme_file(self, readme_file: Path, title: str):
        self.readme_file = readme_file
        self.title = title
        key = self.readme_file.parent.name
        self.pre = f"@{key}"
        self.isTask = True
        return self

    def get_raw_line(self) -> str:
        return self.__line

    def get_render_line(self, key_pad: int) -> str:
        if not self.isTask:
            return self.__line
        readme_path = self.readme_file.resolve().relative_to(self.index_path.parent.resolve(), walk_up=True)
        return f"- [ ]{self.get_pre(key_pad)}[{self.title}]({readme_path}){self.pos}"

    def get_pre(self, key_pad: int) -> str:
        pre = self.pre.replace(f"@{self.get_label()}", "").replace("`", "").replace("- [ ]", "").strip()
        words = pre.split(" ")
        words = [w for w in words if not w.startswith("@") and w != ""]
        tags = [f"{w}" for w in words if w.startswith(":")]
        others = [w for w in words if not w.startswith(":")]
        return f"`@{self.get_label():<{key_pad + 1}}{" ".join(tags)}`" + (f" {' '.join(others)} " if len(others) > 0 else "")

    def get_label(self) -> str:
        edit_task_label = ""
        if self.readme_file.resolve().is_relative_to(self.base_dir.resolve()):
            edit_task_label = self.readme_file.parent.name

        valid_label = ""
        # if "@" not in line:
        valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-+"
        for char in edit_task_label:
            if char in valid_chars:
                valid_label += char
            else:
                print("fail: error in", edit_task_label)
                raise ValueError(f"Invalid label in line: {edit_task_label}")
        # else:
        #     label = line.split('@')[1]
        #     valid_label = ""
        #     for char in label:
        #         if char in valid_chars:
        #             valid_label += char
        #         else:
        #             break
        #     if len(valid_label) == 0:
        #         print("fail: error in", line)
        #         raise ValueError(f"Invalid label in line: {line}")
        return valid_label
    
class Indexer:
    def __init__(self, index_path: Path, base_dir: Path, verbose: bool = True):
        self.index_path = index_path
        self.base_dir = base_dir
        self.verbose = verbose
        self.index_lines: list[IndexLine] = []
        self.path_title_dict: dict[Path, str] = {}
        self.missing_entries: dict[Path, IndexLine] = {}

    # retorna uma lista com os readme's encontrados no basedir, com o título extraído de cada um
    def load_readme_title_dict_from_basedir(self) -> None:
        titles: dict[Path, str] = {}
        for path in self.base_dir.iterdir():
            if path.is_dir():
                readme = (path / 'README.md').resolve()
                if (readme).exists():
                    title = load_title_from_markdown_file(readme)
                    if title is not None:
                        titles[readme] = title
        self.path_title_dict = titles
        if self.verbose:
            print(f"Found {len(self.path_title_dict)} README.md files in base directory '{self.base_dir}'")

    def found_unused_task_dirs(self,) -> None:
        index_tasks = set([f.readme_file for f in self.index_lines if f.isTask])
        missing_entries = [t for t in self.path_title_dict.keys() if t not in index_tasks]
        output: dict[Path, IndexLine] = {}
        if len(missing_entries) > 0:
            for m in missing_entries:
                task_line = (IndexLine(index_path=self.index_path, base_dir=self.base_dir)
                                .init_by_readme_file(m, self.path_title_dict[m]))
                output[m] = task_line
        self.missing_entries = output

    def load_index_lines_removing_broken(self) -> None:
        content = Decoder.load(self.index_path)
        index_lines: list[IndexLine] = []
        for line in content.splitlines():
            file_line = IndexLine(index_path=self.index_path, base_dir=self.base_dir).init_by_line(line)
            if file_line.isTask:
                if not file_line.readme_file.exists():
                    if self.verbose:
                        print(RText.parse(f"Warning: README file '[y]{file_line.readme_file}[.]' does not exist for task:[b]{file_line.get_label()}[.], removing from index"))
                    continue
            index_lines.append(file_line)
        self.index_lines = index_lines

    def fix_titles(self, save_titles: bool = False, load_titles: bool = False) -> None:
        # fixing titles
        for line in self.index_lines:
            if not line.isTask:
                continue
            if not line.readme_file in self.path_title_dict: # wiki maybe?
                if self.verbose:
                    print(RText.parse(f"Warning: README file '[y]{line.readme_file}[.]' does not exist for task:[b]{line.readme_file}[.]"))
                continue
            folder_title = self.path_title_dict[line.readme_file]
            if folder_title == line.title:
                continue
            if self.verbose:
                print(RText.parse(f"Mismatch title for task:[b]{line.readme_file}[.]\n\tREADME:'[y]{line.title}[.]' != TASK:'[g]{folder_title}[.]'"))
            if save_titles:
                self.replace_title_in_readme(line.readme_file, line.title)
            if load_titles:
                line.title = folder_title

    def replace_title_in_readme(self, readme_file: Path, new_title: str) -> None:
        if not readme_file.exists():
            print(f"Error: README file '{readme_file}' does not exist, cannot replace title.")
            return
        with open(readme_file, "r", encoding="utf-8") as f:
            content = f.read()
        # regex to replace first line starting with # with the new title
        regex = r'^(# .*)$'
        new_content = re.sub(regex, f"# {new_title}", content, count=1, flags=re.MULTILINE)
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        if self.verbose:
            print(f"Replaced title in '{readme_file}' with '{new_title}'")

    def insert_missing_tasks(self, default_quest_name: str) -> list[list[IndexLine]]:
        quest_lines: list[list[IndexLine]] = []
        found_index = -1

        if self.index_lines:
            quest_lines.append([self.index_lines[0]])
        for line in self.index_lines[1:]:
            if line.get_raw_line().startswith("## "):
                quest_lines.append([line])
                if line.get_raw_line().startswith(f"## {default_quest_name}"):
                    found_index = len(quest_lines) - 1
            else:
                if line.get_raw_line().strip() != "":
                    quest_lines[-1].append(line)

        if found_index == -1:
            quest_lines.append([IndexLine(index_path=self.index_path, base_dir=self.base_dir).init_by_line(f"## {default_quest_name}")])
            found_index = len(quest_lines) - 1
        if self.missing_entries:
            if self.verbose:
                print(f"Found {len(self.missing_entries)} missing hooks, adding to quest '{default_quest_name}':")
            for _, line in self.missing_entries.items():
                quest_lines[found_index].append(line)
        return quest_lines

    def write_file(self, quest_lines: list[list[IndexLine]], align: bool = False) -> None:
        keys: list[str] = []
        for quest in quest_lines:
            for line in quest:
                if line.isTask:
                    keys.append(line.get_label())
        key_pad = max([len(k) for k in keys]) if len(keys) > 0 else 0

        with open(self.index_path, "w", encoding="utf-8") as f:
            for q in quest_lines:
                f.write(q[0].get_render_line(key_pad=key_pad) + '\n\n')
                for line in q[1:]:
                    f.write(line.get_render_line(key_pad=key_pad) + '\n')
                f.write("\n")

# - create file if not exists
# - remove lines with broken links
# - check if last ## is the default quest, if not, create a new one with missing hooks
#   - else add only the missing hooks to the default quest
def fix_readme(index: Path, base_dir: Path, default_quest_name: str = "Sem Quest", verbose: bool = True, save_titles: bool = False, load_titles: bool = False) -> None:
    index = index.resolve()
    indexer = Indexer(index_path=index, base_dir=base_dir, verbose=verbose)
    indexer.load_readme_title_dict_from_basedir()
    indexer.load_index_lines_removing_broken()
    indexer.fix_titles(save_titles, load_titles)
    indexer.found_unused_task_dirs()
    quest_lines: list[list[IndexLine]] = indexer.insert_missing_tasks(default_quest_name)
    indexer.write_file(quest_lines, align=True)

def index_main(args: argparse.Namespace):
    fix_readme(
        index=Path(args.index), 
        base_dir=Path(args.base), 
        default_quest_name="sandbox", 
        verbose=True, 
        save_titles=args.save, 
        load_titles=args.load
    )
    return 0
