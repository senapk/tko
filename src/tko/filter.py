import enum
import os
import argparse
from typing import Tuple

from .__init__ import __version__

# modes
# == RAW
# ++ CUT
# -- DEL
# $$ COM

class Mark:
    def __init__(self, marker, indent):
        self.marker: str = marker
        self.indent: int = indent

    def __str__(self):
        return f"{self.marker}{self.indent}"

class Mode(enum.Enum):
    ADD = 1 # inserir cortando por degrau
    RAW = 2 # inserir tudo
    DEL = 3 # apagar tudo

class LegacyFilter:
    def __init__(self, filename):
        self.mode = Mode.RAW
        self.level = 1
        self.com = "//"
        if filename.endswith(".py"):
            self.com = "#"
        elif filename.endswith(".puml"):
            self.com = "'"

    def process(self, content: str) -> str:
        lines = content.split("\n")
        output = []
        for line in lines:
            if line[-(3 + len(self.com)):-1] == self.com + "++":
                self.mode = Mode.ADD
                self.level = int(line[-1])
            elif line == self.com + "==":
                self.mode = Mode.RAW
            elif line == self.com + "--":
                self.mode = Mode.DEL
            elif self.mode == Mode.DEL:
                continue
            elif self.mode == Mode.RAW:
                output.append(line)
            elif self.mode == Mode.ADD:
                margin = (self.level + 1) * "    "
                if not line.startswith(margin):
                    output.append(line)
        return "\n".join(output)

class Filter:
    def __init__(self, filename):
        self.filename = filename
        self.stack = [Mark("==", 0)]
        self.com = "//"
        if filename.endswith(".py"):
            self.com = "#"
        elif filename.endswith(".puml"):
            self.com = "'"

    def get_marker(self) -> str:
        return self.stack[-1].marker

    def get_indent(self) -> int:
        return self.stack[-1].indent

    def outside_scope(self, line):
        left_spaces = len(line) - len(line.lstrip())
        return left_spaces < self.get_indent()

    def parse_mode(self, line):
        marker_list = ["$$", "++", "==", "--"]
        with_left = line.rstrip()
        word = with_left.lstrip()
        for marker in marker_list:
            if word == self.com + " " + marker:
                len_spaces = len(with_left) - len(self.com + " " + marker)
                while len(self.stack) > 0 and self.stack[-1].indent >= len_spaces:
                    self.stack.pop()
                self.stack.append(Mark(marker, len_spaces))
                return True
        return False


    def __process(self, content: str) -> str:
        lines = content.split("\n")
        output = []
        for line in lines:
            # print(line)
            # print(", ".join([str(st) for st in self.stack]))
            while self.outside_scope(line) and self.get_marker() != "++":
                self.stack.pop()
            if self.parse_mode(line):
                continue
            elif self.get_marker() == "--":
                continue
            elif self.get_marker() == "==":
                output.append(line)
            elif self.get_marker() == "$$":
                line = line.replace(" " * self.get_indent() + self.com + " ", " " * self.get_indent(), 1)
                output.append(line)
            elif self.get_marker() == "++" and not line.startswith((1 + self.get_indent()) * " "):
                output.append(line)
        return "\n".join(output)
    
    def process(self, content: str) -> str:
        content = LegacyFilter(self.filename).process(content)
        return self.__process(content)



def open_file(path): 
        if os.path.isfile(path):
            with open(path) as f:
                file_content = f.read()
                return True, file_content
        print("Warning: File", path, "not found")
        return False, "" 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='file to process')
    parser.add_argument('-u', '--update', action="store_true", help='update source file')
    parser.add_argument('-o', '--output', type=str, help='output file')
    parser.add_argument("-v", '--version', action="store_true", help='print version')
    args = parser.parse_args()

    if args.version:
        print(__version__)
        exit()

    success, content = open_file(args.file)
    if success:
        content = LegacyFilter(args.file).process(content)
        # content = Filter(args.file).process(content)

        if args.output:
            if os.path.isfile(args.output):
                old = open(args.output).read()
                if old != content:
                    open(args.output, "w").write(content)
            else:                
                open(args.output, "w").write(content)
        elif args.update:
            with open(args.file, "w") as f:
                f.write(content)
        else:
            print(content)

if __name__ == '__main__':
    main()
