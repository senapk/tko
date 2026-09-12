from tko.util.console import Console
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from tko.feno.quest_line import QuestLine
from tko.i18n import Msg
from tko.util.decoder import Decoder
from tko.util.rt import RT
from tko.feno.task_line import TaskLine, TestsFinder
from tko.feno.indexer_md import IndexerMd
from tko.game.task_enums import EvalMode
from tko.game.eval_mode_spec import get_eval_mode_spec
from loguru import logger
from collections.abc import Sequence



type Line = TaskLine | QuestLine | str

_INDEXER_FOUND_READMES = Msg.parse(
    pt="Encontrados {count} arquivos README.md no diretório base '{base_dir}'",
    en="Found {count} README.md files in base directory '{base_dir}'",
)
_INDEXER_MISSING_LOCAL_FILE = Msg.parse(
    pt="Erro: Arquivo local '[y]{file}[]' não existe para a tarefa:[b]{task}[]",
    en="Error: local file '[y]{file}[]' does not exist for task:[b]{task}[]",
)
_INDEXER_MISSING_README_TASK = Msg.parse(
    pt="Aviso: Arquivo README '[y]{readme}[]' não existe para a tarefa:[b]{task}[]",
    en="Warning: README file '[y]{readme}[]' does not exist for task:[b]{task}[]",
)
_INDEXER_MISMATCH_TITLE = Msg.parse(
    pt="Título desajustado para a tarefa:[b]{readme}[]\n\tREADME:'[y]{line_title}[]' != TASK:'[g]{folder_title}[]'",
    en="Mismatch title for task:[b]{readme}[]\n\tREADME:'[y]{line_title}[]' != TASK:'[g]{folder_title}[]'",
)

_INDEXER_MISSING_HOOKS_ADDING = Msg.parse(
    pt="Encontrados {count} hooks faltando, adicionando-os à '{quest}':",
    en="Found {count} missing hooks, adding to quest '{quest}':",
)
_INDEXER_REMOVE_MISSING_LOCAL_TASKS = Msg.text(
    pt="Remover entradas de tarefas locais inválidas? [s/N] ",
    en="Remove invalid local task entries? [y/N] ",
)
_INDEXER_REMOVED_MISSING_LOCAL_TASKS = Msg.parse(
    pt="Removidas {count} entradas de tarefas locais inválidas.",
    en="Removed {count} invalid local task entries.",
)
_INDEXER_SELF_HAS_TESTS = Msg.parse(
    pt="Aviso: tarefa '[b]{task}[]' marcada como eval=self possui testes; use eval=diff se ela deve ser avaliada por testes.",
    en="Warning: task '[b]{task}[]' marked as eval=self has tests; use eval=diff if it should be evaluated by tests.",
)
_INDEXER_DIFF_MISSING_TESTS = Msg.parse(
    pt="Aviso: tarefa '[b]{task}[]' marcada como eval=diff não possui testes materializados.",
    en="Warning: task '[b]{task}[]' marked as eval=diff has no materialized tests.",
)
_INDEXER_KEY_PATH_MISMATCH = Msg.parse(
    pt="Aviso: chave da tarefa '{key}' diverge do caminho local '{path}' no índice {index}:{line}.",
    en="Warning: task key '{key}' differs from local path '{path}' in index {index}:{line}.",
)

