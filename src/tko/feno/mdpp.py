#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import enum
from tko.feno.filter import Filter
from tko.util.decoder import Decoder
from pathlib import Path
from dataclasses import dataclass
from tko.loader.unit_data import UnitData


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
    def execute_toch(content: str) -> str:
        entries = TocMaker.extract_entries(content)
        links = [b for (a, b) in entries if a == 2]
        table = ["--" for _ in links]
        return " | ".join(links) + "\n" + " | ".join(table)
        

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

class Toch:
    @staticmethod
    def execute(content: str, action: Action = Action.RUN) -> str:
        regex = r"<!-- toch -->\n" + r"(.*?)"+ r"<!-- toch -->"
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
                        path = entry.resolve().relative_to(readme_dir)
                        output += "  " * depth + "- [" + entry.name + "](" + str(path) + ")\n"
            return output
        
        origin = readme_dir / filter_dir
        return traverse_directory(origin)

    @staticmethod
    def execute(path: Path, content: str, action: Action = Action.RUN) -> str:
        regex = r"<!-- links (\S*?) -->\n(.*?)<!-- links -->"
        matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)
        
        # replace content of group 2 with load_links of group 1 for each match
        for match in matches:
            filter_dir = match.group(1)
            lregex = r"<!-- links " + filter_dir + r" -->\n(.*?)<!-- links -->"
            if action == Action.RUN:
                readme_dir = path.parent.resolve()
                new_links = Links.load_links(readme_dir, Path(filter_dir))
                subst = r"<!-- links " + filter_dir + r" -->\n" + new_links + r"<!-- links -->"
            else:
                subst = r"<!-- links " + filter_dir + r" -->\n<!-- links -->"
            content = re.sub(lregex, subst, content, 0, re.MULTILINE | re.DOTALL)

        return content

@dataclass
class LoadParams:
    extract: str | None = None
    rmcom: bool = False
    fenced: str | None = None
    filter: bool = False
    table: bool = False
    tests: int | None = None

class Load:
    @staticmethod
    def extract_between_tags(content: str, tag: str) -> str:
        regex = r"\[\[" + tag + r"\]\].*?^(.*)^[\S ]*\[\[" + tag + r"\]\]"
        matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            return match.group(1)
        return ""

    @staticmethod
    def rmcom(target: Path, content: str) -> str:
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
            
            if token  == "--fenced":
                value = Load.__get_value(tokens, i)
                if value:
                    params.fenced = value
                    i += 1 # Consome o valor
                else:
                    params.fenced = "" # Se não houver valor, apenas ativa o fenced sem linguagem específica
            elif token == "--table":
                params.table = True
            elif token == "--extract":
                val = Load.__get_value(tokens, i)
                if val:
                    params.extract = val
                    i += 1 # Consome o valor
                else:
                    print(f"warning: missing value for --extract")
            elif token == "--tests":
                val = Load.__get_value(tokens, i)
                try:
                    if val:
                        params.tests = int(val)
                        i += 1 # Consome o valor
                    else:
                        raise ValueError
                except ValueError:
                    print(f"warning: invalid or missing integer for --tests")

            elif token == "--rmcom":
                params.rmcom = True

            elif token == "--filter":
                params.filter = True

            elif token.startswith("--"):
                print(f"warning: unrecognized tag '{token}'")
            
            i += 1 # Sempre avança para o próximo token
            
            # if params.tests is not None and not params.table:
            #     params.fenced = "py"
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
            print(f"warning: file {rel_path} not found")
            return ""

        data = Decoder.load(abspath)

        if params.extract:
            tag = params.extract
            data = Load.extract_between_tags(data, tag)
        if params.filter:
            data = Filter(Path(rel_path)).process(data)
        if params.rmcom:
            data = Load.rmcom(abspath, data)
        if params.tests is not None:
            data = Load.generate_tests_from_test_toml(data, abspath, params.tests, params.table)
        if params.fenced is not None:
            if params.fenced == "":
                lang = abspath.suffix[1:]
            else:
                lang = params.fenced
            data = f"```{lang}\n{data}\n```"

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
    def execute(file_content: str) -> None:
        regex = r"\[\]\(save\)\[\]\((.*?)\)\n```[a-z]*\n(.*?)```\n\[\]\(save\)"
        matches = re.finditer(regex, file_content, re.MULTILINE | re.DOTALL)
        content_old = ""        
        for match in matches:
            path = Path(match.group(1))
            content = match.group(2)
            exists = path.is_file()
            if exists:
                content_old = Decoder.load(path)
            if not exists or content != content_old:
                Decoder.save(path, content)
                print("file", path, "updated")

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
        print("Warning: File", path, "not found")
        return False, "" 

class Mdpp:
    @staticmethod
    def update_file(target: Path, action: Action = Action.RUN, quiet: bool = False) -> bool:
        # path = MdppMain.fix_path(target)
        path = target
        if not path.suffix == ".md":
            print("Warning: File", path, "is not a markdown file")
            return False
        if not path.is_file():
            print("Warning: File", path, "not found")
            return False
        target_dir = path.parent.resolve()
        found, original = MdppMain.open_file(path)
        if not found:
            return False
        updated = original
        updated_toc = Toc.execute(updated, action)
        updated_toc = Toch.execute(updated_toc, action)
        if updated != updated_toc:
            updated = updated_toc
        updated = Load.execute(updated, target_dir, action)
        updated = Links.execute(target, updated, action)
        Save.execute(updated)
        
        if updated != original:
            Decoder.save(path, updated)
            # hook = os.path.abspath(path).split(os.sep)[-2]
            return True

        return False
