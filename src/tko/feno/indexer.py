from tko.util.console import Console
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from tko.feno.quest_line import QuestLine
from tko.i18n import Msg, t
from tko.util.decoder import Decoder
from tko.util.rt import RT
from tko.feno.task_line import TaskLine
from tko.feno.indexer_md import IndexerMd



type Line = TaskLine | QuestLine | str

_INDEXER_FOUND_READMES = Msg(
    pt="Encontrados {count} arquivos README.md no diretório base '{base_dir}'",
    en="Found {count} README.md files in base directory '{base_dir}'",
)
_INDEXER_MISSING_README_REMOVING = Msg(
    pt="Warning: README file '[y]{readme}[]' does not exist for task:[b]{task}[], removing from index",
    en="Warning: README file '[y]{readme}[]' does not exist for task:[b]{task}[], removing from index",
)
_INDEXER_MISSING_README_TASK = Msg(
    pt="Warning: README file '[y]{readme}[]' does not exist for task:[b]{task}[]",
    en="Warning: README file '[y]{readme}[]' does not exist for task:[b]{task}[]",
)
_INDEXER_MISMATCH_TITLE = Msg(
    pt="Mismatch title for task:[b]{readme}[]\n\tREADME:'[y]{line_title}[]' != TASK:'[g]{folder_title}[]'",
    en="Mismatch title for task:[b]{readme}[]\n\tREADME:'[y]{line_title}[]' != TASK:'[g]{folder_title}[]'",
)

_INDEXER_MISSING_HOOKS_ADDING = Msg(
    pt="Found {count} missing hooks, adding to quest '{quest}':",
    en="Found {count} missing hooks, adding to quest '{quest}':",
)

class Elements:
    def __init__(self, index_path: Path, base_dir: Path, verbose: bool = True):
        self.index_path = index_path
        self.base_dir = base_dir
        self.verbose = verbose
        self.lines: list[QuestLine | TaskLine | str] = []

    def load_lines(self) -> None:
        content = Decoder.load(self.index_path)
        index_lines: list[TaskLine | QuestLine | str] = []
        for line in content.splitlines():
            tl = TaskLine(index_path=self.index_path, base_dir=self.base_dir)
            if tl.init_by_line(line):
                index_lines.append(tl)
                continue
            ql = QuestLine()
            if ql.parse(index_path=self.index_path, line=line):
                index_lines.append(ql)
                continue
            index_lines.append(line)
        self.lines = index_lines

    def print_lines(self) -> None:
        for line in self.lines:
            if isinstance(line, TaskLine):
                Console.print(f"TL: {line.key} -> {line.target_file}")
            elif isinstance(line, QuestLine):
                Console.print(f"QL: {line.key} -> {line.quest.basic.title}")
            else:
                Console.print(f"STR: {line}")

    def remove_tasks_with_broken_targets(self) -> None:
        new_list: list[QuestLine | TaskLine | str] = []
        for line in self.lines:
            if not isinstance(line, TaskLine):
                new_list.append(line)
                continue
            if line.target_file is not None:
                if not line.target_file.exists():
                    if self.verbose:
                        Console.print(RT.parse(t(_INDEXER_MISSING_README_REMOVING, readme=line.target_file, task=line.key)))
                    continue
            new_list.append(line)
        self.lines = new_list

    def fix_titles(self, save_titles: bool = False, load_titles: bool = False) -> None:
        for line in self.lines:
            folder_title: str = ""
            if not isinstance(line, TaskLine):
                return
            if line.tm.is_url:
                return
            if line.target_file is None:
                return
            if line.target_file.exists():
                title = IndexerMd.load_title_from_markdown_file(line.target_file)
                if title is not None:
                    folder_title = title
            if folder_title == line.tm.title:
                continue
            if self.verbose:
                Console.print(RT.parse(t(_INDEXER_MISMATCH_TITLE, readme=line.target_file, line_title=line.tm.title, folder_title=folder_title)))
            if save_titles:
                IndexerMd.replace_title_in_readme(line.target_file, line.tm.title, self.verbose)
            if load_titles:
                line.tm.title = folder_title


