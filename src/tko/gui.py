from typing import List, Optional
import os
import subprocess
import configparser
import io

from .colored import Colored
from .core import Report


class Choose:
    base = ["poo", "ed", "fup"]
    view = ["down", "side"]
    extensions  = ["c", "cpp", "js", "ts", "py", "java", "h", "hpp"]

    def validate(ui: List[str], data_list: List[str]) -> Optional[str]:
        if len(ui) == 2:
            opts = [opt for opt in data_list if ui[1] in opt]
            if len(opts) == 1:
                return opts[0]
        return None

    def validate_or_choose_one(initial: str, ui: List[str], data_list: List[str]) -> str:
        value = Choose.validate(ui, data_list)
        if value is not None:
            return value
        value = Choose.choose_one(data_list)
        if value is not None:
            return value
        return initial
        

    def choose_many(data_list) -> List[str]:
        data_list = sorted(data_list)
        if (len(data_list) == 0):
            print("Sem opções disponíveis")
            return []
        options = []
        for i, data in enumerate(data_list):
            options.append(f"{Colored.green(str(i))}={data}")
        print("Digite os índices separando por espaço\n" + ", ".join(options) + ": ", end = "")
        choices = input()
        try:
            values = [data_list[int(choice)] for choice in choices.split(" ")]
            print("Opções escolhidas: " + Colored.green("[" + ", ".join(values) + "]"))
            return values
        except:
            pass
        return []

    def choose_one(data_list: List[str]) -> Optional[str]:
        if len(data_list) == 0:
            print("Sem opções disponíveis")
            return None
        options = []
        for i, data in enumerate(data_list):
            options.append(f"{Colored.green(str(i))}={data}")
        print(", ".join(options), end = "")
        choice = ""
        print(": ", end="")
        choice = input()
        try:
            index = int(choice)
            if index >= 0 and index < len(data_list):
                print("Opção escolhida: " + Colored.green(data_list[index]))
                return data_list[index]
        except:
            pass
        print("Opção inválida")
        return None

    def choose_index(ui):
        if len(ui) == 2:
            try:
                return int(ui[1])
            except:
                pass
        print("Choose test index or -1 for all: ", end="")
        choice = input()
        try:
            return int(choice)
        except:
            pass
        return -1

