from loguru import logger
from pathlib import Path
import re
import shutil
from dataclasses import dataclass
from enum import Enum
from tko.i18n import Msg
from tko.util.rt import RT
from tko.util.decoder import Decoder
from typing import Any
from tko.util.console import Console




_FILTER_ACTION_DISABLED_PATH = Msg.parse(
    pt="action: disabled, path: {path}",
    en="action: disabled, path: {path}",
)
_FILTER_ACTION_PATH = Msg.parse(
    pt="action: [g]{action}[], path: {path}",
    en="action: [g]{action}[], path: {path}",
)
_FILTER_FILE_NOT_FOUND = Msg.parse(
    pt="Aviso: Arquivo {path} não encontrado",
    en="Warning: File {path} not found",
)
_FILTER_TARGET_MUST_BE_FOLDER = Msg.parse(
    pt="Erro: target deve ser uma pasta no modo recursivo",
    en="Error: target must be a folder in recursive mode",
)
_FILTER_OUTPUT_FOLDER_REQUIRED = Msg.parse(
    pt="Erro: pasta de saída deve ser especificada no modo recursivo",
    en="Error: output folder must be specified in recursive mode",
)
_FILTER_OUTPUT_FOLDER_EXISTS = Msg.parse(
    pt="Erro: pasta de saída já existe",
    en="Error: output folder already exists",
)

class Mode(Enum):
    KEEP = "KEEP"
    DROP = "DROP"
    COM = "COM"
    UNC = "UNC"

    @classmethod
    def from_token(cls, token: str) -> "Mode | None":
        return {
            "@KEEP": cls.KEEP,
            "@DROP": cls.DROP,
            "@COM": cls.COM,
            "@UNC": cls.UNC,
            "ADD!": cls.KEEP,
            "DEL!": cls.DROP,
            "COM!": cls.COM,
            "ACT!": cls.UNC,
        }.get(token)


# Backwards compatibility attributes
Mode.ADD = Mode.KEEP  # type: ignore[attr-defined]
Mode.DEL = Mode.DROP  # type: ignore[attr-defined]
Mode.ACT = Mode.UNC  # type: ignore[attr-defined]
Mode.opts = ["@KEEP", "@DROP", "@COM", "@UNC", "ADD!", "DEL!", "COM!", "ACT!"]  # type: ignore[attr-defined]


@dataclass
class Mark:
    mode: Mode
    indent: int

    def __str__(self):
        return f"{self.mode.value}:{self.indent}"


@dataclass
class Directive:
    mode: Mode
    inline: bool
    code: str


def get_comment(filename: Path) -> str:
    com = "//"
    if filename.suffix in [".py", ".sh", ".bash", ".toml", ".yaml", ".yml", ".tio", ".r", ".rb"]:
        com = "#"
    elif filename.suffix in [".hs", ".sql", ".lua"]:
        com = "--"
    elif filename.suffix == ".puml":
        com = "'"
    return com


def is_offset_in_string(line: str, offset: int, com: str) -> bool:
    in_quote: str | None = None
    escaped = False
    for i, ch in enumerate(line):
        if i >= offset:
            break
        if in_quote is not None:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == in_quote:
                in_quote = None
        else:
            if com != "'" and ch in ('"', "'", "`"):
                in_quote = ch
            elif com == "'" and ch == '"':
                in_quote = ch
            elif line.startswith(com, i):
                return False
    return in_quote is not None


