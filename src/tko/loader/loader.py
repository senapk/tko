from __future__ import annotations
import re

from tko.loader.cio_parser import CioParser
from tko.loader.dir_parser import DirParser
from tko.loader.tio_parser import TioParser
from tko.loader.toml_parser import TomlParser
from tko.loader.vpl_parser import VplParser
from tko.run.unit import Unit
from tko.util.decoder import Decoder
from pathlib import Path

class Loader:

    @staticmethod
    def parse_vpl(text: str, source: Path) -> list[Unit]:
        data_list = VplParser.parse_vpl(text)
        output: list[Unit] = []
        for m in data_list:
            output.append(Unit(m.case, m.input, m.output, m.grade, source))
        return output
    
    @staticmethod
    def parse_toml(text: str, source: Path) -> list[Unit]:
        parser = TomlParser()
        data_list = parser.parse_toml(text, source)
        output: list[Unit] = []
        for m in data_list:
            case = m.label
            inp = m.input
            outp = m.output
            output.append(Unit(case, inp, outp, None, source))
        return output

    @staticmethod
    def extract_data_inside_code_fences(content: str, language: str = "") -> str:
        pattern = r'```' + language + r'\n(.*?)```'  # get only inside code blocks
        code = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        return "\n" + "\n".join(code)

    @staticmethod
    def parse_source(source: Path) -> list[Unit]:
        if source.is_dir():
            return DirParser.parse_dir(source)
        if source.is_file():
            #  if PreScript.exists():
            #      source = PreScript.process_source(source)
            content = Decoder.load(source)
            if source.suffix == ".vpl" or source.suffix == ".cases":
                return Loader.parse_vpl(content, source)
            elif source.suffix == ".tio":
                return TioParser.parse_tio(content, source)
            elif source.suffix == ".toml":
                return Loader.parse_toml(content, source)
            elif source.suffix == ".md":
                tests = TioParser.parse_tio(content, source)
                tests += CioParser.parse_cio(content, source)
                try:
                    content_fences = Loader.extract_data_inside_code_fences(content, "toml")
                    tests += Loader.parse_toml(content_fences, source)
                except ValueError:
                    pass
                return tests
            else:
                print("warning: target format do not supported: " + str(source))  # make this a raise
        else:
            raise FileNotFoundError('warning: unable to find: ' + str(source))
        return []
