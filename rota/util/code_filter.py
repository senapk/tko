import os
import argparse
from typing import Tuple
import shutil
from .decoder import Decoder

class Mark:
    def __init__(self, marker, indent):
        self.marker: str = marker
        self.indent: int = indent

    def __str__(self):
        return f"{self.marker}:{self.indent}"

class Mode:
    ADD = "ADD!"
    COM = "COM!"
    ACT = "ACT!"
    DEL = "DEL!"
    opts = [ADD, COM, ACT, DEL]

def get_comment(filename: str) -> str:
    com = "//"
    if filename.endswith(".py"):
        com = "#"
    elif filename.endswith(".puml"):
        com = "'"
    return com

class Filter:
    def __init__(self, filename):
        self.filename = filename
        self.stack = [Mark(Mode.ADD, 0)]
        self.com = get_comment(filename)

    def get_marker(self) -> str:
        return self.stack[-1].marker

    def get_indent(self) -> int:
        return self.stack[-1].indent

    def outside_scope(self, line):
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

    def search_temp_mode(self, line: str) -> Tuple[str, str]:
        for marker in Mode.opts:
            if line.rstrip().endswith(self.com + " " + marker):
                return marker, line[:-len(self.com + marker + " ")]
        return "---", line

    def __process(self, content: str) -> str:
        lines = content.splitlines()
        output = []
        for line in lines:
            while self.outside_scope(line):
                self.stack.pop()
            if self.has_single_mode_cmd(line):
                self.change_mode(line)
                continue
            marker = self.get_marker()
            pos_marker, line = self.search_temp_mode(line)
            if pos_marker != "---":
                marker = pos_marker

            if marker == Mode.DEL:
                continue
            elif marker == Mode.ADD:
                output.append(line)
            elif marker == Mode.ACT:
                prefix = " " * self.get_indent() + self.com + " "
                if not line.startswith(prefix):
                    prefix = prefix[:-1]
                line = line.replace(prefix, " " * self.get_indent(), 1)
                output.append(line)
            elif marker == Mode.COM:
                line = " " * self.get_indent() + self.com + " " + line[self.get_indent():]
                output.append(line)

        return "\n".join(output) + "\n"
    
    def process(self, content: str) -> str:
        return self.__process(content)

def clean_com(target: str, content: str) -> str:
    com = get_comment(target)
    lines = content.splitlines()
    output = [line for line in lines if not line.lstrip().startswith(com)]
    return "\n".join(output)

class DeepFilter:
    extensions = [".md", ".c", ".cpp", ".h", ".hpp", ".py", ".java", ".js", ".ts", ".hs", ".txt", ".go"]

    def __init__(self):
        self.cheat_mode = False
        self.quiet_mode = False
        self.indent = ""
    
    def print(self, *args, **kwargs):
        if not self.quiet_mode:
            print(self.indent, end="")
            print(*args, **kwargs)

    def set_indent(self, prefix: int):
        self.indent = prefix * " "
        return self

    def set_quiet(self, value):
        self.quiet_mode = (value == True)
        return self
    
    def set_cheat(self, value):
        self.cheat_mode = (value == True)
        return self

    def copy(self, source, destiny, deep: int):
        if deep == 0:
            return
        if os.path.isdir(source):
            chain = source.split(os.sep)
            if len(chain) > 1 and chain[-1].startswith("."):
                return
            if not os.path.isdir(destiny):
                os.makedirs(destiny)
            for file in sorted(os.listdir(source)):
                self.copy(os.path.join(source, file), os.path.join(destiny, file), deep - 1)
        else:
            filename = os.path.basename(source)

            if not any([filename.endswith(ext) for ext in self.extensions]):
                return

            content = Decoder.load(source)

            processed = Filter(filename).process(content)

            if self.cheat_mode:
                if processed != content:
                    cleaned = clean_com(source, content)
                    Decoder.save(destiny, cleaned)
            elif processed != "":
                Decoder.save(destiny, processed)

            line = ""
            if self.cheat_mode:
                if processed != content:
                    line += "(cleaned ): "
                else:
                    line += "(disabled): "
            else:
                if processed == "":
                    line += "(disabled): "
                elif processed != content:
                    line += "(filtered): "
                else:
                    line += "(        ): "
            line += destiny

            self.print(line)

class CodeFilter:
    @staticmethod
    def open_file(path): 
        if os.path.isfile(path):
            file_content = Decoder.load(path)
            return True, file_content
        print("Warning: File", path, "not found")
        return False, "" 

    @staticmethod
    def cf_recursive(target_dir: str, output_dir: str, force: bool, cheat: bool = False, quiet: bool = False, indent: int = 0):
        if output_dir is None:
                print("Error: output is required in recursive mode")
                exit()
        if not os.path.isdir(target_dir):
            print("Error: target must be a folder in recursive mode")
            exit()
        if os.path.exists(output_dir):
            if not force:
                print("Error: output folder already exists")
                exit()
            else:
                # recursive delete all folder content without deleting the folder itself
                for file in os.listdir(output_dir):
                    path = os.path.join(output_dir, file)
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)

        deep_filter = DeepFilter().set_cheat(cheat).set_quiet(quiet).set_indent(indent)
        deep_filter.copy(target_dir, output_dir, 10)

    @staticmethod
    def cf_single_file(target, output, update, cheat):
        file = target
        success, content = CodeFilter.open_file(file)
        if success:
            if cheat:
                content = clean_com(file, content)
            else:
                content = Filter(file).process(content)

            if output:
                if os.path.isfile(output):
                    old = Decoder.load(output)
                    if old != content:
                        Decoder.save(output, content)
                else:
                    Decoder.save(output, content)
            elif update:
                Decoder.save(file, content)
            else:
                print(content)

def cfmain():
    parser = argparse.ArgumentParser()
    parser.add_argument('target', type=str, help='file or folder to process')
    parser.add_argument('-u', '--update', action="store_true", help='update source file')
    parser.add_argument('-c', '--cheat', action="store_true", help='recursive cheat mode cleaning comments on students files')
    parser.add_argument('-o', '--output', type=str, help='output target')
    parser.add_argument("-r", "--recursive", action="store_true", help="recursive mode")
    parser.add_argument("-f", "--force", action="store_true", help="force mode")
    parser.add_argument("-q", "--quiet", action="store_true", help="quiet mode")
    parser.add_argument("-i", "--indent", type=int, default=0, help="indent using spaces")

    args = parser.parse_args()

    if args.cheat:
        args.recursive = True

    if args.recursive:
        CodeFilter.cf_recursive(args.target, args.output, force=args.force, cheat=args.cheat, quiet=args.quiet, indent=args.indent)
        exit()

    CodeFilter.cf_single_file(args.target, args.output, args.update, args.cheat)

if __name__ == '__main__':
    cfmain()
