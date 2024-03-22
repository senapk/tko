import enum

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
            alone = len(line.split(" ")) == 1
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