class Config:
    default_config_file = ".tkgui.ini"
        
    def __init__(self):
        self.view: str = ""          # updown or sidebyside diff
        self.base: str = ""          # which base to use
        self.case: int = -1          # run all or a specific index case
        self.folder: str = ""        # which folder to use
        self.tests: List[str] = []   # files with test testcases
        self.solvers: List[str] = [] # files with solvers
        self.last_cmd = ""           # last command
        self.config_file: str = ""   # config file
        self.root = ""               # root folder

    def create_default_config(self):
        config = configparser.ConfigParser()
        config["DEFAULT"] = {
            "base": Choose.base[0],
            "view": Choose.view[0],
            "case": "-1",
            "folder": "/",
            "tests": "",
            "solvers": "",
            "last_cmd": ""
        }
        with open(self.config_file, "w") as f:
            config.write(f)

    @staticmethod
    def validate_config(config):
        if "DEFAULT" not in config:
            return False
        if "base" not in config["DEFAULT"] or config["DEFAULT"]["base"] not in Choose.base:
            return False
        if "view" not in config["DEFAULT"] or config["DEFAULT"]["view"] not in Choose.view:
            return False
        if "case" not in config["DEFAULT"]:
            return False
        if "folder" not in config["DEFAULT"]:
            return False
        if "tests" not in config["DEFAULT"]:
            return False
        if "solvers" not in config["DEFAULT"]:
            return False
        if "last_cmd" not in config["DEFAULT"]:
            return False
        try:
            int(config["DEFAULT"]["case"])
        except:
            return False
        return True

    def save(self):
        config = configparser.ConfigParser()
        config["DEFAULT"] = {
            "base": self.base,
            "view": self.view,
            "case": str(self.case),
            "folder": self.folder,
            "tests": ",".join(self.tests),
            "solvers": ",".join(self.solvers),
            "last_cmd": self.last_cmd
        }
        with open(self.config_file, "w") as f:
            config.write(f)

    def load(self):
        parser = configparser.ConfigParser()

        self.config_file = self.search_config()
        if self.config_file == "":
            self.config_file = os.path.join(os.getcwd(), Config.default_config_file)
            print("Creating default config file")
            self.create_default_config()
        # else:
        #     print("Loading config file: " + self.config_file)
        
        self.root = os.path.dirname(self.config_file)
        os.chdir(self.root)

        parser.read(self.config_file)
        
        if not Config.validate_config(parser):
            print("fail: config file not valid, recreating")
            self.create_default_config()
            parser.read(self.config_file)

        self.base = parser["DEFAULT"]["base"]
        self.view = parser["DEFAULT"]["view"]
        self.case = int(parser["DEFAULT"]["case"])
        self.folder = parser["DEFAULT"]["folder"]
        tests = parser["DEFAULT"]["tests"].split(",")
        self.tests = [] if tests == [""] else tests
        solvers = parser["DEFAULT"]["solvers"].split(",")
        self.solvers = [] if solvers == [""] else solvers
        self.last_cmd = parser["DEFAULT"]["last_cmd"]

    
    def search_config(self) -> str:
        # recursively search for config file in parent directories
        path = os.getcwd()
        filename = Config.default_config_file
        while True:
            configfile = os.path.join(path, filename)
            if os.path.exists(configfile):
                return configfile
            if path == "/":
                return ""
            path = os.path.dirname(path)

    def __str__(self):
        return  "b.ase: " + self.base + "\n" + \
                "v.iew: " + self.view + "\n" + \
                "i.ndex: " + str(self.case) + "\n" + \
                "f.older: " + self.folder + "\n" + \
                "t.ests: " + str(self.tests) + "\n" + \
                "s.olvers: " + str(self.solvers) + "\n" + \
                "config_file: " + self.config_file + "\n"

