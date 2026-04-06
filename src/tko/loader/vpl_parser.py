from tko.loader.case_data import CaseData


import re


class VplParser:
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
        text += "input=" + unit.input
        text += "output=\"" + unit.output + "\"\n"
        if unit.grade is not None:
            text += "grade reduction=" + str(unit.grade) + "%\n"
        return text