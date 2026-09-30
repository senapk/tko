#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import enum
from collections.abc import Callable
from loguru import logger
from tko.feno.filter import Filter
from tko.i18n import Msg
from tko.util.decoder import Decoder
from pathlib import Path
from dataclasses import dataclass
from tko.loader.unit_data import UnitData



_MDPP_INVALID_TESTS_LIMIT = Msg.text(
    pt="valor inválido ou faltando para --limit",
    en="invalid or missing value for --limit",
)
_MDPP_LOAD_TESTS_OPTION_REMOVED = Msg.text(
    pt="a opção {tag} não é suportada em load; use a diretiva tests",
    en="the {tag} option is not supported in load; use the tests directive",
)
_MDPP_LOAD_EXTRACT_OPTION_REMOVED = Msg.text(
    pt="a opção --extract não é suportada em load",
    en="the --extract option is not supported in load",
)
_MDPP_UNRECOGNIZED_TAG = Msg.text(
    pt="tag não reconhecida '{tag}'",
    en="unrecognized tag '{tag}'",
)
_MDPP_FILE_NOT_FOUND = Msg.text(
    pt="arquivo {path} não encontrado",
    en="file {path} not found",
)
_MDPP_FILE_NOT_MARKDOWN = Msg.text(
    pt="Arquivo {path} não é um arquivo markdown",
    en="File {path} is not a markdown file",
)
_MDPP_UNCLOSED_BLOCK = Msg.text(
    pt="bloco mdpp '{marker}' sem fechamento <!-- end -->",
    en="mdpp block '{marker}' is missing its <!-- end --> closing marker",
)

class Action(enum.Enum):
    RUN = 1
    CLEAN = 2


@dataclass(frozen=True)
class MdppBlock:
    name: str
    opening: str
    command: str
    start: int
    end: int
    newline: str


def _marker_payload(line: str) -> str | None:
    marker: str = line.strip()
    if not marker.startswith("<!--") or not marker.endswith("-->"):
        return None
    return marker[4:-3].strip()


def _opening_marker(payload: str) -> tuple[str, str] | None:
    if payload in {"toc", "toc-table", "toch"}:
        name: str = "toc-table" if payload == "toch" else payload
        return name, ""
    for name in ("links", "load", "tests"):
        prefix: str = f"{name} "
        if payload.startswith(prefix) and payload[len(prefix):].strip():
            return name, payload[len(prefix):].strip()
    return None


def _is_legacy_close(payload: str, name: str, opening: str) -> bool:
    if name in {"toc", "toc-table"}:
        return payload == opening
    return payload == name


def _line_fence(line: str, fence_char: str | None, fence_size: int) -> tuple[str | None, int, bool]:
    text: str = line.rstrip("\r\n")
    if fence_char is not None:
        closing: re.Match[str] | None = re.fullmatch(
            rf" {{0,3}}{re.escape(fence_char)}{{{fence_size},}}[ \t]*", text
        )
        if closing is not None:
            return None, 0, True
        return fence_char, fence_size, True

    tick: str = chr(96)
    opening: re.Match[str] | None = re.match(rf" {{0,3}}({tick}{{3,}}|~{{3,}})", text)
    if opening is None:
        return None, 0, False
    fence: str = opening.group(1)
    if fence[0] == tick and tick in text[opening.end():]:
        return None, 0, False
    return fence[0], len(fence), True


