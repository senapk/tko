from typing import Dict, List, Tuple, Optional, Union
from .game import Game, Task, Quest, Cluster
from .settings import RepoSettings, LocalSettings
from .down import Down
from .format import symbols, colour, red, cyan, green, yellow, Color
import subprocess
import shutil
import os
import re


class Util:
    @staticmethod
    def control(text: str):
        return colour("b,*", text)

    @staticmethod
    def cmd(text: str):
        return colour("r,*", text)

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
            return str(value)
        return "*"

    @staticmethod
    def get_percent(value, color2: str = "", pad = 0):
        text = f"{str(value)}%".rjust(pad)
        if value == 100:
            return colour("c," +  color2, "100%")
        if value >= 70:
            return colour("g," +  color2, text)
        if value == 0:
            return colour("r," +  color2, text)
        return colour("y," +  color2, text)

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

    def __init__(self, local: LocalSettings, game: Game, rep: RepoSettings, repo_alias: str, fnsave):
        self.fnsave = fnsave
        self.local = local
        self.repo_alias = repo_alias
        self.help_options = 0
        self.help_index = 0
        self.rep = rep
        self.show_toolbar = "toolbar" in self.rep.view
        self.admin_mode = "admin" in self.rep.view
        order = [entry for entry in self.rep.view if entry.startswith("order:")]
        if len(order) > 0:
            self.order = order[0][6:].split(",")
        else:
            self.order = []

        self.game: Game = game

        self.vfolds: Dict[str, str] = {} # visible collapsers ou expanders for clusters or quests
        self.vtasks: Dict[str, Task] = {}  # visible tasks  indexed by upper letter
        self.expanded: List[str] = [x for x in self.rep.expanded]
        self.new_items: List[str] = [x for x in self.rep.new_items]
        self.avaliable_quests: List[Quest] = [] # avaliable quests
        self.avaliable_clusters: List[Cluster] = [] # avaliable clusters

        self.first_loop = True

        self.load_rep()


    def save_to_json(self):
        self.rep.expanded = [x for x in self.expanded]
        self.rep.new_items = [x for x in self.new_items]

        self.rep.tasks = {}
        for t in self.game.tasks.values():
            if t.grade != 0:
                self.rep.tasks[t.key] = str(t.grade)
        self.rep.view = []
        self.rep.view.append("order:" + ",".join(self.order))
        if self.admin_mode:
            self.rep.view.append("admin")
        if self.show_toolbar:
            self.rep.view.append("toolbar")
            
        self.fnsave()


    def load_rep(self):
        for key, grade in self.rep.tasks.items():
            if key in self.game.tasks:
                value = "0"
                if grade == "x":
                    value = "10"
                elif grade == "":
                    value = "0"
                else:
                    value = grade
                self.game.tasks[key].set_grade(int(value))


    # return True if change view
    def update_avaliable_quests(self):
        old_quests = [q for q in self.avaliable_quests]
        old_clusters = [c for c in self.avaliable_clusters]
        if self.admin_mode:
            self.avaliable_quests = list(self.game.quests.values())
            self.avaliable_clusters = self.game.clusters
        else:
            self.avaliable_quests = self.game.get_reachable_quests()
            self.avaliable_clusters = []
            for c in self.game.clusters:
                if any([q in self.avaliable_quests for q in c.quests]):
                    self.avaliable_clusters.append(c)


        removed_clusters = [c for c in old_clusters if c not in self.avaliable_clusters]
        for c in removed_clusters:
            if c.key in self.expanded:
                self.expanded.remove(c.key)
        removed_quests = [q for q in old_quests if q not in self.avaliable_quests]
        for q in removed_quests:
            if q.key in self.expanded:
                self.expanded.remove(q.key)
        
        if self.first_loop:
            self.first_loop = False
            return

        added_clusters = [c for c in self.avaliable_clusters if c not in old_clusters]
        added_quests = [q for q in self.avaliable_quests if q not in old_quests]
        
        for c in added_clusters:
            self.new_items.append(c.key)
        for q in added_quests:
            self.new_items.append(q.key)

    @staticmethod
    def cut_limits(title, fn_gen):
        term_size = Util.get_term_size()
        clear_total = Color.len(fn_gen(title))
        dif = clear_total - term_size
        if dif < 0:
            return fn_gen(title)
        title = title[:-dif - 3] + yellow("...")
        return fn_gen(title)

    def str_task(self, key: str, t: Task, ligc: str, ligq: str, min_value = 1) -> str:
        vindex = colour("y,*", str(key).ljust(2, " "))
        vdone = t.get_grade_symbol(min_value)
        title = t.title

        def gen_saida(_title):
            opt = red("[opt]") if t.opt else ""

            parts = _title.split(" ")
            parts = [("@" + colour("*", p[1:]) if p.startswith("@") else p) for p in parts]
            titlepainted = " ".join(parts)
            return f" {ligc} {ligq}{vindex}{vdone} {titlepainted} {opt}"
        
        return Play.cut_limits(title, gen_saida)

    def str_quest(self, key: str, q: Quest, lig: str) -> str:
        key = colour("c,*", key.rjust(1))

        resume = ""
        for item in self.order:
            if item == "cont":
                resume += " " + q.get_resume_by_tasks()
            elif item == "perc":
                resume += " " + q.get_resume_by_percent().rjust(4)
            elif item == "goal":
                resume += " " + q.get_requirement()

        con = "━─"
        if q.key in self.expanded:
            con = "─┯"
        new = "" if q.key not in self.new_items else colour("g,*", " [new]")
        def gen_saida(_title):
            return f" {lig}{con}{key} {_title}{new}{resume}"
        
        return Play.cut_limits(q.title.strip(), gen_saida)

    def str_cluster(self, key: str, cluster: Cluster, quests: List[Quest]) -> str:
        opening = "━─"
        if cluster.key in self.expanded:
            opening = "─┯"

        resume = ""
        for item in self.order:
            if item == "cont":
                resume += " " + cluster.get_resume_by_quests()
            if item == "perc":
                resume += " " + cluster.get_resume_by_percent()

        title = Util.control(key) + " " + colour("*", cluster.title.strip())
        new = "" if cluster.key not in self.new_items else colour("g,*", " [new]")
        return f"{opening}{title}{new}{resume}"
    
    def get_avaliable_quests_from_cluster(self, cluster: Cluster) -> List[Quest]:
        return [q for q in cluster.quests if q in self.avaliable_quests]

    def show_options(self):
        fold_index = 0
        task_index = 0
        self.vfolds = {}
        self.vtasks = {}
        for cluster in self.avaliable_clusters:
            quests = self.get_avaliable_quests_from_cluster(cluster)

            key = str(fold_index)
            self.vfolds[str(key)] = cluster.key
            fold_index += 1
            print(self.str_cluster(key.ljust(2), cluster, quests))
            if not cluster.key in self.expanded: # va para proximo cluster
                continue

            for q in quests:
                key = str(fold_index).ljust(2)
                lig = "├" if q != quests[-1] else "╰"
                print(self.str_quest(key, q, lig))
                self.vfolds[str(fold_index)] = q.key
                fold_index += 1
                if q.key in self.expanded:
                    for t in q.tasks:
                        key = Util.calc_letter(task_index)
                        ligc = "│" if q != quests[-1] else " "
                        ligq = "├─" if t != q.tasks[-1] else "╰─"
                        print(self.str_task(key, t, ligc, ligq, q.tmin))
                        self.vtasks[key] = t
                        task_index += 1

    def process_collapse(self):
        quest_keys = [q.key for q in self.avaliable_quests]
        if any([q in self.expanded for q in quest_keys]):
            self.expanded = [key for key in self.expanded if key not in quest_keys]
        else:
            self.expanded = []

    def process_expand(self):
        # if any cluster outside expanded
        expand_clusters = False
        for c in self.avaliable_clusters:
            if c.key not in self.expanded:
                expand_clusters = True
        if expand_clusters:
            for c in self.avaliable_clusters:
                if c.key not in self.expanded:
                    self.expanded.append(c.key)
        else:
            for q in self.avaliable_quests:
                if q.key not in self.expanded:
                    self.expanded.append(q.key)

    def down_task(self, rootdir, task: Task, ext: str):
        if task.key in task.title:
            cmd = red(f"tko down {self.repo_alias} {task.key} -l {ext}")
            print(f"{cmd}")
            Down.download_problem(rootdir, self.repo_alias, task.key, ext)
        else:
            print(f"Essa não é uma tarefa de código")

    def check_rootdir(self):
        if self.local.rootdir == "":
            print("Diretório raiz para o tko ainda não foi definido")
            print("Você deseja utilizer o diretório atual")
            print("  " + red(os.getcwd()))
            print("como raiz para o repositório de " + self.repo_alias + "? (s/n) ", end="")
            answer = input()
            if answer == "s":
                self.local.rootdir = os.getcwd()
                self.fnsave()
                print("Você pode alterar o diretório raiz navegando para o diretório desejado e executando o comando")
                print("  " + red("tko config --root"))
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

        rootdir = os.path.relpath(os.path.join(self.local.rootdir, self.repo_alias))
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

    def collapse(self, key):
        self.expanded.remove(key)
        cluster = self.find_cluster(key)
        if cluster is not None:
            for q in cluster.quests:
                try:
                    self.expanded.remove(q.key)
                except ValueError:
                    pass

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
            if mass_action is None:
                if key in self.expanded:
                    self.collapse(key)
                    mass_action = "collapse"
                else:
                    self.expanded.append(key)
                    mass_action = "expand"
            else:
                if mass_action == "expand":
                    if key not in self.expanded:
                        self.expanded.append(key)
                else:
                    if key in self.expanded:
                        self.collapse(key)

        return True
    
    def process_tasks(self, actions):
        mass_action: Optional[int] = None
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
                if t.grade == 0:
                    t.set_grade(10)
                    mass_action = 10
                else:
                    t.set_grade(0)
                    mass_action = 0
            else:
                print(f"Talk {t} não processado")
                return False
        return True
    
    
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
            self.reset_view()
            print(f"\nLinguagem de programação alterada para {ext}")
            return False
        else:
            print(f"Extensão {ext} não processada")
            return False

    def take_actions(self, actions) -> bool:
        if len(actions) == 0:
            return True
        cmd = actions[0]

        if cmd == "<":
            self.process_collapse()
        elif cmd == "<<":
            self.process_collapse()
            self.process_collapse()
        elif cmd == ">":
            self.process_expand()
        elif cmd == ">>":
            self.process_expand()
            self.process_expand()
        elif cmd == "h" or cmd == "help":
            return self.show_cmds()
        elif cmd == "c" or cmd == "cont":
            if "cont" in self.order:
                self.order.remove("cont")
            else:
                self.order.append("cont")
        elif cmd == "p" or cmd == "perc":
            if "perc" in self.order:
                self.order.remove("perc")
            else:
                self.order.append("perc")
        elif cmd == "g" or cmd == "goal":
            if "goal" in self.order:
                self.order.remove("goal")
            else:
                self.order.append("goal")
        elif cmd == "a" or cmd == "admin":
            self.admin_mode = not self.admin_mode
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
        return green(symbols.opcheck) if value else yellow(symbols.opuncheck)

    def show_header(self):
        Util.clear()
        total_perc = 0
        
        for q in self.game.quests.values():
            total_perc += q.get_percent()
        if self.game.quests:
            total_perc = total_perc // len(self.game.quests)
        
        vtotal = colour("*,g", "Total: ") + Util.get_percent(total_perc, "bold", 4)

        intro = vtotal + " " + "│" + green(" Digite ") + Util.cmd("h") + red("elp")
        intro += green(" ou ") + Util.cmd("t") + red("oolbar") 
        intro += Play.checkbox(self.show_toolbar)
        vlink = Util.cmd("c") + red("ont") + (Play.checkbox("cont" in self.order))
        vperc = Util.cmd("p") + red("erc") + (Play.checkbox("perc" in self.order))
        vgoal = Util.cmd("g") + red("oal") + (Play.checkbox("goal" in self.order))

        vadmin = Util.cmd("a") + red("dmin") + (Play.checkbox(self.admin_mode))
        
        vext = Util.cmd("e") + red("xt") + "(" + colour("c,*", self.rep.lang) + ")"
        vrep = colour("y,*", self.repo_alias + ":")
        visoes = f"{vrep} {vext} {vlink} {vperc} {vgoal} {vadmin} "


        div0 = "────────────┴─────────────────────────"

        div1 = "──────────────────────────────────────"

        elementos = [intro] + ([div0, visoes] if self.show_toolbar else []) + [div1]
        self.print_elementos(elementos)

    def show_cmds(self):
        controles = green("Números ") + Util.control("azul") + green(" para expandir/colapsar")
        letrass = green("Letras ") + colour("y,*", "amarelo") + green(" para marcar/desmarcar")
        intervalos1 = green("Você pode digitar intervalos: ") + Util.control("1-3")
        intervalos2 = green("Você pode digitar intervalos: ") + Util.control("B-F")

        numeros = "─┯" + colour("c,*", "3") + "  Digite " + colour("c,*", "3") + (" para ver ou ocultar")
        
        letras = " ├─" + colour("y,*", "D ") + colour("m", symbols.uncheck)
        letras += " Tarefa. Dig " + Util.control("D") + " (des)marcar"
        
        graduar = " ╰─" + colour("y,*", "X ") + colour("r", "4")  + " Tarefa. Dig " + Util.control("X4") + " dar nota 4"
        todas = Util.control("<") + " ou " + Util.control(">") + green(" (Compactar ou Descompactar Tudo)")
        
        nomes_verm = green("Os nomes em vermelho são comandos")
        prime_letr = green("Basta a primeira letra do comando")
        down = Util.cmd("d") + red("own") + colour("y,*", " <TaskID ...>") + green(" (Download)")
        link = Util.cmd("l") + red("ink") + colour("y,*", " <TaskID ...>") + green(" (Ver links)")
        # manu = Util.cmd("m") + red("an") + yellow("  (Mostrar manual detalhado)")
        ext = Util.cmd("e") + red("xt") + "  <EXT>" + green(" (Mudar linguagem default)")
        sair = Util.cmd("q") + red("uit") + green(" (Sair do programa)")
        vcont = Util.cmd("c") + red("ont") + green(" (Alterna contador de tarefas)")
        vperc = Util.cmd("p") + red("erc") + green(" (Alterna mostrar porcentagem)")
        vgoal = Util.cmd("g") + red("oal") + green(" (Alterna mostrar meta mínima)")
        vupdate = Util.cmd("u") + red("pdate") + green(" (Recarrega o arquivo do repositório)")

        # rep = Util.cmd("r") + red("ep") + green(" (Muda o repositório)")

        vgame = Util.cmd("a") + red("dmin") + green(" (Modo admin para ver todas as missões)")
        # xp = Util.cmd("x") + red("p") + yellow("  (Mostrar experiência)")
        # indicadores = f"{vall} {vdone} {vinit} {vtodo}"

        div0 = "──────────────────────────────────────"
        div1 = "───────────── " + Util.control("Controles") + "──────────────"
        div2 = "───────────── " + colour("r,*", "Comandos") + " ───────────────"
        elementos = []
        elementos += [div1, controles, letrass, todas, numeros, letras, graduar, intervalos1, intervalos2]
        elementos += [div2, nomes_verm, prime_letr, down, link, ext, vcont, vperc, vgoal, vgame, sair]

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

    def generate_graph(self, graph_ext):

        reachable: List[str] = [q.key for q in self.avaliable_quests]
        counts = {}
        for q in self.game.quests.values():
            done = len([t for t in q.tasks if t.is_complete()])
            init = len([t for t in q.tasks if t.in_progress()])
            todo = len([t for t in q.tasks if t.not_started()])
            counts[q.key] = f"{done} / {done + init + todo}"
        self.game.generate_graph("graph", reachable, counts, graph_ext)

    def update_new(self):
        self.new_items = [item for item in self.new_items if item not in self.expanded]


    def reset_view(self):
        self.update_avaliable_quests()
        self.update_new()
        self.show_header()
        self.show_options()


    # return True if the user wants to continue playing
    def play(self, graph_ext: str) -> bool:
        success = True
        first_graph_msg = True 
        while True:
            if success:
                self.reset_view()

            if graph_ext != "":
                self.generate_graph(graph_ext)
                if first_graph_msg:
                    print("\nGrafo gerado em graph" + graph_ext)
                    first_graph_msg = False

            print("\n" + green("play$") + " ", end="")
            line = input()
            if line == "":
                success = True
                continue
            if line == "q" or line == "quit":
                return False
            if line == "u" or line == "update":
                return True
            actions = Util.expand_range(line)
            success = self.take_actions(actions)
            self.save_to_json()