class GuiActions:

    @staticmethod
    def print_help():
        print("Digite a letra ou o comando e aperte enter.")
        print("")
        print("b ou base: define a base de dados entre as disciplinas fup, ed e poo.")
        print("v ou view: alterna entre mostrar a visualização de erros up_down ou side_by_site.")
        print("c ou case: define o index do caso de teste a ser executado ou -1 para todos.")
        print("")
        print("d ou down: faz o download do problema utilizando o label e a extensão.")
        print("e ou exec: roda o problema esperando a entrada do usuário.")
        print("r ou run : avalia o código do problema contra os casos de testes escolhidos.")
        print("")
        print("l ou list: mostra os arquivos da pasta escolhida.")
        print("h ou help: mostra esse help.")
        print("q ou quit: finaliza o programa.")
        print("")
        print("f ou folder: troca a pasta com o exercício.")
        print("t ou tests: muda o arquivo que contém os testes.")
        print("s ou solver: seleciona qual arquivo(s) contém a resolução do problema.")
        print("Na linha de execução já aparece o último comando entre [], para reexecutar basta apertar enter.")

    @staticmethod
    def tests(config):
        if config.folder == "/":
            print("fail: selecione um folder primeiro")
            return
        files = os.listdir(config.folder)
        tests = [f for f in files if f.endswith(".tio") or f.endswith(".vpl")]
        config.tests = Choose.choose_many(tests)


    @staticmethod
    def solver(config):
        if config.folder == "/":
            print("fail: selecione um folder primeiro")
            return
        files = os.listdir(config.folder)
        solvers = []
        for ext in Choose.extensions:
            solvers += [f for f in files if f.endswith("." + ext)]
        config.solvers = Choose.choose_many(solvers)

    @staticmethod
    def run(config):
        if config.folder == "/":
            print("fail: selecione um folder primeiro")
            return
        cmd = ["tk", "run"]
        cmd += config.tests
        cmd += config.solvers
        if config.case != -1:
            cmd += ["-i", str(config.case)]
        if config.view == "down":
            cmd += ["-v"]
        print(Colored.green("$ " + " ".join(cmd)))
        os.chdir(config.folder)
        subprocess.run(cmd)
        os.chdir(config.root)

    @staticmethod
    def exec(config):
        if config.folder == "/":
            print("fail: selecione um folder primeiro")
            return
        cmd = ["tk", "exec"]
        cmd += config.solvers
        print(Colored.green("$ " + " ".join(cmd)))
        # imprime _ até o final da linha
        
        
        os.chdir(config.folder)
        subprocess.run(cmd)
        os.chdir(os.path.dirname(config.config_file))

    @staticmethod
    def down(ui_list, config: Config):
        
        def is_number(text):
            try:
                int(text)
                return True
            except:
                return False

        cmd = ["tk", "down"]
        cmd += [config.base]

        label = ""
        if len(ui_list) > 1 and len(ui_list[1]) == 3 and is_number(ui_list[1]):
            label = ui_list[1]
        else:
            print("label: ", end="")
            label = input()
        cmd += [label]
        
        ext = ""
        if len(ui_list) > 2 and ui_list[2] in Choose.extensions:
            ext += ui_list[2]
        else:
            print("ext: ", end="")
            ext = input()
        cmd += [ext]
        
        print("$ " + " ".join(cmd))
        os.chdir(os.path.dirname(config.config_file))
        subprocess.run(cmd)


    @staticmethod
    def list(config):
        if config.folder == "/":
            print("fail: selecione um folder primeiro")
            return
        files = os.listdir(config.folder)
        folders = [f for f in files if os.path.isdir(os.path.join(config.folder, f))]
        files = [f for f in files if not f in folders]
        readme = [f for f in files if f.endswith(".md")]
        files = [f for f in files if not f in readme]
        tests = [f for f in files if f.endswith(".tio") or f.endswith(".vpl")]
        files = [f for f in files if not f in tests]
        solvers = []
        for ext in Choose.extensions:
            solvers += [f for f in files if f.endswith("." + ext)]
        files = [f for f in files if not f in solvers]
        output = []
        pre = config.folder + os.sep
        output.append("  ".join(pre + Colored.blue(f) for f in folders))
        output.append("  ".join(pre + Colored.red(f) for f in readme))
        output.append("  ".join(pre + Colored.yellow(f) for f in tests))
        output.append("  ".join(pre + Colored.green(f) for f in solvers))
        output.append("  ".join(pre + Colored.magenta(f) for f in files))

        output = [o for o in output if len(o) > 0]

        print("\n".join(output))


    @staticmethod
    def load_folder(ui_list, config):
        folders = ["/"] + [f for f in os.listdir() if os.path.isdir(f) and not f.startswith(".")]
        if len(folders) == 0:
            print("Não há pastas para serem carregadas")
        else:        
            config.folder = Choose.validate_or_choose_one(config.folder, ui_list, folders)
            folder = config.folder
            config.tests = []
            config.solvers = []
            if folder == "/":
                return
            for ext in ["tio", "vpl"]:
                config.tests += [f for f in os.listdir(folder) if f.endswith("." + ext)]

            for ext in Choose.extensions:
                config.solvers += [f for f in os.listdir(folder) if f.endswith("." + ext)]
        

    @staticmethod
    def print_header(config):
        base = Colored.yellow(config.base.ljust(4))
        case = str(config.case)
        if case == "-1":
            case = "all"
        case = Colored.yellow(case.ljust(4))
        view = Colored.yellow(config.view.ljust(4))
        last = Colored.blue(config.last_cmd)
        
        folder = config.folder
        tests = "[" + ", ".join(config.tests) + "]"
        solvers = "[" + ", ".join(config.solvers) + "]"
        max_len = max(len(folder), len(tests), len(solvers))

        width = Report.get_terminal_size()
        total = 42
        used = 15
        mode = "side"
        avaliable = width - total - used
        needed = max_len

        length = min(avaliable, needed)
        if (width <= 70) and (total + max_len + used > width):
            mode = "down"
            length = total - used
        # length = total - 13
        cut = length - 4
        if len(folder) > length:
            folder = folder[:cut] + "..."
        if len(tests) > length:
            tests = tests[:cut] + "...]"
        if len(solvers) > length:
            solvers = solvers[:cut] + "...]"

        # larg = (max_len, length)
        folder = Colored.magenta(folder.ljust(length))
        tests = Colored.yellow(tests.ljust(length))
        solvers = Colored.green(solvers.ljust(length))

        def icon(name):
            return Colored.blue(name)

        a = "╭─{}───────{}╮ ╭──{}───────╮ ╭──{}───────╮ ".format("─", "─" * 4, "─", "─")
        b = "│ {} b·ase:{}╰╮╰╮ {} d·own ╰╮╰╮ {} l·ist ╰╮".format(icon("⚙"), base, icon("￬"), icon("⇟"))
        c = "│ {} v·iew:{} │ │ {} e·xec  │ │ {} h·elp  │".format(icon("🗘"), view, icon("▶"), icon("?"))
        d = "│ {} c·ase:{}╭╯╭╯ {} r·un  ╭╯╭╯ {} q·uit ╭╯".format(icon("⇶"), case, icon("✓"), icon("𞠊"))
        e = "╰─{}───────{}╯ ╰──{}───────╯ ╰──{}───────╯ ".format("─", "─" * 4, "─", "─")

        f = "╭──{}─────────{}─╮".format("─", "─" * length)
        g = "╰╮ {} f·older:{} │".format(icon("🗀"), folder)
        h = " │ {} t·ests :{} │".format(icon("⇉"), tests)
        i = "╭╯ {} s·olver:{} │".format(icon("⚒"), solvers)
        j = "╰──{}─────────{}─╯".format("─", "─" * length)

        menu = ""
        if mode == "side":
            menu += a + f + "\n" + b + g + "\n" + c + h + "\n" + d + i + "\n" + e + j + "\n"
        else:
            menu += a + "\n" + b + "\n" + c + "\n" + d + "\n" + e + "\n" 
            menu += f + "\n" + g + "\n" + h + "\n" + i + "\n" + j + "\n"
        menu += "[" + last + "] "

        output = io.StringIO()
        for i in range(0, len(menu) - 1):
            if menu[i + 1] == "·":
                output.write(Colored.red(menu[i]))
            else:
                output.write(menu[i])
        output.write(menu[-1])
        menu = output.getvalue()

        print(menu, end="")