def _find_blocks(content: str) -> tuple[list[MdppBlock], list[tuple[str, str]]]:
    lines: list[str] = content.splitlines(keepends=True)
    offsets: list[int] = []
    offset: int = 0
    for line in lines:
        offsets.append(offset)
        offset += len(line)

    blocks: list[MdppBlock] = []
    unclosed: list[tuple[str, str]] = []
    fence_char: str | None = None
    fence_size: int = 0
    line_index: int = 0
    closing_markers: set[str] = {"end", "toc", "toc-table", "toch", "links", "load", "tests"}

    while line_index < len(lines):
        fence_char, fence_size, in_fence = _line_fence(lines[line_index], fence_char, fence_size)
        if in_fence:
            line_index += 1
            continue

        payload: str | None = _marker_payload(lines[line_index])
        opening: tuple[str, str] | None = _opening_marker(payload) if payload is not None else None
        if opening is None:
            line_index += 1
            continue

        name, command = opening
        opening_text: str = payload if payload is not None else ""
        close_index: int | None = None
        scan_index: int = line_index + 1
        block_fence_char: str | None = fence_char
        block_fence_size: int = fence_size

        while scan_index < len(lines):
            block_fence_char, block_fence_size, in_fence = _line_fence(
                lines[scan_index], block_fence_char, block_fence_size
            )
            if in_fence:
                scan_index += 1
                continue

            inner_payload: str | None = _marker_payload(lines[scan_index])
            if inner_payload is None:
                scan_index += 1
                continue
            if inner_payload == "end" or _is_legacy_close(inner_payload, name, opening_text):
                close_index = scan_index
                fence_char, fence_size = block_fence_char, block_fence_size
                break
            if _opening_marker(inner_payload) is not None:
                unclosed.append((name, opening_text))
                fence_char, fence_size = block_fence_char, block_fence_size
                line_index = scan_index
                break
            if inner_payload in closing_markers:
                unclosed.append((name, opening_text))
                fence_char, fence_size = block_fence_char, block_fence_size
                line_index = scan_index + 1
                break
            scan_index += 1
        else:
            unclosed.append((name, opening_text))
            fence_char, fence_size = block_fence_char, block_fence_size
            line_index = len(lines)

        if close_index is None:
            continue

        start: int = offsets[line_index]
        end: int = offsets[close_index] + len(lines[close_index].rstrip("\r\n"))
        newline: str = "\r\n" if lines[line_index].endswith("\r\n") else "\n"
        blocks.append(MdppBlock(name, opening_text, command, start, end, newline))
        line_index = close_index + 1

    return blocks, unclosed


def _replace_blocks(
    content: str,
    names: set[str],
    action: Action,
    render: Callable[[MdppBlock], str],
) -> str:
    blocks, unclosed = _find_blocks(content)
    for name, marker in unclosed:
        if name in names:
            logger.warning(str(_MDPP_UNCLOSED_BLOCK).format(marker=marker))

    updated: str = content
    for block in reversed(blocks):
        if block.name not in names:
            continue
        body: str = "" if action == Action.CLEAN else render(block)
        body = body.replace("\r\n", "\n").replace("\n", block.newline)
        separator: str = "" if not body or body.endswith(block.newline) else block.newline
        replacement: str = (
            f"<!-- {block.opening} -->{block.newline}{body}{separator}<!-- end -->"
        )
        updated = updated[:block.start] + replacement + updated[block.end:]
    return updated

class TocMaker:
    @staticmethod
    def __only_hashtags(x: str) -> bool:
        return len(x) == x.count("#") and len(x) > 0

    # generate md link for the text
    @staticmethod
    def get_md_link(title: str | None) -> str:
        if title is None:
            return ""
        # remove html comments
        if "<!--" in title and "-->" in title:
            title = title.split("<!--")[0]

        if "[](" in title:
            title = title.split("[](")[0]

        title = title.lstrip(" #")
        title = title.lower()
        out = ''
        for c in title:
            if c == ' ' or c == '-':
                out += '-'
            elif c == '_':
                out += '_'
            elif c == '\\':
                pass
            elif c.isalnum():
                out += c
        return out

    @staticmethod
    def _get_level(line: str) -> int:
        return len(line.split(" ")[0])

    @staticmethod
    def _get_content(line: str) -> str:
        if "<!--" in line and "-->" in line:
            line = line.split("<!--")[0]
        return " ".join(line.split(" ")[1:]).replace("\\", "\\\\")

    @staticmethod
    def remove_code_fences(content: str) -> str:
        regex = r"^```.*?```\n"
        return re.sub(regex, "", content, 0, re.MULTILINE | re.DOTALL)


    @staticmethod
    def extract_entries(content: str) -> list[tuple[int, str]]:
        content = TocMaker.remove_code_fences(content)

        lines = content.splitlines()
        disable_tag = "[]()"
        lines = [line for line in lines if TocMaker.__only_hashtags(line.split(" ")[0]) and line.find(disable_tag) == -1]

        entries: list[tuple[int, str]] = []
        for line in lines:
            level = TocMaker._get_level(line)
            text = "[" + TocMaker._get_content(line) + "](#" + TocMaker.get_md_link(line) + ")"
            entries.append((level, text))
        return entries

    
    @staticmethod
    def execute_toc_table(content: str) -> str:
        entries = TocMaker.extract_entries(content)
        links = [b for (a, b) in entries if a == 2]
        table = ["--" for _ in links]
        return " | ".join(links) + "\n" + " | ".join(table)
        
    execute_toch = execute_toc_table

    @staticmethod
    def execute_toc(content: str) -> str:
        entries = TocMaker.extract_entries(content)
        toc_lines = ["  " * (level - 2) + "- " + link for (level, link) in entries if level > 1]
        toc_text = "\n".join(toc_lines)
        return toc_text