class Filter:
    def __init__(self, filename: Path):
        self.filename = filename
        self.stack = [Mark(Mode.KEEP, 0)]
        self.com = get_comment(filename)

    def current_mark(self) -> Mark:
        return self.stack[-1]

    @staticmethod
    def indent_text(line: str) -> str:
        return line[: len(line) - len(line.lstrip(" \t"))]

    @staticmethod
    def indent_column(line: str, tab_size: int = 4) -> int:
        return len(Filter.indent_text(line).expandtabs(tab_size))

    def parse_directive(self, line: str) -> Directive | None:
        stripped = line.strip()
        if stripped == "":
            return None

        # Check block directive (line contains only the comment tag)
        if stripped.startswith(self.com):
            payload = stripped[len(self.com):].strip()
            mode = Mode.from_token(payload)
            if mode is not None:
                return Directive(mode, inline=False, code="")

        # Check inline directive at the end of the line
        pattern = rf"(?:^|[\t ]){re.escape(self.com)}\s*(@KEEP|@DROP|@COM|@UNC|ADD!|DEL!|COM!|ACT!)\s*$"
        match = re.search(pattern, line)
        if match:
            start_idx = line.find(self.com, match.start())
            if not is_offset_in_string(line, start_idx, self.com):
                token = match.group(1)
                mode = Mode.from_token(token)
                if mode is not None:
                    code = line[:start_idx].rstrip()
                    if code.strip() == "":
                        return Directive(mode, inline=False, code="")
                    return Directive(mode, inline=True, code=code)

        return None

    def comment_line(self, line: str) -> str:
        if line.strip() == "":
            return line
        indent = self.indent_text(line)
        return f"{indent}{self.com} {line[len(indent):]}"

    def uncomment_line(self, line: str) -> str:
        if line.strip() == "":
            return line
        indent = self.indent_text(line)
        body = line[len(indent):]
        if body.startswith(self.com + " "):
            return f"{indent}{body[len(self.com) + 1:]}"
        if body.startswith(self.com):
            return f"{indent}{body[len(self.com):]}"
        return line

    def __process(self, content: str) -> str:
        if not content:
            return ""

        lines = content.splitlines()
        output: list[str] = []
        self.stack = [Mark(Mode.KEEP, 0)]

        for line in lines:
            if line.strip() == "":
                mode = self.stack[-1].mode
                if mode != Mode.DROP:
                    output.append(line)
                continue

            column = self.indent_column(line)

            # Pop scopes closed by reduced indentation
            while len(self.stack) > 1 and column < self.stack[-1].indent:
                self.stack.pop()

            directive = self.parse_directive(line)

            if directive is not None and not directive.inline:
                # Block directive: pop any scope at same or deeper level
                while len(self.stack) > 1 and column <= self.stack[-1].indent:
                    self.stack.pop()
                self.stack.append(Mark(directive.mode, column))
                continue

            if directive is not None and directive.inline:
                mode = directive.mode
                source_line = directive.code
            else:
                mode = self.stack[-1].mode
                source_line = line

            if mode == Mode.DROP:
                continue
            elif mode == Mode.KEEP:
                output.append(source_line)
            elif mode == Mode.COM:
                output.append(self.comment_line(source_line))
            elif mode == Mode.UNC:
                output.append(self.uncomment_line(source_line))

        if not output:
            return ""

        return "\n".join(output) + "\n"

    def process(self, content: str) -> str:
        return self.__process(content)

def clean_com(target: Path, content: str) -> str:
    com = get_comment(target)
    lines = content.splitlines()
    output = [line for line in lines if not line.lstrip().startswith(com)]
    return "\n".join(output)

class Action:
    DISABLED = "disabled" # filtrado e completamente removido
    FILTERED = "filtered" # filtrado
    ORIGINAL = "original" # nenhuma marcação de filtragem
    COMCLEAN = "comclean" # comando de limpar comentários

    def __init__(self, action: str, content: str):
        self.name: str = action
        self.content: str = content

