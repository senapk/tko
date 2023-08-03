from typing import List
import re


class Replacer:

    def __init__(self):
        pass

    @staticmethod
    def _get_borders(regex, text, options) -> List[str]:
        out = []
        last = 0
        for m in re.finditer(regex, text, options):
            out.append(text[last:m.span()[0]])
            last = m.span()[1]
        out.append(text[last:])
        return out

    @staticmethod
    def _merge_tests(borders, tests):
        out = []
        for i in range(len(borders)):
            out.append(borders[i])
            if i < len(tests):
                out.append(tests[i])
        return out

    @staticmethod
    def insert_tests(regex: str, text: str, options: int, tests: List[str]) -> str:
        borders = Replacer._get_borders(regex, text, options)
        return "".join(Replacer._merge_tests(borders, tests))