class Toc:
    @staticmethod
    def execute(content: str, action: Action = Action.RUN) -> str:
        return _replace_blocks(
            content,
            {"toc"},
            action,
            lambda _block: TocMaker.execute_toc(content),
        )

class TocTable:
    @staticmethod
    def execute(content: str, action: Action = Action.RUN) -> str:
        return _replace_blocks(
            content,
            {"toc-table", "toch"},
            action,
            lambda _block: TocMaker.execute_toc_table(content),
        )

class Toch:
    @staticmethod
    def execute(content: str, action: Action = Action.RUN) -> str:
        return _replace_blocks(
            content,
            {"toc-table"},
            action,
            lambda _block: TocMaker.execute_toch(content),
        )

class Links:

    @staticmethod
    def load_links(readme_dir: Path, filter_dir: Path):
        readme_dir = readme_dir.resolve()
        def traverse_directory(directory: Path, depth: int = 0) -> str:
            output:str = ""
            if directory.is_dir():
                entries = sorted(directory.iterdir())
                for entry in entries:
                    if entry.name.startswith("."):
                        continue
                    if entry.is_dir():
                        output += "  " * depth + "- " + entry.name + "\n"
                        output += traverse_directory(entry, depth + 1)
                    else:
                        try:
                            rel_path = entry.resolve().relative_to(readme_dir).as_posix()
                        except ValueError:
                            rel_path = Path(os.path.relpath(entry.resolve(), readme_dir)).as_posix()
                        output += "  " * depth + "- [" + entry.name + "](" + rel_path + ")\n"
            return output
        
        origin = readme_dir / filter_dir
        return traverse_directory(origin)

    @staticmethod
    def execute(path: Path, content: str, action: Action = Action.RUN) -> str:
        readme_dir: Path = path.parent.resolve()
        return _replace_blocks(
            content,
            {"links"},
            action,
            lambda block: Links.load_links(readme_dir, Path(block.command)),
        )

@dataclass
class LoadParams:
    filter: bool = False
    rm_comments: bool = False
    fenced: str | None = None

    @property
    def rmcom(self) -> bool:
        return self.rm_comments

    @rmcom.setter
    def rmcom(self, value: bool) -> None:
        self.rm_comments = value

class Load:
    @staticmethod
    def rm_comments(target: Path, content: str) -> str:
        com = "//"
        if target.suffix == ".py":
            com = "#"
        if target.suffix == ".puml":
            com = "'"
        lines = content.splitlines()
        output: list[str] = []
        for line in lines:
            if not line.lstrip().startswith(com):
                output.append(line)
        return "\n".join(output)

    rmcom = rm_comments
    
    @staticmethod
    def __get_value(tokens: list[str], index: int) -> str | None:
        """Tenta pegar o próximo token se ele não for uma nova flag."""
        next_idx = index + 1
        if next_idx < len(tokens) and not tokens[next_idx].startswith("--"):
            return tokens[next_idx]
        return None

    @staticmethod
    def parse_tags(tag_str: str) -> LoadParams:
        params = LoadParams()
        tokens = tag_str.split()
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token == "--fenced":
                value = Load.__get_value(tokens, i)
                if value:
                    params.fenced = value
                    i += 1  # Consome o valor
                else:
                    params.fenced = ""  # Se não houver valor, apenas ativa o fenced sem linguagem específica
            elif token == "--extract":
                logger.error(str(_MDPP_LOAD_EXTRACT_OPTION_REMOVED))
                if Load.__get_value(tokens, i) is not None:
                    i += 1
            elif token == "--filter":
                params.filter = True
            elif token in ("--rm-comments", "--rmcom"):
                params.rm_comments = True
            elif token in ("--tests", "--tests-table", "--tests-tio"):
                logger.error(str(_MDPP_LOAD_TESTS_OPTION_REMOVED).format(tag=token))
            elif token.startswith("--"):
                logger.warning(str(_MDPP_UNRECOGNIZED_TAG).format(tag=token))
            
            i += 1  # Sempre avança para o próximo token

        return params

    @staticmethod
    def generate_tests_table_from_toml(content: str, path: Path, limit: int | None = None) -> str:
        from tko.loader.toml_parser import TomlParser

        test_data_list: list[UnitData] = TomlParser.extract_toml_units(content, path)
        if limit is not None:
            test_data_list = test_data_list[:limit]
        if not test_data_list:
            return ""

        lines: list[str] = [
            '<table><tr><th><code>Entrada</code></th><th><code>Saída</code></th></tr>'
        ]
        for unit in test_data_list:
            lines.append('<!-- INPUT --><tr><td valign="top"><pre>')
            lines.append(unit.input.removesuffix("\n"))
            lines.append('</pre></td>')
            lines.append('<!-- OUTPUT --><td valign="top"><pre>')
            lines.append(unit.output.removesuffix("\n"))
            lines.append('</pre></td></tr>')
        lines.append('</table>')
        return "\n".join(lines)

    @staticmethod
    def _process_file_content(abspath: Path, rel_path: str, params: LoadParams) -> str:
        """Encapsula a lógica de leitura e transformação do conteúdo."""
        if not abspath.is_file():
            logger.warning(str(_MDPP_FILE_NOT_FOUND).format(path=rel_path))
            return ""

        data = Decoder.load(abspath)

        # 1. filter
        if params.filter:
            data = Filter(Path(rel_path)).process(data)
        # 2. remove comments
        if params.rm_comments:
            data = Load.rm_comments(abspath, data)
        # 3. fenced
        if params.fenced is not None:
            if params.fenced == "":
                lang = abspath.suffix[1:] if abspath.suffix.startswith(".") else ""
            else:
                lang = params.fenced
            data = f"```{lang}\n{data.rstrip()}\n```"

        # Garante que termine com apenas uma quebra de linha
        return data.rstrip()

    @staticmethod
    def execute(content: str, target_dir: Path, action: Action = Action.RUN) -> str:
        def render(block: MdppBlock) -> str:
            full_command: str = block.command
            parts = full_command.split(maxsplit=1)
            path_str = parts[0] if len(parts) > 0 else ""
            flags_str = parts[1] if len(parts) > 1 else ""
            params: LoadParams = Load.parse_tags(flags_str)
            abspath: Path = (Path(target_dir) / path_str).resolve()
            return Load._process_file_content(abspath, path_str, params)

        return _replace_blocks(content, {"load"}, action, render)



