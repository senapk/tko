from pathlib import Path
import argparse
import shutil
from tko.util.decoder import Decoder
from typing import Any

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
    DISABLED = 0 # filtrado e completamente removido
    FILTERED = 1 # filtrado
    ORIGINAL = 2 # nenhuma marcação de filtragem
    COMCLEAN = 3 # comando de limpar comentários

    def __init__(self, action: int, content: str):
        self.action: int = action
        self.content: str = content

class DeepFilter:
    extensions = ["md", "c", "cpp", "h", "hpp", "py", "java", "js", "ts", "hs", "txt", "go", "json", "mod", "puml", "sh", "sql", "yaml", "exec", "hide", "tio", "zig"]

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
                    print("(disabled):", destiny)
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
                action_map[destiny] = Action(Action.ORIGINAL, "")
        line += f"{destiny}"

        self.print(line)

    def deploy_actions(self, actions: dict[Path, Action]):
        run_actions = False
        for _, action in actions.items():
            if action.action in [Action.FILTERED, Action.COMCLEAN]:
                run_actions = True
                break
        if not run_actions:
            print("Nenhuma filtragem encontrada, nenhuma ação tomada.")
            return
        for path, action in actions.items():
            if action.action in [Action.FILTERED, Action.COMCLEAN, Action.ORIGINAL]:
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "w") as f:
                    f.write(action.content) 
        
class CodeFilter:
    @staticmethod
    def open_file(path: Path): 
        if path.is_file():
            file_content = Decoder.load(path)
            return True, file_content
        print("Warning: File", path, "not found")
        return False, "" 

    @staticmethod
    def cf_recursive(target_dir: Path, output_dir: Path, force: bool, cheat: bool = False, quiet: bool = False, indent: int = 0):
        if not target_dir.is_dir():
            print("Error: target must be a folder in recursive mode")
            exit()
        if output_dir.exists():
            if not force:
                print("Error: output folder already exists")
                exit()
            else:
                # recursive delete all folder content without deleting the folder itself
                for item in output_dir.iterdir():
                    if item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                    else:
                        item.unlink()

        deep_filter = DeepFilter().set_cheat(cheat).set_quiet(quiet).set_indent(indent)
        deep_filter.execute(target_dir, output_dir, 10)

    @staticmethod
    def cf_single_file(target: Path, output: Path, update: bool, cheat: bool):
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
    def get_default_drafts_dir(source_dir: Path) -> Path:
        return source_dir / ".cache" / "drafts"

    @staticmethod
    def get_default_src_dir(source_dir: Path) -> Path:
        return source_dir / "src"
    
def filter_main(args: argparse.Namespace):
    if args.cheat:
        args.recursive = True

    if args.recursive:
        CodeFilter.cf_recursive(args.target, args.output, force=args.force, cheat=args.cheat, quiet=args.quiet, indent=args.indent)
        exit()

    CodeFilter.cf_single_file(args.target, args.output, args.update, args.cheat)


def build_drafts_main(args: argparse.Namespace):
    changedir = args.changedir
    here = Path(".").resolve() if changedir is None else Path(changedir).resolve()
    print(f"Updating drafts in {here}")
    source_src = CodeFilter.get_default_src_dir(here)
    drafts_dest = CodeFilter.get_default_drafts_dir(here)
    if source_src.is_dir():
        filter = DeepFilter().set_indent(4)
        filter.execute(source_src, drafts_dest, 5)