class Elements:
    def __init__(
        self,
        index_path: Path,
        base_dir: Path | None = None,
        verbose: bool = True,
        base_dirs: Sequence[Path] | None = None,
    ):
        self.index_path = index_path
        self.base_dirs = [path.resolve() for path in (base_dirs or ([base_dir] if base_dir is not None else []))]
        if not self.base_dirs:
            raise ValueError("At least one index source directory is required")
        self.base_dir = self.base_dirs[0]
        self.verbose = verbose
        self.lines: list[QuestLine | TaskLine | str] = []

    def load_lines(self) -> None:
        content = Decoder.load(self.index_path)
        index_lines: list[TaskLine | QuestLine | str] = []
        for line in content.splitlines():
            tl = TaskLine(index_path=self.index_path, base_dir=self.base_dir)
            try:
                if tl.init_by_line(line):
                    index_lines.append(tl)
                    continue
            except ValueError as e:
                Console.print(RT(f" {self.index_path}:{len(index_lines) + 1} - ", "r") + RT.parse(str(e)))
                index_lines.append(line)
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

    def missing_local_targets(self) -> list[tuple[int, TaskLine]]:
        missing: list[tuple[int, TaskLine]] = []
        for i, line in enumerate(self.lines):
            if not isinstance(line, TaskLine):
                continue
            if line.target_file is None or line.tm.is_url or line.target_file.exists():
                continue
            missing.append((i, line))
        return missing

    def print_missing_local_targets(self, missing: list[tuple[int, TaskLine]]) -> None:
        for i, line in missing:
            message = str(_INDEXER_MISSING_LOCAL_FILE).format(file=line.target_file, task=line.key)
            Console.print(RT(f" {self.index_path}:{i + 1} - ", "r") + RT.parse(message))

    def remove_missing_local_targets(self, missing: list[tuple[int, TaskLine]]) -> None:
        indexes = {i for i, _ in missing}
        self.lines = [line for i, line in enumerate(self.lines) if i not in indexes]

    def ask_remove_missing_local_targets(self, missing: list[tuple[int, TaskLine]]) -> None:
        if not missing:
            return
        self.print_missing_local_targets(missing)
        answer = input(_INDEXER_REMOVE_MISSING_LOCAL_TASKS.t())
        if answer.strip().lower() not in {"s", "sim", "y", "yes"}:
            return
        self.remove_missing_local_targets(missing)
        Console.print(str(_INDEXER_REMOVED_MISSING_LOCAL_TASKS).format(count=len(missing)))

    def print_test_type_warnings(self) -> None:
        for i, line in enumerate(self.lines):
            if not isinstance(line, TaskLine):
                continue
            eval_mode = line.tm.eval
            if eval_mode is None:
                continue
            eval_spec = get_eval_mode_spec(eval_mode)
            if not eval_spec.supports_self_evaluation:
                continue
            folder = line.materialized_folder
            if folder is None or not folder.is_dir():
                continue
            try:
                has_tests = TestsFinder.find_tests(folder)
            except (FileNotFoundError, OSError, ValueError):
                has_tests = False

            if line.tm.eval == EvalMode.SELF and has_tests:
                message = _INDEXER_SELF_HAS_TESTS
            elif line.tm.eval == EvalMode.DIFF and not has_tests:
                message = _INDEXER_DIFF_MISSING_TESTS
            else:
                continue
            Console.print(RT(f" {self.index_path}:{i + 1} - ", "r") + RT.parse(str(message).format(task=line.key)))

    def warn_key_path_mismatches(self) -> None:
        """Warn when an explicit local task key does not name its linked folder."""
        for line_number, line in enumerate(self.lines, 1):
            if not isinstance(line, TaskLine) or line.origin_key is None:
                continue
            path_key = line.path_key
            if path_key is None or line.origin_key == path_key:
                continue
            logger.warning(
                str(_INDEXER_KEY_PATH_MISMATCH).format(
                    key=line.origin_key,
                    path=path_key,
                    index=self.index_path,
                    line=line_number,
                )
            )

    def normalize_managed_task_keys(self) -> None:
        """Make each managed local task key match its activity-folder path."""
        for line in self.lines:
            if not isinstance(line, TaskLine) or line.target_file is None:
                continue
            target = line.target_file.resolve()
            if not target.exists() or not any(target.is_relative_to(base) for base in self.base_dirs):
                continue
            path_key = line.path_key
            if path_key is None:
                continue
            # The path itself is now the only task identity.  A legacy key is
            # intentionally discarded when the line is rendered.
            line.origin_key = None

    def fix_titles(self, save_titles: bool = False, load_titles: bool = False) -> None:
        for line in self.lines:
            folder_title: str = ""
            if not isinstance(line, TaskLine):
                continue
            if line.tm.is_url:
                continue
            if line.target_file is None:
                continue
            if not line.target_file.exists():
                continue
            folder_title = IndexerMd.load_title_from_markdown_file(line.target_file) or ""
            if folder_title == line.tm.title:
                continue
            if self.verbose and folder_title:
                Console.print(RT.parse(str(_INDEXER_MISMATCH_TITLE).format(readme=line.target_file, line_title=line.tm.title, folder_title=folder_title)))
            if save_titles:
                IndexerMd.replace_title_in_readme(line.target_file, line.tm.title, self.verbose)
            if load_titles and folder_title:
                line.tm.title = folder_title


