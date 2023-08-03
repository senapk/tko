from typing import List, Optional
import re


class VplParser:
    @staticmethod
    def finish(text):
        return text if text.endswith("\n") else text + "\n"

    @staticmethod
    def unwrap(text):
        while text.endswith("\n"):
            text = text[:-1]
        if text.startswith("\"") and text.endswith("\""):
            text = text[1:-1]
        return VplParser.finish(text)

    @staticmethod
    class CaseData:
        def __init__(self, case="", inp="", outp="", grade: Optional[int] = None):
            self.case: str = case
            self.input: str = VplParser.finish(inp)
            self.output: str = VplParser.unwrap(VplParser.finish(outp))
            self.grade: Optional[int] = grade

        def __str__(self):
            return "case=" + self.case + '\n' \
                   + "input=" + self.input \
                   + "output=" + self.output \
                   + "gr=" + str(self.grade)

    regex_vpl_basic = r"case= *([ \S]*) *\n *input *=(.*?)^ *output *=(.*)"
    regex_vpl_extended = r"case= *([ \S]*) *\n *input *=(.*?)^ *output *=(.*?)^ *grade *reduction *= *(\S*)% *\n?"

    @staticmethod
    def filter_quotes(x):
        return x[1:-2] if x.startswith('"') else x

    @staticmethod
    def split_cases(text: str) -> List[str]:
        regex = r"^ *[Cc]ase *="
        subst = "case="
        text = re.sub(regex, subst, text, 0, re.MULTILINE | re.DOTALL)
        return ["case=" + t for t in text.split("case=")][1:]

    @staticmethod
    def extract_extended(text) -> Optional[CaseData]:
        f = re.match(VplParser.regex_vpl_extended, text, re.MULTILINE | re.DOTALL)
        if f is None:
            return None
        try:
            gr = int(f.group(4))
        except ValueError:
            gr = None
        return VplParser.CaseData(f.group(1), f.group(2), f.group(3), gr)

    @staticmethod
    def extract_basic(text) -> Optional[CaseData]:
        m = re.match(VplParser.regex_vpl_basic, text, re.MULTILINE | re.DOTALL)
        if m is None:
            return None
        return VplParser.CaseData(m.group(1), m.group(2), m.group(3), None)

    @staticmethod
    def parse_vpl(content: str) -> List[CaseData]:
        text_cases = VplParser.split_cases(content)
        seq: List[VplParser.CaseData] = []

        for text in text_cases:
            case = VplParser.extract_extended(text)
            if case is not None:
                seq.append(case)
                continue
            case = VplParser.extract_basic(text)
            if case is not None:
                seq.append(case)
                continue
            print("invalid case: " + text)
            exit(1)
        return seq

    @staticmethod
    def to_vpl(unit: CaseData):
        text = "case=" + unit.case + "\n"
        text += "input=" + unit.input
        text += "output=\"" + unit.output + "\"\n"
        if unit.grade is not None:
            text += "grade reduction=" + str(unit.grade) + "%\n"
        return text