class DeepFilter:
    include = ["md", "txt", "toml", "tio", "json", "puml", "yaml"]
    extensions = ["c", "cpp", "h", "hpp", "py", "java", "js", "ts", "hs", "go", "mod", "sh", "sql", "exec", "hide", "zig"] + include

    def __init__(self):
        self.cheat_mode = False
        self.quiet_mode = False
        self.indent = ""
    
    def print(self, *args: str, **kwargs: Any):
        if not self.quiet_mode:
            Console.print(self.indent, end="")
            Console.print(*args, **kwargs)

    def set_indent(self, prefix: int):
        self.indent = prefix * " "
        return self

    def set_quiet(self, value: bool):
        self.quiet_mode = (value == True)
        return self
    
    def set_cheat(self, value: bool):
        self.cheat_mode = (value == True)
        return self

    def execute(self, source: Path | str, destiny: Path | str, deep: int):
        actions: dict[Path, Action] = {}
        self.__prepare_actions(source, destiny, 10, actions)
        self.deploy_actions(actions)

    def __prepare_actions(self, source: Path | str, destiny: Path | str, deep: int, action_map: dict[Path, Action]):
        source = Path(source)
        destiny = Path(destiny)
        if deep == 0:
            return
        
        if source.is_dir():
            if source.name.startswith("."):
                return
            for item in sorted(source.iterdir()):
                self.__prepare_actions(item, destiny / item.name, deep - 1, action_map)
            return
        
        filename = source
        folder = source.parent
        deny_list = folder / ".deny"
        if deny_list.is_file():
            with open(deny_list) as f:
                deny = [x.strip() for x in f.read().splitlines()]
                if filename in deny:
                    Console.print(RT.parse(str(_FILTER_ACTION_DISABLED_PATH).format(path=destiny)))
                    action_map[destiny] = Action(Action.DISABLED, "")
                    return

        if not any([filename.suffix == f".{ext}" for ext in self.extensions]):
            return
        content = Decoder.load(source)

        processed = Filter(filename).process(content)

        if self.cheat_mode and processed != content:
            content = clean_com(source, content)

        line = ""
        if self.cheat_mode:
            if processed != content:
                line += "(cleaned ): "
                action_map[destiny] = Action(Action.COMCLEAN, content)
            else:
                line += "(disabled): "
                action_map[destiny] = Action(Action.DISABLED, "")
        else:
            if processed == "" or processed == "\n":
                line += "(disabled): "
                action_map[destiny] = Action(Action.DISABLED, "")
            elif processed != content:
                line += "(filtered): "
                action_map[destiny] = Action(Action.FILTERED, processed)
            else:
                line += "(original): "
                action_map[destiny] = Action(Action.ORIGINAL, content)
        line += f"{destiny}"

        # self.print(line)

    def deploy_actions(self, actions: dict[Path, Action]):
        folder_actions: dict[Path, list[tuple[Path, Action]]] = {}
        for path, action in actions.items():
            parent = path.parent.resolve()
            if parent not in folder_actions:
                folder_actions[parent] = []
            folder_actions[parent].append((path, action))
        for _, action_list in folder_actions.items():
            self.__deploy_actions(action_list)

    def __deploy_actions(self, actions: list[tuple[Path, Action]]):
        run_actions = False
        for path, action in actions:
            if action.name in [Action.FILTERED, Action.COMCLEAN]:
                run_actions = True
                break
        # if not run_actions:
        #     print(RT.parse(f"Nenhuma filtragem encontrada para a pasta [r]{parent}[.], nenhuma ação tomada."))
        #     return
        for path, action in actions:
            if (run_actions or path.suffix[1:] in DeepFilter.include) and action.name in [Action.FILTERED, Action.COMCLEAN, Action.ORIGINAL] :
                Console.print(RT.parse(str(_FILTER_ACTION_PATH).format(action=action.name, path=path.resolve())))
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "w") as f:
                    f.write(action.content) 
            else:
                Console.print(RT.parse(str(_FILTER_ACTION_DISABLED_PATH).format(path=path.resolve())))
        
class CodeFilter:
    @staticmethod
    def open_file(path: Path): 
        if path.is_file():
            file_content = Decoder.load(path)
            return True, file_content
        logger.warning(str(_FILTER_FILE_NOT_FOUND).format(path=path))
        return False, "" 

    @staticmethod
    def cf_recursive(source_dir: Path | str, destiny_dir: Path | str | None, force: bool, cheat: bool = False, quiet: bool = False, indent: int = 0):
        if isinstance(source_dir, str):
            source_dir = Path(source_dir)
        if isinstance(destiny_dir, str):
            destiny_dir = Path(destiny_dir)
        if not source_dir.is_dir():
            logger.error(str(_FILTER_TARGET_MUST_BE_FOLDER))
            exit()
        if destiny_dir is None:
            logger.error(str(_FILTER_OUTPUT_FOLDER_REQUIRED))
            exit()
        if destiny_dir.exists():
            if not force:
                logger.error(str(_FILTER_OUTPUT_FOLDER_EXISTS))
                exit()
            else:
                # recursive delete all folder content without deleting the folder itself
                for item in destiny_dir.iterdir():
                    if item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                    else:
                        item.unlink()

        deep_filter = DeepFilter().set_cheat(cheat).set_quiet(quiet).set_indent(indent)
        deep_filter.execute(source_dir, destiny_dir, 10)

    @staticmethod
    def cf_single_file(target: Path, output: Path | None, update: bool, cheat: bool):
        file = Path(target)
        success, content = CodeFilter.open_file(file)
        if success:
            if cheat:
                content = clean_com(file, content)
            else:
                content = Filter(file).process(content)

            if output:
                if output.is_file():
                    old = Decoder.load(output)
                    if old != content:
                        Decoder.save(output, content)
                else:
                    Decoder.save(output, content)
            elif update:
                Decoder.save(file, content)
            else:
                Console.print(content)

    @staticmethod
    def get_source_drafts_dir(source_dir: Path, language: str | None = None) -> Path:
        if language is None:
            return source_dir / ".cache" / "drafts"
        else:
            return source_dir / ".cache" / "drafts" / language

    @staticmethod
    def get_default_src_dir(source_dir: Path) -> Path:
        return source_dir / "src"
    
