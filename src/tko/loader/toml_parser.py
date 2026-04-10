import tomllib
from pathlib import Path
from tko.util.decoder import Decoder
from tko.loader.unit_data import UnitData

class TomlParser:

    @staticmethod
    def load_and_expand(origin: Path) -> str:
        test_cases: list[UnitData] = TomlParser().parse_toml(Decoder.load(origin), origin)
        content = "\n".join([TomlParser.to_toml(unit.label, unit.input, unit.output) for unit in test_cases])
        return content

    def parse_toml(self, content: str, file: Path) -> list[UnitData]:
        visited: set[Path] = set()
        return self.__parse_toml(content, file, visited)

    @staticmethod
    def to_toml(label: str, input: str, output: str) -> str:
        def _multiline(value: str) -> str:
            # Garante que termina com newline (TOML multiline padrão)
            if not value.endswith("\n"):
                value += "\n"
            return f"'''\n{value}'''"
        
        lines = ["[[tests]]"]

        # label primeiro
        if label:
            lines.append(f'label = {label!r}')

        # blocos multiline reais
        lines.append(f"input = {_multiline(input)}")
        lines.append(f"output = {_multiline(output)}")


        return "\n".join(lines) + "\n"
    
    @staticmethod
    def create_empty_toml() -> str:
        return "[[tests]]\nlabel = ''\ninput = '''\n'''\noutput = '''\n'''\n"

    def __parse_toml(self, content: str, file: Path, visited: set[Path]) -> list[UnitData]:
        main_list_name = "tests"
        load_command = "load"

        if file in visited:
            return []
        visited.add(file)

        try:
            data = tomllib.loads(content)
        except tomllib.TOMLDecodeError as _:
            return []

        result: list[UnitData] = []
        
        if load_command in data and isinstance(data[load_command], str):
            path = Path(data[load_command])
            if not path.is_absolute():
                path = (file.parent / path).resolve()
            result.extend(self.__parse_toml(Decoder.load(path), path, visited))

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

            data = UnitData()
            data.input = case["input"]
            data.output = case["output"]

            if "label" in case:
                data.label = case["label"]

            result.append(data)

        return result