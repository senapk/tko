import tomllib
from pathlib import Path
from tko.i18n import Msg, t
from tko.util.decoder import Decoder
from tko.loader.unit_data import UnitData


_TOML_CASE_INVALID = Msg(
    pt="caso {index} inválido",
    en="invalid case {index}",
)
_TOML_CASE_DATA_WARNING = Msg(
    pt="aviso: caso {index} inválido: {case}",
    en="warning: invalid case {index}: {case}",
)

class TomlParser:

    @staticmethod
    def load_and_expand_from_path(origin: Path) -> str:
        return "\n".join(TomlParser.load_and_expand_from_content(Decoder.load(origin), origin))
    
    @staticmethod
    def load_and_expand_from_content(content: str, origin: Path) -> list[str]:
        test_cases: list[UnitData] = TomlParser.extract_toml_units(content, origin)
        return [TomlParser.data_to_toml_test(unit.label, unit.input, unit.output) for unit in test_cases]

    @staticmethod
    def extract_toml_units(content: str, file: Path) -> list[UnitData]:
        visited: set[Path] = set()
        return TomlParser.__parse_toml(content, file, visited)

    @staticmethod
    def data_to_toml_test(label: str, input: str, output: str) -> str:
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

    @staticmethod
    def __parse_toml(content: str, file: Path, visited: set[Path]) -> list[UnitData]:
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
            result.extend(TomlParser.__parse_toml(Decoder.load(path), path, visited))

        if main_list_name not in data or not isinstance(data[main_list_name], list):
            return result

        for i, case in enumerate(data[main_list_name], start=1): # type:ignore
            if not isinstance(case, dict):
                raise ValueError(t(_TOML_CASE_INVALID, index=i))

            if "input" not in case or "output" not in case:
                print(t(_TOML_CASE_DATA_WARNING, index=i, case=case)) # type: ignore
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