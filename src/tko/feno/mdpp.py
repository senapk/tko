#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import enum
from loguru import logger
from tko.feno.filter import Filter
from tko.i18n import Msg
from tko.util.decoder import Decoder
from pathlib import Path
from dataclasses import dataclass
from tko.loader.unit_data import UnitData



_MDPP_MISSING_EXTRACT_VALUE = Msg.text(
    pt="faltando valor para --extract",
    en="missing value for --extract",
)
_MDPP_INVALID_TESTS_INTEGER = Msg.text(
    pt="valor inválido ou faltando para --tests",
    en="invalid or missing integer for --tests",
)
_MDPP_MUTUALLY_EXCLUSIVE_TESTS = Msg.text(
    pt="--tests-tio e --tests-table são mutuamente exclusivos",
    en="--tests-tio and --tests-table are mutually exclusive",
)
_MDPP_DEPRECATED_TESTS_TABLE = Msg.text(
    pt="a combinação --tests --table está depreciada, use --tests-table",
    en="the combination --tests --table is deprecated, use --tests-table",
)
_MDPP_UNRECOGNIZED_TAG = Msg.text(
    pt="tag não reconhecida '{tag}'",
    en="unrecognized tag '{tag}'",
)
_MDPP_FILE_NOT_FOUND = Msg.text(
    pt="arquivo {path} não encontrado",
    en="file {path} not found",
)
_MDPP_FILE_UPDATED = Msg.text(
    pt="arquivo {path} atualizado",
    en="file {path} updated",
)
_MDPP_FILE_NOT_MARKDOWN = Msg.text(
    pt="Arquivo {path} não é um arquivo markdown",
    en="File {path} is not a markdown file",
)

class Action(enum.Enum):
    RUN = 1
    CLEAN = 2

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
        regex = r"<!-- toc -->\n" + r"(.*?)"+ r"<!-- toc -->"
        if action == Action.RUN:
            new_toc = TocMaker.execute_toc(content)
            subst = r"<!-- toc -->\n" + new_toc + r"\n<!-- toc -->"
        else:
            subst = r"<!-- toc -->\n<!-- toc -->"
        return re.sub(regex, subst, content, 0, re.MULTILINE | re.DOTALL)

class TocTable:
    @staticmethod
    def execute(content: str, action: Action = Action.RUN) -> str:
        regex = r"<!-- toc-table -->\n" + r"(.*?)" + r"<!-- toc-table -->"
        if action == Action.RUN:
            new_toc = TocMaker.execute_toc_table(content)
            subst = r"<!-- toc-table -->\n" + new_toc + r"\n<!-- toc-table -->"
        else:
            subst = r"<!-- toc-table -->\n<!-- toc-table -->"
        content = re.sub(regex, subst, content, 0, re.MULTILINE | re.DOTALL)
        return Toch.execute(content, action)

class Toch:
    @staticmethod
    def execute(content: str, action: Action = Action.RUN) -> str:
        regex = r"<!-- toch -->\n" + r"(.*?)" + r"<!-- toch -->"
        if action == Action.RUN:
            new_toc = TocMaker.execute_toch(content)
            subst = r"<!-- toch -->\n" + new_toc + r"\n<!-- toch -->"
        else:
            subst = r"<!-- toch -->\n<!-- toch -->"
        return re.sub(regex, subst, content, 0, re.MULTILINE | re.DOTALL)

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
        regex = r"<!-- links (\S*?) -->\r?\n(.*?)<!-- links -->"
        matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)

        for match in matches:
            filter_dir = match.group(1)

            lregex = (
                r"<!-- links "
                + re.escape(filter_dir)
                + r" -->\r?\n(.*?)<!-- links -->"
            )

            if action == Action.RUN:
                readme_dir = path.parent.resolve()
                new_links = Links.load_links(readme_dir, Path(filter_dir))

                subst = (
                    f"<!-- links {filter_dir} -->\n"
                    f"{new_links}"
                    f"<!-- links -->"
                )
            else:
                subst = f"<!-- links {filter_dir} -->\n<!-- links -->"

            content = re.sub(
                lregex,
                lambda _: subst,
                content,
                flags=re.MULTILINE | re.DOTALL,
            )

        return content

@dataclass
class LoadParams:
    extract: str | None = None
    filter: bool = False
    rm_comments: bool = False
    tests_tio: int | None = None
    tests_table: int | None = None
    fenced: str | None = None

    @property
    def rmcom(self) -> bool:
        return self.rm_comments

    @rmcom.setter
    def rmcom(self, value: bool) -> None:
        self.rm_comments = value

    @property
    def tests(self) -> int | None:
        return self.tests_tio

    @tests.setter
    def tests(self, value: int | None) -> None:
        self.tests_tio = value

    @property
    def table(self) -> bool:
        return self.tests_table is not None

    @table.setter
    def table(self, value: bool) -> None:
        if value and self.tests_tio is not None:
            self.tests_table = self.tests_tio
            self.tests_tio = None