class Tests:
    """Renderiza casos de teste TOML como tabela."""

    @staticmethod
    def _parse_command(full_command: str) -> tuple[str, int | None]:
        tokens = full_command.split()
        path_str = tokens[0]
        limit: int | None = None
        index = 1
        while index < len(tokens):
            token = tokens[index]
            if token == "--limit":
                if index + 1 >= len(tokens):
                    logger.warning(str(_MDPP_INVALID_TESTS_LIMIT))
                else:
                    try:
                        parsed = int(tokens[index + 1])
                        if parsed < 0:
                            raise ValueError
                        limit = parsed or None
                    except ValueError:
                        logger.warning(str(_MDPP_INVALID_TESTS_LIMIT))
                    index += 1
            elif token.startswith("--"):
                logger.warning(str(_MDPP_UNRECOGNIZED_TAG).format(tag=token))
            index += 1
        return path_str, limit

    @staticmethod
    def execute(content: str, target_dir: Path, action: Action = Action.RUN) -> str:
        def render(block: MdppBlock) -> str:
            path_str, limit = Tests._parse_command(block.command)
            path: Path = (Path(target_dir) / path_str).resolve()
            if not path.is_file():
                logger.warning(str(_MDPP_FILE_NOT_FOUND).format(path=path_str))
                return ""
            return Load.generate_tests_table_from_toml(Decoder.load(path), path, limit)

        return _replace_blocks(content, {"tests"}, action, render)


class MdppMain:
    @staticmethod
    def fix_path(target: Path) -> Path:
        target = target.resolve()
        if target.is_dir():
            target = target / "README.md"
        return target

    @staticmethod
    def open_file(path: Path) -> tuple[bool, str]: 
        if path.is_file():
            file_content = Decoder.load(path)
            return True, file_content
        logger.warning(str(_MDPP_FILE_NOT_FOUND).format(path=path))
        return False, "" 

class Mdpp:
    @staticmethod
    def update_file(target: Path, action: Action = Action.RUN, quiet: bool = False) -> bool:
        path: Path = MdppMain.fix_path(target)
        if not path.suffix == ".md":
            logger.warning(str(_MDPP_FILE_NOT_MARKDOWN).format(path=path))
            return False
        if not path.is_file():
            logger.warning(str(_MDPP_FILE_NOT_FOUND).format(path=path))
            return False
        target_dir = path.parent.resolve()
        found, original = MdppMain.open_file(path)
        if not found:
            return False
        updated = original
        updated = Toc.execute(updated, action)
        updated = TocTable.execute(updated, action)
        updated = Tests.execute(updated, target_dir, action)
        updated = Load.execute(updated, target_dir, action)
        updated = Links.execute(path, updated, action)
        if updated != original:
            Decoder.save(path, updated)
            return True

        return False
