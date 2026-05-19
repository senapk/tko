import logging
from pathlib import Path
import shutil
from tko.i18n import Msg, t
from tko.util.rt import RT
from tko.util.decoder import Decoder
from typing import Any


logger = logging.getLogger(__name__)

_FILTER_ACTION_DISABLED_PATH = Msg(
    pt="action: disabled, path: {path}",
    en="action: disabled, path: {path}",
)
_FILTER_ACTION_PATH = Msg(
    pt="action: {action}, path: {path}",
    en="action: {action}, path: {path}",
)
_FILTER_FILE_NOT_FOUND = Msg(
    pt="Aviso: Arquivo {path} não encontrado",
    en="Warning: File {path} not found",
)
_FILTER_TARGET_MUST_BE_FOLDER = Msg(
    pt="Erro: target deve ser uma pasta no modo recursivo",
    en="Error: target must be a folder in recursive mode",
)
_FILTER_OUTPUT_FOLDER_REQUIRED = Msg(
    pt="Erro: pasta de saída deve ser especificada no modo recursivo",
    en="Error: output folder must be specified in recursive mode",
)
_FILTER_OUTPUT_FOLDER_EXISTS = Msg(
    pt="Erro: pasta de saída já existe",
    en="Error: output folder already exists",
)

class Mark:
    def __init__(self, marker: str, indent: int):
        self.marker: str = marker
        self.indent: int = indent

    # @override
    def __str__(self):
        return f"{self.marker}:{self.indent}"

class Mode:
    ADD = "ADD!"
    COM = "COM!"
    ACT = "ACT!"
    DEL = "DEL!"
    opts = [ADD, COM, ACT, DEL]

def get_comment(filename: Path) -> str:
    com = "//"
    if filename.suffix == ".py":
        com = "#"
    elif filename.suffix == ".hs":
        com = "--"
    elif filename.suffix == ".puml":
        com = "'"
    return com

class Filter:
    def __init__(self, filename: Path):
        self.filename = filename
        self.stack = [Mark(Mode.ADD, 0)]
        self.com = get_comment(filename)
        self.tab_char = "\t" if filename.suffix == ".go" else " "

    def get_marker(self) -> str:
        return self.stack[-1].marker

    def get_indent(self) -> int:
        return self.stack[-1].indent

    def outside_scope(self, line: str):
        stripped = line.strip()
        left_spaces = len(line) - len(line.lstrip())
        return stripped != "" and left_spaces < self.get_indent()

    def has_single_mode_cmd(self, line: str) -> bool:
        stripped = line.strip()
        for marker in Mode.opts:
            if stripped == self.com + " " + marker:
                return True
        return False

    def change_mode(self, line: str):
        with_left = line.rstrip()
        marker = with_left.lstrip()[len(self.com) + 1:]
        len_spaces = len(with_left) - len(self.com + marker + " ")
        while len(self.stack) > 0 and self.stack[-1].indent >= len_spaces:
            self.stack.pop()
        self.stack.append(Mark(marker, len_spaces))

    def search_temp_mode(self, line: str) -> tuple[str, int, str]:
        for marker in Mode.opts:
            if line.rstrip().endswith(self.com + " " + marker):
                count: int = 0
                for i in range(len(line)):
                    if line[i] == " ":
                        count += 1
                    else:
                        break
                return marker, count, line[:-len(self.com + marker + " ")].rstrip()
        return "---", 0, line

    def __process(self, content: str) -> str:
        lines = content.splitlines()
        output: list[str] = []
        for line in lines:
            while self.outside_scope(line):
                self.stack.pop()
            if self.has_single_mode_cmd(line):
                self.change_mode(line)
                continue
            marker: str = self.get_marker()
            indent: int = self.get_indent()
            temp_marker, temp_indent, line = self.search_temp_mode(line)
            if temp_marker != "---":
                marker = temp_marker
                indent = temp_indent

            if marker == Mode.DEL:
                continue
            elif marker == Mode.ADD:
                output.append(line)
            elif marker == Mode.ACT:
                prefix = self.tab_char * indent + self.com + " "
                if not line.startswith(prefix):
                    prefix = prefix[:-1]
                line = line.replace(prefix, self.tab_char * indent, 1)
                output.append(line)
            elif marker == Mode.COM:
                line = self.tab_char * indent + self.com + " " + line[indent:]
                output.append(line)

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
            print(self.indent, end="")
            print(*args, **kwargs)

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
                    print(t(_FILTER_ACTION_DISABLED_PATH, path=destiny))
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
                print(RT.parse(t(_FILTER_ACTION_PATH, action=f"[g]{action.name}[.]", path=path.resolve())))
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "w") as f:
                    f.write(action.content) 
            else:
                print(RT.parse(t(_FILTER_ACTION_DISABLED_PATH, path=path.resolve())))
        
class CodeFilter:
    @staticmethod
    def open_file(path: Path): 
        if path.is_file():
            file_content = Decoder.load(path)
            return True, file_content
        logger.warning(t(_FILTER_FILE_NOT_FOUND, path=path))
        return False, "" 

    @staticmethod
    def cf_recursive(source_dir: Path | str, destiny_dir: Path | str | None, force: bool, cheat: bool = False, quiet: bool = False, indent: int = 0):
        if isinstance(source_dir, str):
            source_dir = Path(source_dir)
        if isinstance(destiny_dir, str):
            destiny_dir = Path(destiny_dir)
        if not source_dir.is_dir():
            logger.error(t(_FILTER_TARGET_MUST_BE_FOLDER))
            exit()
        if destiny_dir is None:
            logger.error(t(_FILTER_OUTPUT_FOLDER_REQUIRED))
            exit()
        if destiny_dir.exists():
            if not force:
                logger.error(t(_FILTER_OUTPUT_FOLDER_EXISTS))
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
                print(content)

    @staticmethod
    def get_source_drafts_dir(source_dir: Path, language: str | None = None) -> Path:
        if language is None:
            return source_dir / ".cache" / "drafts"
        else:
            return source_dir / ".cache" / "drafts" / language

    @staticmethod
    def get_default_src_dir(source_dir: Path) -> Path:
        return source_dir / "src"
    
