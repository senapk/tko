import enum
import os
from typing import List
import shutil

class Mode(enum.Enum):
    ADD = 1 # inserir cortando por degrau
    RAW = 2 # inserir tudo
    DEL = 3 # apagar tudo
    COM = 4 # inserir código removendo comentários

class Filter:
    def __init__(self, filename):
        self.mode = Mode.RAW
        self.backup_mode = Mode.RAW
        self.level = 1
        self.com = "//"
        if filename.endswith(".py"):
            self.com = "#"

    # decide se a linha deve entrar no texto
    def evaluate_insert(self, line: str):
        if self.mode == Mode.DEL:
            return False
        if self.mode == Mode.RAW:
            return True
        if self.mode == Mode.COM:
            return True
        if line == "":
            return True
        margin = (self.level + 1) * "    "
        if line.startswith(margin):
            return False

        return True

    def process(self, content: str) -> str:
        lines = content.split("\n")
        output = []
        for line in lines:
            two_words = len(line.strip().split(" ")) == 2
            if self.mode == Mode.COM:
                if not line.strip().startswith(self.com):
                    self.mode = self.backup_mode
            if two_words and line.endswith("$$") and self.mode == Mode.ADD:
                self.backup_mode = self.mode
                self.mode = Mode.COM
            elif line[-(3 + len(self.com)):-1] == self.com + "++":
                self.mode = Mode.ADD
                self.level = int(line[-1])
            elif line == self.com + "==":
                self.mode = Mode.RAW
            elif line == self.com + "--":
                self.mode = Mode.DEL
            elif self.evaluate_insert(line):
                if self.mode == Mode.COM:
                    line = line.replace(self.com + " ", "", 1)
                output.append(line)
        return "\n".join(output)

class FilterMode:

    @staticmethod
    def deep_filter_copy(source, destiny):
        if os.path.isdir(source):
            chain = source.split(os.sep)
            if len(chain) > 1 and chain[-1].startswith("."):
                return
            if not os.path.isdir(destiny):
                os.makedirs(destiny)
            for file in sorted(os.listdir(source)):
                FilterMode.deep_filter_copy(os.path.join(source, file), os.path.join(destiny, file))
        else:
            filename = os.path.basename(source)
            text_extensions = [".md", ".c", ".cpp", ".h", ".hpp", ".py", ".java", ".js", ".ts", ".hs"]

            if not any([filename.endswith(ext) for ext in text_extensions]):
                return
            
            content = open(source, "r").read()
            processed = Filter(filename).process(content)
            with open(destiny, "w") as f:
                f.write(processed)
            
            line = "";
            if processed != content:
                line += "(filtered): "
            else:
                line += "(        ): "
            line += destiny
            print(line)

    @staticmethod
    def deep_copy_and_change_dir():
        # path to ~/.tko_filter
        filter_path = os.path.join(os.path.expanduser("~"), ".tko_filter")
        try:
            if not os.path.isdir(filter_path):
                os.makedirs(filter_path)
            else:
                # force remove  non empty dir
                shutil.rmtree(filter_path)
                os.makedirs(filter_path)
        except FileExistsError as e:
            print("fail: Dir " + filter_path + " could not be created.")
            print("fail: verify your permissions, or if there is a file with the same name.")
        
        FilterMode.deep_filter_copy(".", filter_path)

        os.chdir(filter_path)

    # @staticmethod
    # def filter_targets_and_change_paths(targets) -> List[str]:
    #     # path to ~/.tko_filter
    #     filter_path = os.path.join(os.path.expanduser("~"), ".tko_filter")
    #     try:
    #         if not os.path.isdir(filter_path):
    #             os.makedirs(filter_path)
    #         else:
    #             # force remove  non empty dir
    #             shutil.rmtree(filter_path)
    #             os.makedirs(filter_path)
    #     except FileExistsError as e:
    #         print("fail: Dir " + filter_path + " could not be created.")
    #         print("fail: verify your permissions, or if there is a file with the same name.")
        
    #     new_targets = []

    #     for target in targets:
    #         destiny = os.path.join(filter_path, target)
    #         content = open(target, "r").read()
    #         processed = Filter(target).process(content)

    #         if processed != content:
    #             destiny_dir = os.path.dirname(destiny)
    #             if not os.path.isdir(destiny_dir):
    #                 os.makedirs(os.path.dirname(destiny))
    #             with open(destiny, "w") as f:
    #                 f.write(processed)
    #                 print("filtered : " + destiny)
    #             new_targets.append(destiny)
    #         else:
    #             new_targets.append(target)
    #     return new_targets
