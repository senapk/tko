#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import re
from pathlib import Path
from tko.i18n import Msg, t
from tko.util.decoder import Decoder
from tko.util.rt import RT
from tko.game.task_matcher import TaskMatcher


logger = logging.getLogger(__name__)

_INDEXER_INVALID_LABEL = Msg(
    pt="Rótulo inválido na linha: {label}",
    en="Invalid label in line: {label}",
)
_INDEXER_FOUND_READMES = Msg(
    pt="Encontrados {count} arquivos README.md no diretório base '{base_dir}'",
    en="Found {count} README.md files in base directory '{base_dir}'",
)
_INDEXER_MISSING_README_REMOVING = Msg(
    pt="Warning: README file '<{readme}:y>' does not exist for task:<{task}:b>, removing from index",
    en="Warning: README file '<{readme}:y>' does not exist for task:<{task}:b>, removing from index",
)
_INDEXER_MISSING_README_TASK = Msg(
    pt="Warning: README file '<{readme}:y>' does not exist for task:<{task}:b>",
    en="Warning: README file '<{readme}:y>' does not exist for task:<{task}:b>",
)
_INDEXER_MISMATCH_TITLE = Msg(
    pt="Mismatch title for task:<{readme}:b>\n\tREADME:'<{line_title}:y>' != TASK:'<{folder_title}:g>'",
    en="Mismatch title for task:<{readme}:b>\n\tREADME:'<{line_title}:y>' != TASK:'<{folder_title}:g>'",
)
_INDEXER_REPLACE_TITLE_README_MISSING = Msg(
    pt="Error: README file '{readme}' does not exist, cannot replace title.",
    en="Error: README file '{readme}' does not exist, cannot replace title.",
)
_INDEXER_REPLACED_TITLE = Msg(
    pt="Replaced title in '{readme}' with '{title}'",
    en="Replaced title in '{readme}' with '{title}'",
)
_INDEXER_MISSING_HOOKS_ADDING = Msg(
    pt="Found {count} missing hooks, adding to quest '{quest}':",
    en="Found {count} missing hooks, adding to quest '{quest}':",
)

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
        self.raw_line: str = ""
        self.isTask: bool = False
        self.raw_pre: str = ""
        self.raw_pos: str = ""
        self.title: str = ""
        self.origin_key: str | None = None

        self.readme_file: Path | None = None
        self.url: str | None = None
        
        self.index_path: Path = index_path.resolve()
        self.base_dir: Path = base_dir.resolve()
    
    def init_by_line(self, line: str):
        self.raw_line = line
        tm = TaskMatcher()
        if not tm.match_full_pattern(line):
            return self
        self.isTask = True
        self.raw_pre = tm.raw_pre
        self.raw_pos = tm.raw_pos
        self.title = tm.task_title
        self.origin_key = tm.key
        
        if not tm.is_view:
            if tm.task_link.startswith(r"http://") or tm.task_link.startswith(r"https://"):
                self.url = tm.task_link
            else:
                # Markdown links may come from Windows paths; normalize separators first.
                normalized_link = tm.task_link.replace("\\", "/")
                link = Path(normalized_link)
                if link.name != "README.md":
                    raise ValueError(f"Invalid README file name: {link}")
                if link.is_absolute():
                    self.readme_file = Path(link).resolve()
                else:
                    self.readme_file = (self.index_path.parent / link).resolve()
        else:
            self.url = tm.task_link
        return self

    def init_by_readme_file(self, readme_file: Path, title: str):
        self.readme_file = readme_file
        self.title = title
        self.origin_key = self.readme_file.parent.name
        self.raw_pre = f"@{self.origin_key}"
        self.isTask = True
        return self

    def get_render_line(self, key_pad: int) -> str:
        if not self.isTask:
            return self.raw_line
        if self.readme_file is not None:
            readme_path = self.readme_file.resolve().relative_to(self.index_path.parent.resolve(), walk_up=True)
            return f"- [ ]{self.get_pre(key_pad)}[{self.title}]({readme_path}){self.raw_pos}"
        elif self.url is not None:
            return f"- [ ]{self.get_pre(key_pad)}[{self.title}]({self.url}){self.raw_pos}"
        return self.raw_line

    def get_pre(self, key_pad: int) -> str:
        pre = self.raw_pre.replace(f"@{self.key}", "").replace("`", "").replace("- [ ]", "").strip()
        words = pre.split(" ")
        words = [w for w in words if not w.startswith("@") and w != ""]
        tags = [f"{w}" for w in words if w.startswith(":")]
        others = [w for w in words if not w.startswith(":")]
        out = f"`@{self.key:<{key_pad + 1}}{' '.join(tags)}`"
        if len(others) > 0:
            out += " " + " ".join(others)
        return out

    @property
    def key(self) -> str:
        edit_task_label = ""
        if self.readme_file is not None:
            if self.readme_file.resolve().is_relative_to(self.base_dir.resolve()):
                edit_task_label = self.readme_file.parent.name
        elif self.origin_key is not None:
            edit_task_label = self.origin_key
        valid_label = ""
        # if "@" not in line:
        valid_chars = TaskMatcher.ALLOWED
        for char in edit_task_label:
            if char in valid_chars:
                valid_label += char
            else:
                logger.error(t(_INDEXER_INVALID_LABEL, label=edit_task_label))
                raise ValueError(t(_INDEXER_INVALID_LABEL, label=edit_task_label))

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
            print(t(_INDEXER_FOUND_READMES, count=len(self.path_title_dict), base_dir=self.base_dir))

    def found_unused_task_dirs(self,) -> None:
        index_tasks: set[str] = set([f.key for f in self.index_lines if f.isTask])
        missing_entries = [t for t in self.path_title_dict.keys() if t.parent.name not in index_tasks]
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
            if file_line.isTask and file_line.readme_file is not None:
                if not file_line.readme_file.exists():
                    if self.verbose:
                        print(RT.parse(t(_INDEXER_MISSING_README_REMOVING, readme=file_line.readme_file, task=file_line.key)))
                    continue
            index_lines.append(file_line)
        self.index_lines = index_lines

    def fix_titles(self, save_titles: bool = False, load_titles: bool = False) -> None:
        # fixing titles
        for line in self.index_lines:
            if not line.isTask or line.readme_file is None:
                continue
            if not line.readme_file in self.path_title_dict: # wiki maybe?
                if self.verbose:
                    print(RT.parse(t(_INDEXER_MISSING_README_TASK, readme=line.readme_file, task=line.readme_file)))
                continue
            folder_title = self.path_title_dict[line.readme_file]
            if folder_title == line.title:
                continue
            if self.verbose:
                print(RT.parse(t(_INDEXER_MISMATCH_TITLE, readme=line.readme_file, line_title=line.title, folder_title=folder_title)))
            if save_titles:
                self.replace_title_in_readme(line.readme_file, line.title)
            if load_titles:
                line.title = folder_title

    def replace_title_in_readme(self, readme_file: Path, new_title: str) -> None:
        if not readme_file.exists():
            logger.error(t(_INDEXER_REPLACE_TITLE_README_MISSING, readme=readme_file))
            return
        with open(readme_file, "r", encoding="utf-8") as f:
            content = f.read()
        # regex to replace first line starting with # with the new title
        regex = r'^(# .*)$'
        new_content = re.sub(regex, f"# {new_title}", content, count=1, flags=re.MULTILINE)
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        if self.verbose:
            print(t(_INDEXER_REPLACED_TITLE, readme=readme_file, title=new_title))

    def insert_missing_tasks(self, default_quest_name: str) -> list[list[IndexLine]]:
        quest_lines: list[list[IndexLine]] = []
        found_index = -1

        if self.index_lines:
            quest_lines.append([self.index_lines[0]])
        for line in self.index_lines[1:]:
            if line.raw_line.startswith("## "):
                quest_lines.append([line])
                if line.raw_line.startswith(f"## {default_quest_name}"):
                    found_index = len(quest_lines) - 1
            else:
                if line.raw_line.strip() != "":
                    quest_lines[-1].append(line)

        if found_index == -1:
            quest_lines.append([IndexLine(index_path=self.index_path, base_dir=self.base_dir).init_by_line(f"## {default_quest_name}")])
            found_index = len(quest_lines) - 1
        if self.missing_entries:
            if self.verbose:
                print(t(_INDEXER_MISSING_HOOKS_ADDING, count=len(self.missing_entries), quest=default_quest_name))
            for _, line in self.missing_entries.items():
                quest_lines[found_index].append(line)
        return quest_lines

    def write_file(self, quest_lines: list[list[IndexLine]], align: bool = False) -> None:
        keys: list[str] = []
        for quest in quest_lines:
            for line in quest:
                if line.isTask:
                    keys.append(line.key)
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
