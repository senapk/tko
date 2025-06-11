from __future__ import annotations
from typing import Any
import re
import os

from tko.run.unit import Unit
from tko.util.pattern_loader import PatternLoader
from tko.util.decoder import Decoder


class CaseData:
    def __init__(self, case: str="", inp: str="", outp: str="", grade: None | int = None):
        self.case: str = case
        self.input: str = VplParser.finish(inp)
        self.output: str = VplParser.unwrap(VplParser.finish(outp))
        self.grade: None | int = grade

    # @override
    def __str__(self) -> str:
        return "case=" + self.case + '\n' \
                + "input=" + self.input \
                + "output=" + self.output \
                + "gr=" + str(self.grade)

class VplParser:
    @staticmethod
    def finish(text: str):
        return text if text.endswith("\n") else text + "\n"

    @staticmethod
    def unwrap(text: str):
        while text.endswith("\n"):
            text = text[:-1]
        if text.startswith("\"") and text.endswith("\""):
            text = text[1:-1]
        return VplParser.finish(text)

    regex_vpl_basic = r"[cC]ase *= *([ \S]*) *\n *[iI]nput *=([\s\S]*?)^ *[oO]utput *=([\s\S]*?)(?=^ *[cC]ase *=|\Z)"
    regex_grade_reduction = r"([\s\S]*) *[Gg]rade [rR]eduction *= *(.*)%"

    @staticmethod
    def filter_quotes(x: str):
        return x[1:-2] if x.startswith('"') else x

    @staticmethod
    def parse_vpl(content: str) -> list[CaseData]:
        output: list[CaseData] = []
        for m in re.finditer(VplParser.regex_vpl_basic, content, re.MULTILINE):
            str_case = m.group(1)
            str_input = m.group(2)
            str_output = m.group(3)
            grade: int | None = None
            gr = re.match(VplParser.regex_grade_reduction, str_output, re.MULTILINE)
            if gr is not None:
                str_output = gr.group(1)
                grade = int(gr.group(2))
            output.append(CaseData(str_case, str_input, str_output, grade))
        return output

    @staticmethod
    def to_vpl(unit: CaseData):
        text = "case=" + unit.case + "\n"
        text += "inserted=" + unit.input
        text += "expected=\"" + unit.output + "\"\n"
        if unit.grade is not None:
            text += "grade reduction=" + str(unit.grade) + "%\n"
        return text


class Loader:
    # regex_tio = r"^ *#INPUT *(.*?)\n(.*?)^ *#OUTPUT *\n(.*?)^ *#END *\n?"
    regex_tio = r"^[ ]*[>]+ ?INSERT[ ]*([^\n]*?)\n([\s\S]*?)^[ ]*[=]+ ?EXPECT[ ]*\n([\s\S]*?)^[ ]*[<]+ ?FINISH[ ]*$"
    regex_tio_origin = r"^>>>>>>>> *(.*?)\n(.*?)^======== *\n(.*?)^<<<<<<<<"

    def __init__(self):
        pass

    @staticmethod
    def parse_cio(text: str, source: str):
        unit_list: list[Unit] = []
        text = "\n" + text

        pattern = r'```.*?\n(.*?)```'  # get only inside code blocks
        code = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
        # join all code blocks found
        text = "\n" + "\n".join(code)

        pieces: list[dict[str, Any]] = []  # header, input, output

        open_case = False
        for line in text.splitlines():
            if line.startswith("#__case") or line.startswith("#TEST_CASE"):
                pieces.append({"header": line, "input": [], "output": []})
                open_case = True
            elif open_case:
                pieces[-1]["output"].append(line)
                if line.startswith("$end"):
                    open_case = False

        # concatenando testes contínuos e finalizando testes sem $end
        for i in range(len(pieces)):
            output = pieces[i]["output"]
            if output[-1] != "$end" and i < len(pieces) - 1:
                pieces[i + 1]["output"] = output + pieces[i + 1]["output"]
                output.append("$end")

        # removendo linhas vazias e criando input das linhas com $
        for piece in pieces:
            piece["input"] = [line[1:] for line in piece["output"] if line.startswith("$")]
            piece["output"] = [line for line in piece["output"] if line != "" and not line.startswith("#")]

        for piece in pieces:
            case = " ".join(piece["header"].split(" ")[1:])
            inp = "\n".join(piece["input"]) + "\n"
            output = "\n".join(piece["output"]) + "\n"
            unit_list.append(Unit(case, inp, output, None, source))

        return unit_list

    @staticmethod
    def parse_tio(text: str, source: str = "") -> list[Unit]:

        # identifica se tem grade e retorna case name e grade
        def parse_case_grade(value: str) -> tuple[str, None | int]:
            if value.endswith("%"):
                words = value.split(" ")
                last = value.split(" ")[-1]
                _case = " ".join(words[:-1])
                grade_str = last[:-1]           # ultima palavra sem %
                try:
                    _grade = int(grade_str)
                    return _case, _grade
                except ValueError:
                    pass
            return value, None

        matches = re.findall(Loader.regex_tio, text, re.MULTILINE | re.DOTALL)
        if len(matches) == 0:
            matches += re.findall(Loader.regex_tio_origin, text, re.MULTILINE | re.DOTALL)
        unit_list: list[Unit] = []
        for m in matches:
            case, grade = parse_case_grade(m[0])
            unit_list.append(Unit(case, m[1], m[2], grade, source))
        return unit_list

    @staticmethod
    def parse_vpl(text: str, source: str = "") -> list[Unit]:
        data_list = VplParser.parse_vpl(text)
        output: list[Unit] = []
        for m in data_list:
            output.append(Unit(m.case, m.input, m.output, m.grade, source))
        return output

    @staticmethod
    def parse_dir(folder: str) -> list[Unit]:  # Updated return type to list[Unit]
        pattern_loader = PatternLoader()
        files = sorted(os.listdir(folder))
        matches = pattern_loader.get_file_sources(files)

        unit_list: list[Unit] = []  # Updated type to list[Unit]
        try:
            for m in matches:
                unit = Unit()
                unit.source = os.path.join(folder, m.label)
                unit.grade = 100
                input_file = os.path.join(folder, m.input_file)
                value = Decoder.load(input_file)
                unit.inserted = value + ("" if value.endswith("\n") else "\n")
                output_file = os.path.join(folder, m.output_file)
                value = Decoder.load(output_file)
                unit.set_expected(value + ("" if value.endswith("\n") else "\n"))
                unit_list.append(unit)
        except FileNotFoundError as e:
            print(str(e))
        return unit_list

    @staticmethod
    def parse_source(source: str) -> list[Unit]:
        if os.path.isdir(source):
            return Loader.parse_dir(source)
        if os.path.isfile(source):
            #  if PreScript.exists():
            #      source = PreScript.process_source(source)
            content = Decoder.load(source)
            if source.endswith(".vpl") or source.endswith(".cases"):
                return Loader.parse_vpl(content, source)
            elif source.endswith(".tio"):
                return Loader.parse_tio(content, source)
            elif source.endswith(".md"):
                tests = Loader.parse_tio(content, source)
                tests += Loader.parse_cio(content, source)
                return tests
            else:
                print("warning: target format do not supported: " + source)  # make this a raise
        else:
            raise FileNotFoundError('warning: unable to find: ' + source)
        return []
