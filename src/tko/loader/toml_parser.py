import tomllib
from pathlib import Path
from typing import Any
from tko.util.decoder import Decoder


class TomlParser:
    def __init__(self):
        self.visited: set[Path] = set()

    def parse_toml(self, content: str, file: Path) -> list[dict[str, Any]]:
        main_list_name = "tests"
        load_command = "load"

        if file in self.visited:
            return []
        self.visited.add(file)

        try:
            data = tomllib.loads(content)
        except tomllib.TOMLDecodeError as _:
            return []

        result: list[dict[str, Any]] = []
        
        if load_command in data and isinstance(data[load_command], str):
            path = Path(data[load_command])
            result.extend(self.parse_toml(Decoder.load(path), path))

        if main_list_name not in data or not isinstance(data[main_list_name], list):
            return result

        for i, case in enumerate(data[main_list_name], start=1): # type:ignore
            if not isinstance(case, dict):
                raise ValueError(f"Case {i} inválido.")

            if "input" not in case or "output" not in case:
                print(f"warning: case {i} data: {case}") # type: ignore
                continue # ou raise ValueError(f"Case {i} inválido: campos 'input' e 'output' são obrigatórios.")

            if "input" in case:
                case["input"] = str(case["input"]) # type: ignore
                if case["input"] != "" and not case["input"].endswith("\n"): # type: ignore
                    case["input"] += "\n"

            if "output" in case:
                case["output"] = str(case["output"]) # type: ignore
                if case["output"] != "" and not case["output"].endswith("\n"):
                    case["output"] += "\n"

            parsed: dict[str, str] = {
                "input": case["input"],
                "output": case["output"],
            }

            if "label" in case:
                parsed["label"] = case["label"]

            if "grade_reduction" in case:
                parsed["grade_reduction"] = case["grade_reduction"]

            result.append(parsed)

        return result