class Renderer:
    def __init__(self, index_path: Path, align: bool = True):
        self.index_path = index_path
        self.align = align

    def get_render_line(self, item: Line, key_pad: int, fields_pad: int) -> str:
        if isinstance(item, TaskLine):
            return item.render_line(key_pad, fields_pad)
        elif isinstance(item, QuestLine):
            return item.render_line()
        return item

    def _calc_key_pad(self, quests: list[QuestLine], header: list[TaskLine | str]) -> int:
        keys: list[str] = []
        for line in header:
            if isinstance(line, TaskLine):
                keys.append(line.key)
        for quest in quests:
            for line in quest.lines:
                if isinstance(line, TaskLine):
                    keys.append(line.key)
        return max([len(k) for k in keys]) if len(keys) > 0 else 0

    def _calc_fields_pad(self, quests: list[QuestLine], header: list[TaskLine | str]) -> int:
        max_len = len("eval=diff gcs=32")
        all_task_lines: list[TaskLine] = [line for line in header if isinstance(line, TaskLine)]
        for quest in quests:
            all_task_lines.extend([line for line in quest.lines if isinstance(line, TaskLine)])
        for tl in all_task_lines:
            fields = [f for f in tl.tm.get_filled_fields() if not f.startswith("@")]
            max_len = max(max_len, len(" ".join(fields)))
        return max_len

    def _render(self, header: list[TaskLine | str], quests: list[QuestLine]) -> list[str]:
        key_pad = self._calc_key_pad(quests, header) if self.align else 0
        fields_pad = self._calc_fields_pad(quests, header) if self.align else 0
        output: list[str] = []
        for line in header:
            output.append(self.get_render_line(line, key_pad=key_pad, fields_pad=fields_pad))

        for quest in quests:
            output.append(quest.render_line())
            for line in quest.lines:
                output.append(self.get_render_line(line, key_pad=key_pad, fields_pad=fields_pad))
        return output

    def write_file(self, header: list[TaskLine | str], quests: list[QuestLine]) -> None:
        # Combine header and quests into a single list of lines
        output = self._render(header, quests)
        # print("\n".join(output))
        with open(self.index_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output) + "\n")


class Finder:
    def __init__(self, indexer: Elements):
        self.base_dirs = indexer.base_dirs
        self.lines = indexer.lines
        self.index_path = indexer.index_path

    def _get_indexed_targets(self, lines: list[Line]) -> set[Path]:
        targets: set[Path] = set()
        for line in lines:
            if not isinstance(line, TaskLine) or line.target_file is None:
                continue
            targets.add(line.target_file.resolve())
        return targets

    def create_tasks_from_unused_dirs(self) -> dict[Path, TaskLine]:
        output: dict[Path, TaskLine] = {}
        indexed_targets = self._get_indexed_targets(self.lines)
        for base_dir in self.base_dirs:
            if not base_dir.exists():
                continue
            for folder in sorted(path for path in base_dir.iterdir() if path.is_dir()):
                readme = (folder / "README.md").resolve()
                if not readme.exists() or readme in indexed_targets or readme in output:
                    continue
                title = IndexerMd.load_title_from_markdown_file(readme)
                if title is None:
                    continue
                tl = TaskLine(index_path=self.index_path, base_dir=base_dir)
                tl.init_by_readme_file(readme, title)
                output[readme] = tl
        return output


