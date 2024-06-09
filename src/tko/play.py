from typing import Dict, List, Tuple, Optional
from .game import Game, Task, Quest, Cluster
from .settings import RepoSettings
from .down import Down
from .format import GSym, colour, bold, red, cyan, green, yellow, Color
import subprocess
import shutil
import os
import re


class Util:
    @staticmethod
    def control(text: str):
        return bold("blue", text)

    @staticmethod
    def cmd(text: str):
        return bold("red", text)

    @staticmethod
    def calc_letter(index_letter: int):
        unit = index_letter % 26
        ten = index_letter // 26
        if ten == 0:
            return chr(ord("A") + unit)
        return chr(ord("A") + ten - 1) + chr(ord("A") + unit)

    @staticmethod
    def calc_index(letter: str):
        letter = letter.upper()
        if len(letter) == 1:
            return ord(letter) - ord("A")
        return (ord(letter[0]) - ord("A") + 1) * 26 + (ord(letter[1]) - ord("A"))

    @staticmethod
    def get_number(value: int):
        if 0 <= value <= 9:
            return GSym.numbers[value]
        return "*"

    @staticmethod
    def get_percent(value, color2: Optional[str]=None):
        text = f"{str(value).rjust(2)}%"
        if value == 100:
            return colour("c", GSym.check * 3, color2)
        if value >= 70:
            return colour("g", text, color2)
        if value == 0:
            return colour("r", text, color2)
        return colour("y", text, color2)

    @staticmethod
    def get_term_size():
        return shutil.get_terminal_size().columns
    
    @staticmethod
    def get_num_num(s: str):
        pattern = r"^(\d+)-(\d+)$"
        match = re.match(pattern, s)
        if match:
            return int(match.group(1)), int(match.group(2))
        else:
            return None, None

    @staticmethod
    def get_letter_letter(s: str) -> Tuple[Optional[str], Optional[str]]:
        pattern = r"([a-zA-Z]+)-([a-zA-Z]+)"
        match = re.match(pattern, s)
        if match:
            return match.group(1), match.group(2)
        return None, None
    
    @staticmethod
    def expand_range(line: str) -> List[str]:
        line = line.replace(" - ", "-")
        actions = line.split()

        expand: List[str] = []
        for t in actions:
            (start_number, end_number) = Util.get_num_num(t)
            (start_letter, end_letter) = Util.get_letter_letter(t)
            if start_number is not None and end_number is not None:
                expand += [str(v) for v in list(range(start_number, end_number + 1))]
            elif start_letter is not None and end_letter is not None:
                start_index = Util.calc_index(start_letter)
                end_index = Util.calc_index(end_letter)
                limits = range(start_index, end_index + 1)
                expand += [Util.calc_letter(i) for i in limits]
            else:
                expand.append(t)
        return expand
    
    @staticmethod
    def clear():
        subprocess.run("clear")
        pass

    @staticmethod
    def is_number(s):
        try:
            int(s)
            return True
        except ValueError:
            return False


