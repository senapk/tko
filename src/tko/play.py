from .game import Game, Task, Quest, Cluster, Graph, XP
from .settings import RepoSettings, LocalSettings
from .down import Down
from .format import symbols, colour, Color
import shutil
import os
import re
from typing import List, Dict, Tuple, Optional

def debug(text):
    print(text)

class DD:
    cluster_key = "blue, bold"
    cluster_title = "bold"
    quest_key = "blue, bold, italic"
    tasks = "yellow, bold"
    opt = "magenta, italic"
    opt_task = "cyan, italic"
    lcmd = "red, bold"
    cmd = "red"
    code_key = "bold"
    skills = "cyan, bold"


    play = "green"
    new = "green, bold"

    nothing = "magenta"
    started = "red"
    required = "yellow"
    complete = "green"

    dots = "yellow" # ...
    shell = "red" # extern shell cmds

    htext = "white"

    check = "green"
    uncheck = "yellow"

    param = "cyan, bold"

class Util:
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
            return colour(DD.complete + "," +  color2, "100%")
        if value >= 70:
            return colour(DD.required + "," +  color2, text)
        if value == 0:
            return colour(DD.nothing + "," +  color2, text)
        return colour(DD.started + "," +  color2, text)

    @staticmethod
    def get_term_size():
        return shutil.get_terminal_size().columns
    
    @staticmethod
    def get_num_num(s: str) -> Tuple[Optional[int], Optional[int]]:
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
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

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
        self.mark_opt = "opt" in self.rep.view
        order = [entry for entry in self.rep.view if entry.startswith("order:")]
        if len(order) > 0:
            self.order = [v for v in order[0][6:].split(",") if v != '']
        else:
            self.order = []

        if not "title" in self.order:
            self.order.append("title")

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
        if self.mark_opt:
            self.rep.view.append("opt")
            
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
        title = title[:-dif - 3] + colour(DD.dots, "...")
        return fn_gen(title)

    def str_task(self, key: str, t: Task, ligc: str, ligq: str, min_value = 1) -> str:
        vindex = colour(DD.tasks, str(key).ljust(2, " "))
        vdone = t.get_grade_symbol(min_value)
        title = t.title

        def gen_saida(_title):
            parts = _title.split(" ")
        
            xp = ""
            if "xp" in self.order:
                for s, v in t.skills.items():
                    xp += f" +{s}:{v}"
                xp = colour(DD.skills, xp)

            if self.mark_opt and t.opt:
                fn = lambda x: colour(DD.opt_task, x)
            else:
                fn = lambda x: x
            parts = [("@" + colour(DD.code_key, p[1:]) if p.startswith("@") else fn(p)) for p in parts]

            titlepainted = " ".join(parts)
            return f" {ligc} {ligq}{vindex}{vdone} {titlepainted}{xp}"
        
        

        return Play.cut_limits(title, gen_saida)

    def str_quest(self, key: str, q: Quest, lig: str) -> str:
        key = colour(DD.quest_key, key.rjust(1))


        con = "━─"
        if q.key in self.expanded:
            con = "─┯"
        new = "" if q.key not in self.new_items else colour(DD.new, " [new]")

        def gen_saida(_title):
            if self.mark_opt and q.opt:
                _title = colour(DD.opt, _title)
            resume = ""
            for item in self.order:
                if item == "cont":
                    resume += " " + q.get_resume_by_tasks()
                elif item == "perc":
                    resume += " " + q.get_resume_by_percent().rjust(4)
                elif item == "goal":
                    resume += " " + q.get_requirement()
                elif item == "title":
                    resume += " " + _title
                elif item == "xp":
                    xp = ""
                    for s,v in q.skills.items():
                        xp += f" +{s}:{v}"
                    xp = colour(DD.skills, xp)
                    resume += " " + xp
            return f" {lig}{con}{key}{resume}{new}"
        
        return Play.cut_limits(q.title.strip(), gen_saida)

    def str_cluster(self, key: str, cluster: Cluster, quests: List[Quest]) -> str:
        opening = "━─"
        resume = ""
        if cluster.key in self.expanded:
            opening = "─┯"
            resume = " " + cluster.get_resume_by_percent()

        # resume = ""
        # for item in self.order:
        #     if item == "cont":
        #         resume += " " + cluster.get_resume_by_quests()
            # if item == "perc":
        key = colour(DD.cluster_key, key)
        title = colour(DD.cluster_title, cluster.title.strip())
        new = "" if cluster.key not in self.new_items else colour(DD.new, " [new]")
        return f"{opening}{key} {title}{resume}{new}"
    
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
                    for t in q.get_tasks():
                        key = Util.calc_letter(task_index)
                        ligc = "│" if q != quests[-1] else " "
                        ligq = "├─" if t != q.get_tasks()[-1] else "╰─"
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
            cmd = colour(DD.shell, f"tko down {self.repo_alias} {task.key} -l {ext}")
            print(f"{cmd}")
            Down.download_problem(rootdir, self.repo_alias, task.key, ext)
        else:
            print(f"Essa não é uma tarefa de código")

    def check_rootdir(self):
        if self.local.rootdir == "":
            print("Diretório raiz para o tko ainda não foi definido")
            print("Você deseja utilizer o diretório atual")
            print("  " + colour(DD.shell, os.getcwd()))
            print("como raiz para o repositório de " + self.repo_alias + "? (s/n) ", end="")
            answer = input()
            if answer == "s":
                self.local.rootdir = os.getcwd()
                self.fnsave()
                print("Você pode alterar o diretório raiz navegando para o diretório desejado e executando o comando")
                print("  " + colour(DD.shell, "tko config --root"))
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
            print("  " + colour(DD.cmd, "ext <Extensão>"))

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

    def process_folds(self, actions) -> bool:
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
                key = colour(DD.tasks, t)
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

    def order_toggle(self, token):
        if token in self.order:
            self.order.remove(token)
        else:
            self.order.append(token)

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
            self.order_toggle("cont")
        elif cmd == "p" or cmd == "perc":
            self.order_toggle("perc")
        elif cmd == "g" or cmd == "goal":
            self.order_toggle("goal")
        elif cmd == "x" or cmd == "xp":
            self.order_toggle("xp")
        elif cmd == "a" or cmd == "admin":
            self.admin_mode = not self.admin_mode
        elif cmd == "t" or cmd == "toolbar":
            self.show_toolbar = not self.show_toolbar
        elif cmd == "o" or cmd == "opt":
            self.mark_opt = not self.mark_opt
        elif cmd == "d" or cmd == "down":
            return self.process_down(actions)
        elif cmd == "l" or cmd == "link":
            return self.process_link(actions)
        elif cmd == "r" or cmd == "rotate":
            if len(self.order) == 1:
                self.order.append("cont")
            self.order = [self.order[-1]] + self.order[:-1]
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
        output = "Digite " + colour(DD.lcmd, "t")
        output += " os números ou intervalo das tarefas para (marcar/desmarcar), exemplo:"
        print(output)
        print(colour(DD.play, "play$ ") + "t 1 3-5")
        return False

    @staticmethod
    def checkbox(value):
        return colour(DD.check, symbols.opcheck) if value else colour(DD.uncheck, symbols.opuncheck)

    def show_header(self):
        Util.clear()
        total_perc = 0
        
        for q in self.game.quests.values():
            total_perc += q.get_percent()
        if self.game.quests:
            total_perc = total_perc // len(self.game.quests)
        
        vrep = colour(DD.htext + ",*", "[")+ colour(DD.tasks, self.repo_alias) + colour(DD.htext + ",*", "]")
        vtotal = colour(DD.htext + ",*", "Total: ") + Util.get_percent(total_perc, "bold", 4)

        intro = vtotal + " " + "│" + colour(DD.htext, " Digite ") + colour(DD.lcmd, "h") + colour(DD.cmd, "elp")
        intro += colour(DD.htext, " ou ") + colour(DD.lcmd, "t") + colour(DD.cmd, "oolbar") 
        intro += Play.checkbox(self.show_toolbar)
        vlink = colour(DD.lcmd, "c") + colour(DD.cmd, "ont") + (Play.checkbox("cont" in self.order))
        vperc = colour(DD.lcmd, "p") + colour(DD.cmd, "erc") + (Play.checkbox("perc" in self.order))
        vgoal = colour(DD.lcmd, "g") + colour(DD.cmd, "oal") + (Play.checkbox("goal" in self.order))
        vxp__ = colour(DD.lcmd, "x") + colour(DD.cmd, "p") + (Play.checkbox("xp" in self.order))
        vopt_ = colour(DD.lcmd, "o") + colour(DD.cmd, "pt") + (Play.checkbox(self.mark_opt))

        vadmi = colour(DD.lcmd, "a") + colour(DD.cmd, "dmin") + (Play.checkbox(self.admin_mode))
        
        vext = colour(DD.lcmd, "e") + colour(DD.cmd, "xt") + "(" + colour(DD.param, self.rep.lang) + ")"
        visoes = f"{vlink} {vperc} {vgoal} {vxp__} {vopt_} {vadmi} "

        # XP        
        obt, total = self.game.get_xp_resume()
        cur_level = XP().get_level(obt)
        xp_next = XP().get_xp(cur_level + 1)
        xp_prev = XP().get_xp(cur_level)
        xpresume = colour(DD.skills, f"{obt}/{total}")
        atual = obt - xp_prev
        needed = xp_next - xp_prev
        nbar = 35
        nbarobt = int((atual * nbar // needed))
        level = colour("bold, green", str(cur_level))
        vxpall = f"{vrep} {vext} {xpresume} Level:{level} "
        vxpall += colour("y", f"{str(atual).rjust(3)}/{str(needed).rjust(3)} ")
        vxpnext = colour("y", "xp:") + "#" * nbarobt + "-" * (nbar - nbarobt)

        def adding_break(base: str, added: str, lim: int):
            last = base.split("\n")[-1]
            if Color.len(last) + Color.len(added) > lim:
                return base + "\n" + added
            return base + added

        skills = self.game.get_skills_resume()
        vskills = ""
        if skills:
            for s, v in skills.items():
                if s != "xp":
                    vskills = adding_break(vskills, f"{colour(DD.skills, s)}:{v} ", nbar)

        div0 = "────────────┴─────────────────────────"

        div1 = "──────────────────────────────────────"

        elementos = [intro]
        if self.show_toolbar:
            elementos += [div0, visoes, div1, vxpall, vxpnext]
            if vskills:
                elementos += [vskills]
        elementos += [div1]


        # elementos = [intro] + ([div0, visoes, div1, vxpall, vxpnext, vskills] if self.show_toolbar else []) + [div1]
        self.print_elementos(elementos)

    def show_cmds(self):
        controles = colour(DD.htext, "Números ") + colour(DD.cluster_key, "azul") + colour(DD.htext, " para expandir/colapsar")
        letrass = colour(DD.htext, "Letras ") + colour(DD.tasks, "amarelo") + colour(DD.htext, " para marcar/desmarcar")
        intervalos1 = colour(DD.htext, "Você pode digitar intervalos: ") + colour(DD.cluster_key, "1-3")
        intervalos2 = colour(DD.htext, "Você pode digitar intervalos: ") + colour(DD.cluster_key, "B-F")

        numeros = "─┯" + colour(DD.cluster_key, "3") + "  Digite " + colour(DD.cluster_key, "3") + (" para ver ou ocultar")
        
        letras = " ├─" + colour(DD.tasks, "D ") + colour(DD.nothing, symbols.uncheck)
        letras += " Tarefa. Dig " + colour(DD.cluster_key, "D") + " (des)marcar"
        
        graduar = " ╰─" + colour(DD.tasks, "X ") + colour(DD.started, "4")  + " Tarefa. Dig " + colour(DD.cluster_key, "X4") + " dar nota 4"
        todas = colour(DD.cluster_key, "<") + " ou " + colour(DD.cluster_key, ">") + colour(DD.htext, " (Compactar ou Descompactar Tudo)")
        
        nomes_verm = colour(DD.htext, "Os nomes em vermelho são comandos")
        prime_letr = colour(DD.htext, "Basta a primeira letra do comando")
        vdown = colour(DD.lcmd, "d") + colour(DD.cmd, "own") + colour(DD.param, " <TaskID ...>") + colour(DD.htext, " (Download)")
        vlink = colour(DD.lcmd, "l") + colour(DD.cmd, "ink") + colour(DD.param, " <TaskID ...>") + colour(DD.htext, " (Ver links)")
        vexte = colour(DD.lcmd, "e") + colour(DD.cmd, "xt") + colour(DD.param, "  <EXT>") + colour(DD.htext, " (Mudar linguagem default)")
        vsair = colour(DD.lcmd, "q") + colour(DD.cmd, "uit") + colour(DD.htext, " (Sair do programa)")
        vcont = colour(DD.lcmd, "c") + colour(DD.cmd, "ont") + colour(DD.htext, " (Alterna contador de tarefas)")
        vperc = colour(DD.lcmd, "p") + colour(DD.cmd, "erc") + colour(DD.htext, " (Alterna mostrar porcentagem)")
        vgoal = colour(DD.lcmd, "g") + colour(DD.cmd, "oal") + colour(DD.htext, " (Alterna mostrar meta mínima)")
        vopt_ = colour(DD.lcmd, "o") + colour(DD.cmd, "pt") + colour(DD.htext, " (Alterna ressaltar opcionais)")
        vupda = colour(DD.lcmd, "u") + colour(DD.cmd, "pdate") + colour(DD.htext, " (Recarrega o repositório)")
        vrota = colour(DD.lcmd, "r") + colour(DD.cmd, "otate") + colour(DD.htext, " (Rotaciona elementos visuais)")
        vgame = colour(DD.lcmd, "a") + colour(DD.cmd, "dmin") + colour(DD.htext, " (Libera todas as missões)")

        div0 = "──────────────────────────────────────"
        div1 = "───────────── " + colour(DD.cluster_key, "Controles") + "──────────────"
        div2 = "───────────────── " + colour(DD.lcmd, "Flags") + " ──────────────"
        div3 = "───────────── " + colour(DD.lcmd, "Comandos") + " ───────────────"

        elementos = []
        elementos += [div1, controles, letrass, todas, numeros, letras, graduar, intervalos1, intervalos2]
        elementos += [div2, nomes_verm, prime_letr, vcont, vperc, vgoal, vgame, div3, vdown, vlink, vexte, vupda, vrota, vsair]

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
            done = len([t for t in q.get_tasks() if t.is_complete()])
            init = len([t for t in q.get_tasks() if t.in_progress()])
            todo = len([t for t in q.get_tasks() if t.not_started()])
            counts[q.key] = f"{done} / {done + init + todo}\n{q.get_percent()}%"

        Graph(self.game).set_opt(self.mark_opt).set_reachable(reachable).set_counts(counts).set_graph_ext(graph_ext).generate()

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

            print("\n" + colour(DD.play, "play$") + " ", end="")
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