class Merger:
    def __init__(self, indexer: Elements):
        self.lines = indexer.lines
        self.index_path = indexer.index_path
        self.base_dirs = indexer.base_dirs
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

    def _remove_duplicate_local_tasks(self) -> None:
        """Keep the first index entry for each local task README."""
        seen: set[Path] = set()

        def unique(lines: list[TaskLine | str]) -> list[TaskLine | str]:
            output: list[TaskLine | str] = []
            for line in lines:
                if not isinstance(line, TaskLine) or line.target_file is None:
                    output.append(line)
                    continue
                target = line.target_file.resolve()
                if target in seen:
                    continue
                seen.add(target)
                output.append(line)
            return output

        self.header = unique(self.header)
        for quest in self.quests:
            quest.lines = unique(quest.lines)

    def _search_sandbox_quest_index(self, default_quest_name: str) -> int:
        for index, quest in enumerate(self.quests):
            if quest.key == default_quest_name or quest.quest.basic.title == default_quest_name:
                return index
        return -1

    def _source_name(self, readme: Path) -> str:
        for base_dir in self.base_dirs:
            if readme.resolve().is_relative_to(base_dir):
                return base_dir.name
        return readme.parent.parent.name

    def insert_missing_tasks(self, missing_entries: dict[Path, TaskLine]) -> tuple[list[TaskLine | str], list[QuestLine]]:
        self._split_header_and_quests()
        self._remove_duplicate_local_tasks()
        grouped: dict[str, list[TaskLine]] = {}
        for readme, line in missing_entries.items():
            grouped.setdefault(self._source_name(readme), []).append(line)

        for source_name, entries in grouped.items():
            found_index = self._search_sandbox_quest_index(source_name)
            if found_index == -1:
                source_quest = QuestLine()
                source_quest.qp.quest.basic.title = source_name
                source_quest.qp.raw_line = f"## {source_name}"
                self.quests.append(source_quest)
                found_index = len(self.quests) - 1
            if self.verbose:
                Console.print(str(_INDEXER_MISSING_HOOKS_ADDING).format(count=len(entries), quest=source_name))
            self.quests[found_index].lines.extend(entries)
        return self.header, self.quests

def fix_readme(
    index: Path,
    base_dir: Path | None = None,
    verbose: bool = True,
    save_titles: bool = False,
    load_titles: bool = False,
    yes: bool = False,
    align: bool = True,
    warn_key_path_mismatches: bool = False,
    base_dirs: Sequence[Path] | None = None,
) -> None:
    index = index.resolve()
    source_dirs = list(base_dirs or ([base_dir] if base_dir is not None else []))
    if not source_dirs:
        raise ValueError("At least one index source directory is required")
    elements = Elements(index_path=index, base_dirs=source_dirs, verbose=verbose)
    elements.load_lines()
    missing = elements.missing_local_targets()
    if yes:
        elements.remove_missing_local_targets(missing)
        if verbose and missing:
            Console.print(str(_INDEXER_REMOVED_MISSING_LOCAL_TASKS).format(count=len(missing)))
    elif verbose:
        elements.ask_remove_missing_local_targets(missing)
    elements.normalize_managed_task_keys()
    if warn_key_path_mismatches:
        elements.warn_key_path_mismatches()
    elements.fix_titles(save_titles, load_titles)
    if verbose:
        elements.print_test_type_warnings()

    finder = Finder(elements)
    missing_entries = finder.create_tasks_from_unused_dirs()
    
    merger = Merger(elements)
    header, quests = merger.insert_missing_tasks(missing_entries)
    
    renderer = Renderer(index_path=index, align=align)
    renderer.write_file(header, quests)
