from tko.run.unit import Unit


import re
from pathlib import Path


class TioParser:
    regex_tio = r"^[ ]*[>]+ ?INSERT[ ]*([^\n]*?)\n([\s\S]*?)^[ ]*[=]+ ?EXPECT[ ]*\n([\s\S]*?)^[ ]*[<]+ ?FINISH[ ]*$"
    regex_tio_origin = r"^>>>>>>>> *(.*?)\n(.*?)^======== *\n(.*?)^<<<<<<<<"

    @staticmethod
    def parse_tio(text: str, source: Path) -> list[Unit]:
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

        matches = re.findall(TioParser.regex_tio, text, re.MULTILINE | re.DOTALL)
        if len(matches) == 0:
            matches += re.findall(TioParser.regex_tio_origin, text, re.MULTILINE | re.DOTALL)
        unit_list: list[Unit] = []
        for m in matches:
            case, grade = parse_case_grade(m[0])
            unit_list.append(Unit(case, m[1], m[2], grade, source))
        return unit_list


    @staticmethod
    def parse_tio2(text: str):
        pattern = re.compile(
            r"===== ?(.*?) ?=====\n"   # caso com nome
            r"(.*?)"
            r">>>>>\n"
            r"(.*?)"
            r"<<<<<",
            re.DOTALL
        )

        pattern_no_label = re.compile(
            r"=====\n"                # caso sem nome
            r"(.*?)"
            r">>>>>\n"
            r"(.*?)"
            r"<<<<<",
            re.DOTALL
        )

        cases: list[dict[str, str]] = []

        for label, inp, out in pattern.findall(text):
            cases.append({
                "label": label.strip() or None, # type: ignore
                "input": inp.strip(),
                "expected": out.strip(),
            })

        for inp, out in pattern_no_label.findall(text):
            cases.append({
                "label": None, # type: ignore
                "input": inp.strip(),
                "expected": out.strip(),
            })

        return cases