class Renderer:
    def __init__(self, index_path: Path):
        self.index_path = index_path

    def get_render_line(self, item: Line, key_pad: int) -> str:
        if isinstance(item, TaskLine):
            return item.render_line(key_pad)
        elif isinstance(item, QuestLine):
            return item.render_line()
        return item

    def _calc_key_pad(self, quest_lines: list[QuestLine]) -> int:
        keys: list[str] = []
        for quest in quest_lines:
            for line in quest.lines:
                if isinstance(line, TaskLine):
                    keys.append(line.key)
        return max([len(k) for k in keys]) if len(keys) > 0 else 0

    def _render(self, header: list[TaskLine | str], quests: list[QuestLine]) -> list[str]:
        
        key_pad = self._calc_key_pad(quests)
        output: list[str] = []
        for line in header:
            output.append(self.get_render_line(line, key_pad=key_pad))

        for quest in quests:
            output.append(quest.render_line())
            for line in quest.lines:
                output.append(self.get_render_line(line, key_pad=key_pad))
        return output

    def write_file(self, header: list[TaskLine | str], quests: list[QuestLine]) -> None:
        # Combine header and quests into a single list of lines
        output = self._render(header, quests)
        # print("\n".join(output))
        with open(self.index_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output) + "\n")


class Finder:
    def __init__(self, indexer: Elements):
        self.base_dir = indexer.base_dir
        self.lines = indexer.lines
        self.index_path = indexer.index_path

    def _get_folder_keys(self) -> set[str]:
        keys: set[str] = set()
        for path in self.base_dir.iterdir():
            if path.is_dir():
                readme = (path / 'README.md').resolve()
                if readme.exists():
                    keys.add(path.name)
        return keys

    def _get_line_keys(self, lines: list[Line]) -> set[str]:
        line_keys: set[str] = set()
        for line in lines:
            if isinstance(line, TaskLine):
                line_keys.add(line.key)
        return line_keys

    def create_tasks_from_unused_dirs(self) -> dict[Path, TaskLine]:
        folder_keys = self._get_folder_keys()
        line_keys = self._get_line_keys(self.lines)
        missing_keys = folder_keys - line_keys

        output: dict[Path, TaskLine] = {}
        for m in missing_keys:
            tl = TaskLine(index_path=self.index_path, base_dir=self.base_dir)
            readme = (self.base_dir / m / 'README.md').resolve()
            if not readme.exists():
                continue
            title = IndexerMd.load_title_from_markdown_file(readme)
            if title is None:
                continue
            tl.init_by_readme_file(readme, title)
            output[readme] = tl
        return output


class Merger:
    def __init__(self, indexer: Elements):
        self.lines = indexer.lines
        self.index_path = indexer.index_path
        self.base_dir = indexer.base_dir
        self.verbose = indexer.verbose
        self.header: list[str | TaskLine] = []
        self.quests: list[QuestLine] = []

    def _raw_line(self, line: Line) -> str:
        if isinstance(line, TaskLine):
            return line.raw_line
        elif isinstance(line, QuestLine):
            return line.qp.raw_line
        return line

    def _split_header_and_quests(self) -> None:
        header: list[TaskLine | str] = []
        quests: list[QuestLine] = []

        for line in self.lines:
            if isinstance(line, QuestLine):
                quests.append(line)
                continue
            if quests:
                quests[-1].lines.append(line)
            else:
                header.append(line)
                    
        self.header = header
        self.quests = quests

    def _search_sandbox_quest_index(self, default_quest_name: str) -> int:
        found_index = -1
        for quest in self.quests:
            if quest.qp.raw_line.startswith(f"## {default_quest_name}"):
                found_index = len(self.quests) - 1
        return found_index

    def insert_missing_tasks(self, default_quest_name: str, missing_entries: dict[Path, TaskLine]) -> tuple[list[TaskLine | str], list[QuestLine]]:
        self._split_header_and_quests()
        found_index = self._search_sandbox_quest_index(default_quest_name)

        if found_index == -1:
            sandbox_quest = QuestLine()
            sandbox_quest.qp.quest.basic.title = default_quest_name
            sandbox_quest.qp.raw_line = f"## {default_quest_name}"
            self.quests.append(sandbox_quest)
            found_index = len(self.quests) - 1

        if missing_entries:
            if self.verbose:
                Console.print(t(_INDEXER_MISSING_HOOKS_ADDING, count=len(missing_entries), quest=default_quest_name))
            for _, line in missing_entries.items():
                self.quests[found_index].lines.append(line)
        return self.header, self.quests


def fix_readme(index: Path, base_dir: Path, default_quest_name: str = "Sem Quest", verbose: bool = True, save_titles: bool = False, load_titles: bool = False) -> None:
    index = index.resolve()
    elements = Elements(index_path=index, base_dir=base_dir, verbose=verbose)
    elements.load_lines()
    elements.remove_tasks_with_broken_targets()
    elements.fix_titles(save_titles, load_titles)

    finder = Finder(elements)
    missing_entries = finder.create_tasks_from_unused_dirs()
    
    merger = Merger(elements)
    header, quests = merger.insert_missing_tasks(default_quest_name, missing_entries)
    
    renderer = Renderer(index_path=index)
    renderer.write_file(header, quests)