class Play:
    cluster_prefix = "'"

    def __init__(self, game: Game, rep: RepoSettings, repo_alias: str, fnsave):
        self.fnsave = fnsave
        self.repo_alias = repo_alias
        self.help_options = 0
        self.help_index = 0
        self.rep = rep
        self.show_vbar = "vbar" in self.rep.view
        self.show_game = False

        self.show_perc = "perc" in self.rep.view
        self.hack_mode = "game" not in self.rep.view
        self.show_toolbar = "toolbar" in self.rep.view

        self.game: Game = game

        self.vfolds: Dict[str, str] = {} # visible collapsers ou expanders for clusters or quests
        self.vtasks: Dict[str, Task] = {}  # visible tasks  indexed by upper letter
        self.expanded: List[str] = []  # expanded quests or clusters
        self.avaliable: List[Quest] = [] # avaliable quests keys

        for k, v in self.rep.active.items():
            if "e" in v:
                self.expanded.append(k)

        for key, grade in rep.tasks.items():
            if key in game.tasks:
                game.tasks[key].set_grade(grade)


    def save_to_json(self):
        self.rep.active = {}
        for q in self.expanded:
            self.rep.active[q] = "e"
        self.rep.tasks = {}
        for t in self.game.tasks.values():
            if t.grade != "":
                self.rep.tasks[t.key] = t.grade
        self.rep.view = []
        if self.show_vbar:
            self.rep.view.append("vbar")
        if self.show_perc:
            self.rep.view.append("perc")
        if self.hack_mode:
            self.rep.view.append("hack")
        if self.show_game:
            self.rep.view.append("game")
        if self.show_toolbar:
            self.rep.view.append("toolbar")
        self.fnsave()

    def update_reachable(self):
        if self.hack_mode:
            self.avaliable = self.game.quests.values()
        else:
            self.avaliable = self.game.get_reachable_quests()


    def str_quest(self, key: str, q: Quest) -> str:
        opening = GSym.right2
        if q.key in self.expanded:
            opening = GSym.down2

        key = Util.control(key.rjust(2))

        title = q.title

        if self.show_vbar:
            if self.show_perc:
                resume = Util.get_percent(q.get_percent())
            else:
                done = Util.get_number(len([t for t in q.tasks if t.is_complete()]))
                init = Util.get_number(len([t for t in q.tasks if t.in_progress()]))
                todo = Util.get_number(len([t for t in q.tasks if t.not_started()]))
                resume = f"{green(done)}{yellow(init)}{red(todo)}"
            resume = resume + " "
        else:
            resume = ""

        return f"{resume}{opening} {key} {title}"

    def str_task(self, key: str, t: Task, lig: str) -> str:
        term_size = Util.get_term_size()
        vindex = Util.control(str(key).rjust(2, " "))
        vdone = t.get_grade()
        vlink = ""
        title = t.title
        extra = ""
        if self.show_vbar:
            extra = "    "

        def gen_saida(ligg: str):
            return f"{extra}{vdone}  {ligg}{vindex} {title}{vlink}"
        
        parts = title.split(" ")
        parts = [("@" + yellow(p[1:]) if p.startswith("@") else p) for p in parts]
        title = " ".join(parts)

        saida = gen_saida(lig)
        clear_total = Color.len(saida)
        dif = clear_total - term_size
        if dif < 0:
            return saida 
        title = title[:-dif - 3] + "..."

        return gen_saida(lig)

    @staticmethod
    def sort_keys(keys):
        single = [k for k in keys if len(str(k)) == 1]
        double = [k for k in keys if len(str(k)) == 2]
        return sorted(single) + sorted(double)

    def str_cluster(self, key: str, cluster_name: str, quests: List[Quest]) -> str:
        opening = GSym.right
        if cluster_name in self.expanded:
            opening = GSym.down

        if not self.show_perc:
            init = bold("y", Util.get_number(len([1 for q in quests if q.in_progress()])))
            done = bold("g", Util.get_number(len([1 for q in quests if q.is_complete()])))
            todo = bold("r", Util.get_number(len([1 for q in quests if q.not_started()])))
            resume = f"{done}{init}{todo} "
        else:
            total = 0
            for q in quests:
                total += q.get_percent()
            total = total // len(quests)
            resume = Util.get_percent(total, "bold") + " "
            
        title = Util.control(key) + " " + colour("bold", cluster_name.strip())
        opening = yellow(opening)
        if not self.show_vbar:
            resume = ""
        return f"{resume}{opening} {title}"
    
    # def find_cluster_keys(self) -> Dict[str, str]:
    #     data = sorted(self.game.cluster_order)
    #     keys = []
    #     for cluster in data:
    #         i = 2
    #         while True:
    #             key = cluster[:i]
    #             if key not in keys:
    #                 keys.append(key)
    #                 break
    #             i += 1
    #     output = {}
    #     for k, v in zip(keys, data):
    #         output[k] = v
    #     return output

    def show_options(self):
        fold_index = 0
        task_index = 0
        self.vfolds = {}
        self.vtasks = {}
        for cluster in self.game.clusters:
            quests = [q for q in cluster.quests if q in self.avaliable]
            if len(quests) == 0: # va para proximo cluster
                continue
            key = str(fold_index).rjust(2)
            print(self.str_cluster(key, cluster.title, quests))
            self.vfolds[str(fold_index)] = cluster.key
            fold_index += 1
            if not cluster.key in self.expanded: # va para proximo cluster
                continue

            for q in quests:
                key = str(fold_index).rjust(2)
                print(self.str_quest(key, q))
                self.vfolds[str(fold_index)] = q.key
                fold_index += 1
                if q.key in self.expanded:
                    for t in q.tasks:
                        key = Util.calc_letter(task_index)
                        lig = "├─" if t != q.tasks[-1] else "╰─"
                        print(self.str_task(key, t, lig))
                        self.vtasks[key] = t
                        task_index += 1

    def process_colapse(self):
        pass

    def process_expand(self):
        pass

    def down_task(self, rootdir, task: Task, ext: str):
        if task.key in task.title:
            cmd = red(f"tko down {self.repo_alias} {task.key} -l {ext}")
            print(f"{cmd}")
            Down.download_problem(rootdir, self.repo_alias, task.key, ext)
        else:
            print(f"Essa não é uma tarefa de código")

    def check_rootdir(self):
        if self.rep.rootdir == "":
            print("Diretório raiz para esse repositório ainda não foi definido")
            print("Você deseja utilizer o diretório atual")
            print("  " + red(os.getcwd()))
            print("como raiz para o repositório de " + self.repo_alias + "? (s/n) ", end="")
            answer = input()
            if answer == "s":
                self.rep.rootdir = os.getcwd()
                self.fnsave()
                print("Você pode alterar o diretório raiz navegando para o diretório desejado e executando o comando")
                print("  " + red("tko repo init " + self.repo_alias))
            else:
                print("Navegue para o diretório desejado e execute o comando novamente")
                exit(1)
    
    def check_language(self):
        if self.rep.lang == "":
            print("Linguagem de programação default para esse repositório ainda não foi definida")
            print("Escolha a linguagem de programação para o repositório de " + self.repo_alias)
            print("  [c, cpp, py, ts, js, java]: ", end="")
            lang = input()
            self.rep.lang = lang
            self.fnsave()
            print("Você pode mudar a linguagem de programação executando o comando")
            print("  " + red("ext <Extensão>"))

    def process_down(self, actions):
        if len(actions) < 2:
            print("Modo de usar: down <TaskID ...>")
            print("Exemplo: down A C-F")
            return False
        self.check_rootdir()
        self.check_language()

        rootdir = os.path.relpath(self.rep.rootdir)
        for t in actions[1:]:
            if t in self.vtasks:
                self.down_task(rootdir, self.vtasks[t], self.rep.lang)
            else:
                print(f"Tarefa {t} não encontrada")
                input()

    def find_cluster(self, key) -> Optional[Cluster]:
        for c in self.game.clusters:
            if c.key == key:
                return c
        return None

    def process_folds(self, actions):
        mass_action = None
        for t in actions:
            if not Util.is_number(t):
                print(f"Missão '{t}' não é um número")
                return False
            if not str(t) in self.vfolds:
                print(self.vfolds.keys())
                print(f"Entrada '{t}' não existe")
                return False
            key = self.vfolds[str(t)]
            if key in self.expanded:
                self.expanded.remove(key)
                cluster = self.find_cluster(key)
                if cluster is not None:
                    for q in cluster.quests:
                        try:
                            self.expanded.remove(q.key)
                        except ValueError:
                            pass
            else:
                self.expanded.append(key)

        return True
    
    def process_tasks(self, actions):
        mass_action = None
        for t in actions:
            letter = "".join([c for c in t if c.isupper() and not c.isdigit()])
            number = "".join([c for c in t if c.isdigit()])
            if letter in self.vtasks:
                t = self.vtasks[letter]
                if len(number) > 0:
                    t.set_grade(number)
                    continue
                
                if mass_action is not None:
                    t.set_grade(mass_action)
                    continue
                if t.grade == "":
                    t.set_grade("x")
                    mass_action = "x"
                else:
                    t.set_grade("")
                    mass_action = ""
            else:
                print(f"Talk {t} não processado")
                return False
        return True
    
    # def process_see(self, actions):
    #     if len(actions) > 1:
    #         if actions[1] in self.tasks:
    #             # print(self.tasks[actions[1]].link)
    #             self.read_link(self.tasks[actions[1]].link)
    #         else:
    #             print(f"{actions[1]} não processado")
    #             return False
    #     return True
    
    def process_link(self, actions):
        if len(actions) == 1:
            print("Após o comando passe a letra da tarefa para ver o link")
            return False
        for t in actions[1:]:
            if t in self.vtasks:
                # print(self.tasks[actions[1]].link)
                key = Util.control(t)
                link = self.vtasks[t].link
                print(f"{key} {link}")
            else:
                print(f"{t} não processado")
                return False
        return False
    
    def process_ext(self, actions):
        if len(actions) == 1:
            print("Após o comando passe a extensão desejada")
            return False
        ext = actions[1]
        if ext in ["c", "cpp", "py", "ts", "js", "java"]:
            self.rep.lang = ext
            self.fnsave()
            print(f"Linguagem de programação alterada para {ext}")
            return False
        else:
            print(f"Extensão {ext} não processada")
            return False

    def take_actions(self, actions) -> bool:
        if len(actions) == 0:
            return True
        cmd = actions[0]

        if cmd == "<":
            self.process_colapse()
        elif cmd == ">":
            self.process_expand()
        elif cmd == "m" or cmd == "man":
            return self.show_help()
        elif cmd == "h" or cmd == "help":
            return self.show_cmds()
        elif cmd == "v" or cmd == "vbar":
            self.show_vbar = not self.show_vbar
        elif cmd == "p" or cmd == "perc":
            self.show_perc = not self.show_perc
        elif cmd == "g" or cmd == "game":
            self.hack_mode = not self.hack_mode
        elif cmd == "t" or cmd == "toolbar":
            self.show_toolbar = not self.show_toolbar
        elif cmd == "d" or cmd == "down":
            return self.process_down(actions)
        elif cmd == "l" or cmd == "link":
            return self.process_link(actions)
        elif cmd == "e" or cmd == "ext":
            return self.process_ext(actions)
        elif Util.is_number(cmd):
            return self.process_folds(actions)
        elif cmd[0].isupper():
            return self.process_tasks(actions)
        else:
            print(f"{cmd} não processado")
            return False
        return True

    @staticmethod
    def show_help():
        output = "Digite " + red("t")
        output += " os números ou intervalo das tarefas para (marcar/desmarcar), exemplo:"
        print(output)
        print(green("play$ ") + "t 1 3-5")
        return False

    @staticmethod
    def checkbox(value):
        return green(GSym.vcheck) if value else yellow(GSym.vuncheck)

    def show_header(self):
        Util.clear()
        # ball = self.show_done and self.show_init and self.show_todo
        # full_count = len([q for q in self.quests.values()])
        # done_count = len([q for q in self.quests.values() if q.is_complete()])
        # init_count = len([q for q in self.quests.values() if q.in_progress()])
        # todo_count = len([q for q in self.quests.values() if q.not_started()])
        # vall = red("full") + (green(GSym.vcheck) if ball else yellow(GSym.vuncheck))
        # vdone = "(" + str(done_count).rjust(2, "0") + ")" + red("done") + checkbox(not ball and self.show_done)
        # vinit = "(" + str(init_count).rjust(2, "0") + ")" + red("init") + checkbox(not ball and self.show_init)
        # vtodo = "(" + str(todo_count).rjust(2, "0") + ")" + red("todo") + checkbox(not ball and self.show_todo)
        # vjoin = red("join") + ( checkbox(self.show_fold) )
        intro = green("Digite ") + Util.cmd("h") + green(" para ") + Util.cmd("h") + red("elp")
        intro += green(" ou ") + Util.cmd("t") + green(" para ") + Util.cmd("t") + red("oolbar") 
        intro += Play.checkbox(self.show_toolbar)
        vlink = Util.cmd("v") + red("bar") + (Play.checkbox(self.show_vbar))
        vperc = red("perc") + (Play.checkbox(self.show_perc))
        vhack = Util.cmd("g") + red("ame") + (Play.checkbox(not self.hack_mode))
        vgame = Util.cmd("x") + red("p") + (Play.checkbox(False))
        vext = Util.cmd("e") + red("xt") + "(" + colour("c", self.rep.lang, "bold") + ")"
        vrep = colour("y", self.repo_alias + ":", "bold")
        visoes = f"{vrep} {vext} {vlink} {vperc} {vhack} {vgame} "
        div0 = "──────────────────────────────────────"
        elementos = [intro] + ([div0, visoes] if self.show_toolbar else []) + [div0]
        self.print_elementos(elementos)

    def show_cmds(self):
        controles = green("Elementos em ") + Util.control("azul") + green(" são controles")
        feitos = bold("g", "1") + bold("y", "2") + bold("r", "3")
        feitos += green(" Feitos") + "/" + yellow("Iniciados") + "/" + red("Não Iniciados")
        cluster = GSym.right + Util.control(" Gr") + green("upo. Digite ")
        cluster += Util.control("Gr") + green(" para ver ou ocultar")
        numeros = GSym.right2 + Util.control("  3") + green(" Missão. Dig ")
        numeros += Util.control("3") + green(" para ver ou ocultar")
        letras = colour("g", GSym.check) + Util.control("  D")
        letras += green(" Tarefa. Dig ") + Util.control("D") + green(" (des)marcar")
        graduar = colour("r", "4") + Util.control("  X") + green(" Tarefa. Dig ")
        graduar += Util.control("X4") + green(" dar nota 4")
        todas = Util.control("<") + " ou " + Util.control(">") + yellow(" (Compactar ou Descompactar Tudo)")
        
        nomes_verm = green("Os nomes em vermelho são comandos")
        prime_letr = green("Basta a primeira letra do comando")
        down = Util.cmd("d") + red("own") + Util.control(" <TaskID ...>") + yellow(" (Download)")
        link = Util.cmd("l") + red("ink") + Util.control(" <TaskId ...>") + yellow(" (Ver links)")
        manu = Util.cmd("m") + red("an") + yellow("  (Mostrar manual detalhado)")
        ext = Util.cmd("e") + red("xt") + "  <EXT>" + yellow(" (Mudar linguagem default)")
        sair = Util.cmd("q") + red("uit") + yellow(" (Sair do programa)")
        vbar = Util.cmd("v") + red("bar") + yellow(" (Alterna mostrar barra vertical)")
        perc = Util.cmd("p") + red("erc") + yellow(" (Alterna mostrar porcentagens)")
        rep = Util.cmd("r") + red("ep") + yellow(" (Muda o repositório)")

        game = Util.cmd("g") + red("ame") + yellow(" (Quebra pré requisitos de missões)")
        xp = Util.cmd("x") + red("p") + yellow("  (Mostrar experiência)")

        # indicadores = f"{vall} {vdone} {vinit} {vtodo}"

        div0 = "──────────────────────────────────────"
        div1 = "───────────── " + Util.control("Controles") + "──────────────"
        div2 = "───────────── " + bold("r", "Comandos") + " ───────────────"
        elementos = []
        elementos += [div1, controles, feitos, todas, cluster, numeros, letras, graduar]
        elementos += [div2, nomes_verm, prime_letr, down, link, rep, ext, vbar, perc, game, xp, manu, sair]

        self.print_elementos(elementos)
        print(div0)
        return False

    @staticmethod
    def print_elementos(elementos):
        maxlen = max([len(Color.remove_colors(t)) for t in elementos])
        # qtd = term_size // (maxlen + 3)
        qtd = 1

        count = 0
        for i in range(len(elementos)):
            print(Color.ljust(elementos[i], maxlen), end="")
            count += 1
            if count >= qtd:
                count = 0
                print("")
            elif i < len(elementos) - 1:
                print(" ║ ", end="")
        if count != 0:
            print("")

    def play(self):
        success = True
        while True:
            if success:
                self.vtasks = {}
                self.update_reachable()
                self.show_header()
                self.show_options()
            print("\n" + green("play$") + " ", end="")
            line = input()
            if line == "":
                success = True
                continue
            if line == "q" or line == "quit":
                break
            actions = Util.expand_range(line)
            success = self.take_actions(actions)
            self.save_to_json()