def gui_main(_args):
    config = Config()
    config.load()
    while True: 
        Report.update_terminal_size()
        GuiActions.print_header(config)

        line = input()
        if line == "":
            line = config.last_cmd

        ui_list = line.split(" ")
        cmd = ui_list[0]

        if cmd == "q" or cmd == "quit":
            break
        elif cmd == "h" or cmd == "help":
            GuiActions.print_help()
        elif cmd == "b" or cmd == "base":
            config.base = Choose.validate_or_choose_one(config.base, ui_list, Choose.base)
        elif cmd == "v" or cmd == "view":
            config.view = Choose.validate_or_choose_one(config.view, ui_list, Choose.view)
        elif cmd == "c" or cmd == "case":
            config.case = Choose.choose_index(ui_list)
        elif cmd == "d" or cmd == "down":
            GuiActions.down(ui_list, config)
        elif cmd == "e" or cmd == "exec":
            GuiActions.exec(config)
        elif cmd == "r" or cmd == "run":
            GuiActions.run(config)
        elif cmd == "l" or cmd == "list":
            GuiActions.list(config)
        elif cmd == "f" or cmd == "folder":
            GuiActions.load_folder(ui_list, config)
        elif cmd == "t" or cmd == "tests":
            GuiActions.tests(config)
        elif cmd == "s" or cmd == "solver":
            GuiActions.solver(config)
        else:
            print("Invalid command")
        print("\nPressione ENTER para continuar...", end="")
        input()
        print("")
        config.last_cmd = cmd
        config.save()
    config.save()