class Load:
    @staticmethod
    def extract_between_tags(content: str, tag: str) -> str:
        escaped = re.escape(tag)
        regex = r"\[\[" + escaped + r"\]\].*?\r?\n(.*?)^[^\r\n]*?\[\[" + escaped + r"\]\]"
        match = re.search(regex, content, re.MULTILINE | re.DOTALL)
        if match:
            return match.group(1)
        return ""

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
        
        raw_tests_tio: int | None = None
        raw_tests_table: int | None = None
        raw_tests: int | None = None
        had_legacy_table: bool = False
        mutually_exclusive_error: bool = False

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
                val = Load.__get_value(tokens, i)
                if val:
                    params.extract = val
                    i += 1  # Consome o valor
                else:
                    logger.warning(str(_MDPP_MISSING_EXTRACT_VALUE))
            elif token == "--filter":
                params.filter = True
            elif token in ("--rm-comments", "--rmcom"):
                params.rm_comments = True
            elif token == "--tests-tio":
                val = Load.__get_value(tokens, i)
                if val is not None:
                    try:
                        parsed = int(val)
                        if parsed < 0:
                            raise ValueError
                        raw_tests_tio = parsed
                        i += 1
                    except ValueError:
                        logger.warning(str(_MDPP_INVALID_TESTS_INTEGER))
                        i += 1
                else:
                    raw_tests_tio = 0
            elif token == "--tests-table":
                val = Load.__get_value(tokens, i)
                if val is not None:
                    try:
                        parsed = int(val)
                        if parsed < 0:
                            raise ValueError
                        raw_tests_table = parsed
                        i += 1
                    except ValueError:
                        logger.warning(str(_MDPP_INVALID_TESTS_INTEGER))
                        i += 1
                else:
                    raw_tests_table = 0
            elif token == "--tests":
                val = Load.__get_value(tokens, i)
                if val is not None:
                    try:
                        parsed = int(val)
                        if parsed < 0:
                            raise ValueError
                        raw_tests = parsed
                        i += 1
                    except ValueError:
                        logger.warning(str(_MDPP_INVALID_TESTS_INTEGER))
                        i += 1
                else:
                    raw_tests = 0
            elif token == "--table":
                had_legacy_table = True
            elif token.startswith("--"):
                logger.warning(str(_MDPP_UNRECOGNIZED_TAG).format(tag=token))
            
            i += 1  # Sempre avança para o próximo token

        if (raw_tests_tio is not None or raw_tests is not None) and (raw_tests_table is not None):
            logger.warning(str(_MDPP_MUTUALLY_EXCLUSIVE_TESTS))
            mutually_exclusive_error = True

        if not mutually_exclusive_error:
            if raw_tests_table is not None:
                params.tests_table = raw_tests_table
                if had_legacy_table:
                    logger.warning(str(_MDPP_DEPRECATED_TESTS_TABLE))
            elif raw_tests_tio is not None:
                params.tests_tio = raw_tests_tio
                if had_legacy_table:
                    logger.warning(str(_MDPP_DEPRECATED_TESTS_TABLE))
            elif raw_tests is not None:
                if had_legacy_table:
                    logger.warning(str(_MDPP_DEPRECATED_TESTS_TABLE))
                    params.tests_table = raw_tests
                else:
                    params.tests_tio = raw_tests
            elif had_legacy_table:
                logger.warning(str(_MDPP_UNRECOGNIZED_TAG).format(tag="--table"))

        return params

    @staticmethod
    def __calc_input_and_output_pad(arr: list[UnitData]) -> tuple[int, int]:
        input_lines: list[str] = []
        output_lines: list[str] = []
        for unit in arr:
            input_lines.extend(unit.input.splitlines())
            output_lines.extend(unit.output.splitlines())
        input_pad = max((len(line) for line in input_lines), default=0)
        output_pad = max((len(line) for line in output_lines), default=0)
        return input_pad, output_pad

    @staticmethod
    def generate_tests_from_test_toml(content: str, path: Path, cases: int, use_table: bool) -> str:
        def format_table(_input: str, _output: str, pad_input: int, pad_output: int) -> str:
            pad_input += 3
            if pad_input % 2 == 0:
                pad_input += 1
            pad_output += 3
            if pad_output % 2 == 0:
                pad_output += 1
            # Envolvemos o texto e o padding dentro da tag <code>
            header_in = f'{"Entrada".center(pad_input, " ")}'
            header_out = f'{"Saída".center(pad_output, " ")}'
            
            table_start = f'<table><tr><th><code>{header_in}</code>\n</th><th><code>{header_out}</code>\n</th></tr><tr><td valign="top"><pre>\n'
            table_mid = '</pre></td><td valign="top"><pre>\n'
            table_end = '</pre></td></tr></table>'
            
            return table_start + _input + table_mid + _output + table_end
        
        def format_simple_test_cases(_input: str, _output: str, pad: int) -> str:
            opening = "```py"
            before = f'{">>>>>>>> INSERT"}'
            middle = f'{"======== EXPECT"}'
            ending = f'{"<<<<<<<< FINISH"}'
            closing = "```"
            return f"{opening}\n{before}\n{_input}{middle}\n{_output}{ending}\n{closing}"

        from tko.loader.toml_parser import TomlParser
        test_data_list: list[UnitData] = TomlParser.extract_toml_units(content, path)
        if cases == 0:
            cases = len(test_data_list)
        elif cases > 0:
            test_data_list = test_data_list[:cases]
        pad_input, pad_output = Load.__calc_input_and_output_pad(test_data_list)
        if use_table:
            table_data_list = [format_table(unit.input, unit.output, pad_input, pad_output) for unit in test_data_list]
        else:
            pad = max(20, pad_input, pad_output)
            table_data_list = [format_simple_test_cases(unit.input, unit.output, pad) for unit in test_data_list]

        return "\n\n".join(table_data_list)

    @staticmethod
    def _process_file_content(abspath: Path, rel_path: str, params: LoadParams) -> str:
        """Encapsula a lógica de leitura e transformação do conteúdo."""
        if not abspath.is_file():
            logger.warning(str(_MDPP_FILE_NOT_FOUND).format(path=rel_path))
            return ""

        data = Decoder.load(abspath)

        # 1. extract
        if params.extract:
            tag = params.extract
            data = Load.extract_between_tags(data, tag)
        # 2. filter
        if params.filter:
            data = Filter(Path(rel_path)).process(data)
        # 3. remove comments
        if params.rm_comments:
            data = Load.rm_comments(abspath, data)
        # 4. tests-tio OR tests-table
        if params.tests_tio is not None:
            data = Load.generate_tests_from_test_toml(data, abspath, params.tests_tio, use_table=False)
        elif params.tests_table is not None:
            data = Load.generate_tests_from_test_toml(data, abspath, params.tests_table, use_table=True)
        # 5. fenced
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
        regex = r"<!-- load\s*(.*?)\s*-->\n(.*?)(?=<!-- load -->)<!-- load -->"
        
        def replace_tag_fn(match: re.Match[str]) -> str:
            full_command = match.group(1).strip()
            _ = match.group(2) 
            parts = full_command.split(maxsplit=1)
            path_str = parts[0] if len(parts) > 0 else ""
            flags_str = parts[1] if len(parts) > 1 else ""
            result = [f"<!-- load {full_command} -->"]
            if action == Action.RUN:
                params = Load.parse_tags(flags_str)
                abspath = (Path(target_dir) / path_str).resolve()
                result.append(Load._process_file_content(abspath, path_str, params))
            result.append("<!-- load -->")
            return "\n".join(result)

        # O sub substitui as ocorrências usando a função de callback
        return re.sub(regex, replace_tag_fn, content, flags=re.MULTILINE | re.DOTALL)

class Save:
    @staticmethod
    # execute filename and content
    def execute(file_content: str, target_dir: Path | None = None) -> None:
        regex = r"\[\]\(save\)\[\]\((.*?)\)\n```[a-z]*\n(.*?)```\n\[\]\(save\)"
        matches = re.finditer(regex, file_content, re.MULTILINE | re.DOTALL)
        content_old = ""        
        for match in matches:
            path_str = match.group(1)
            content = match.group(2)
            path = Path(path_str)
            if not path.is_absolute() and target_dir is not None:
                path = (target_dir / path).resolve()
            exists = path.is_file()
            if exists:
                content_old = Decoder.load(path)
            if not exists or content != content_old:
                Decoder.save(path, content)
                logger.info(str(_MDPP_FILE_UPDATED).format(path=path))

class MdppMain:
    @staticmethod
    def fix_path(target: Path):
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
        # path = MdppMain.fix_path(target)
        path = target
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
        updated = Load.execute(updated, target_dir, action)
        updated = Links.execute(target, updated, action)
        Save.execute(updated, target_dir)
        
        if updated != original:
            Decoder.save(path, updated)
            return True

        return False
