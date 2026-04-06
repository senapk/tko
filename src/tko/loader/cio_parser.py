from tko.run.unit import Unit


import re
from pathlib import Path
from typing import Any


class CioParser:
    @staticmethod
    def parse_cio(text: str, source: Path):
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