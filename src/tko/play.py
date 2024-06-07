from typing import Dict, List, Tuple
from .game import Game, Task, Quest
from .settings import RepoSettings
from .remote import RemoteCfg
from .down import Down
from .format import GSym, colour, colour_bold, red, green, yellow, cyan, Color
import subprocess
import shutil
import tempfile
import os
import re


class Play:
    cluster_prefix = "'"

    def __init__(self, game: Game, rep: RepoSettings, repo_alias: str, fnsave):
        self.fnsave = fnsave
        self.repo_alias = repo_alias
        self.help_options = 0
        self.help_index = 0
        self.rep = rep
        self.show_link = "link" in self.rep.view
        self.show_done = "done" in self.rep.view
        self.show_init = "init" in self.rep.view
        self.show_todo = "todo" in self.rep.view

        help = [v for v in self.rep.view if v.startswith("help_")]
        if len(help) > 0:
            self.help_index = int(help[0][5:])
            if self.help_index >= self.help_options:
                self.help_index = 0
        else:
            self.help_index = 0

        self.show_perc = "perc" in self.rep.view
        self.show_fold = not "unfold" in self.rep.view
        self.show_hack = "hack" in self.rep.view
        self.show_view = "view" in self.rep.view

        if not self.show_done and not self.show_init and not self.show_todo:
            self.show_done = True
            self.show_init = True
            self.show_todo = True

        self.game: Game = game

        self.clusters: Dict[str, str] = self.find_cluster_keys()
        self.clusters_keys = {}
        for k, v in self.clusters.items():
            self.clusters_keys[v] = k
        self.tasks: Dict[str, Task] = {}  # visible tasks  indexed by upper letter
        self.quests: Dict[str, Quest] = {}  # visible quests indexed by number
        self.active: List[str] = []  # expanded quests

        for k, v in self.rep.quests.items():
            if "e" in v:
                self.active.append(k)

        self.term_limit = 130

        for key, grade in rep.tasks.items():
            if key in game.tasks:
                game.tasks[key].set_grade(grade)

    def control(self, text):
        return colour_bold("blue", text)

    def read_link(self, link):
        if link.endswith(".md"):
            if link.startswith("https"):
                with tempfile.NamedTemporaryFile(delete=False) as f:
                    file = f.name
                    cfg = RemoteCfg()
                    cfg.from_url(link)
                    cfg.download_absolute(file)
                    link = file
                    # verify is subprocess succeeds
            result = subprocess.run(["glow", "-p", link])
            if result.returncode != 0:
                print(f"Erro ao abrir o arquivo {link}")
                print("Verifique se o arquivo está no formato markdown")
                input("Digite enter para continuar")

    def down_task(self, task: Task):
        if task.key in task.title:
            print(f"Tarefa de código {task.key}")
            cmd = red(f"tko down {self.repo_alias} {task.key}")
            print(f"Baixando com o comando {cmd}")
            result = Down.download_problem(self.repo_alias, task.key, None)
            # result = subprocess.run(["tko", "down", self.repo_alias, task.key])
            if result:
                pasta = red(f"{os.getcwd()}/{task.key}/Readme.md")
                print(f"Tarefa baixada na pasta {pasta}")
        else:
            print(f"Essa não é uma tarefa de código")
        input("Digite enter para continuar")

    def save_to_json(self):
        self.rep.quests = {}
        for q in self.active:
            self.rep.quests[q] = "e"
        self.rep.tasks = {}
        for t in self.game.tasks.values():
            if t.grade != "":
                self.rep.tasks[t.key] = t.grade
        self.rep.view = []
        if self.show_link:
            self.rep.view.append("link")
        if self.show_perc:
            self.rep.view.append("perc")
        if not self.show_fold:
            self.rep.view.append("unfold")
        if self.show_hack:
            self.rep.view.append("hack")
        if self.show_view:
            self.rep.view.append("view")
        if self.show_done:
            self.rep.view.append("done")
        if self.show_init:
            self.rep.view.append("init")
        if self.show_todo:
            self.rep.view.append("todo")

        self.rep.view.append(f"help_{self.help_index}")

        self.fnsave()

    @staticmethod
    def calc_letter(index_letter):
        unit = index_letter % 26
        ten = index_letter // 26
        if ten == 0:
            return chr(ord("A") + unit)
        return chr(ord("A") + ten - 1) + chr(ord("A") + unit)

    @staticmethod
    def calc_index(letter):
        letter = letter.upper()
        if len(letter) == 1:
            return ord(letter) - ord("A")
        return (ord(letter[0]) - ord("A") + 1) * 26 + (ord(letter[1]) - ord("A"))

    def update_reachable(self):
        quests = []
        if self.show_hack:
            quests = self.game.quests.values()
        else:
            quests = self.game.get_reachable_quests()

        reach_keys = []
        reach_keys = [q.key for q in quests]
        menu_keys = [q.key for q in self.quests.values()]

        for key in menu_keys:
            if key not in reach_keys:
                self.quests = {}
                break

        if len(self.quests) == 0:
            index = 0
            for q in quests:
                self.quests[str(index)] = q
                index += 1
        else:
            index = len(self.quests.keys())
            for q in quests:
                if q.key not in menu_keys:
                    self.quests[str(index)] = q
                    index += 1

        # self.active = set([k for k in self.active if k in reach_keys])

        # if len(self.quests.values()) == 1:
        #     for q in self.quests.values():
        #         self.active.add(q.key)

    def calculate_pad(self):
        titles = []
        keys = self.quests.keys()
        for key in keys:
            q = self.quests[key]
            titles.append(q.title)
            if q.key not in self.active:
                continue
            for t in q.tasks:
                titles.append(t.title)
        max_title = 10
        if len(titles) > 0:
            max_title = max([len(t) for t in titles])
        return max_title

    def to_show_quest(self, quest: Quest):
        if quest.is_complete() and not self.show_done:
            return False
        if quest.not_started() and not self.show_todo:
            return False
        if quest.in_progress() and not self.show_init:
            return False
        return True

    def get_number(self, value):
        if value >= 0 and value <= 20:
            return GSym.numbers[value]
        return "*"

    def str_quest(self, entry: str, q: Quest, max_title) -> str:
        term_size = self.get_term_size()
        resume = ""
        opening = GSym.right
        if q.key in self.active:
            opening = GSym.down
        done = self.get_number(len([t for t in q.tasks if t.is_complete()]))
        init = self.get_number(len([t for t in q.tasks if t.in_progress()]))
        todo = self.get_number(len([t for t in q.tasks if t.not_started()]))
 
        if self.show_perc:
            text = f"{str(q.get_percent()).rjust(2)}%"
            if q.get_percent() == 100:
                text = GSym.check * 3
            if q.get_percent() == 100:
                resume = cyan(text)
            elif q.is_complete():
                resume = green(text)
            elif q.in_progress():
                resume = yellow(text)
            else:
                resume = red(text)
        else:
            resume = f"{green(done)}{yellow(init)}{red(todo)}"
        space = " " if len(entry) == 1 else ""
        entry = self.control(entry)
        qlink = ""
        if self.show_link:
            if term_size > self.term_limit:
                qlink = " " + colour("c", q.mdlink)
            else:
                qlink = "\n      " + colour("c", q.mdlink)
        if not self.to_show_quest(q):
            return ""
        title = q.title
        if self.show_link and term_size > self.term_limit:
            title = title.strip().ljust(max_title + 1)
        title = title.strip()
        return f"{resume} {opening} {space}{entry} {title}"

    def str_task(self, t: Task, max_title: int, letter: str, lig: str) -> str:
        term_size = self.get_term_size()
        vindex = self.control(str(letter).rjust(2, " "))
        vdone = t.get_grade()
        vlink = ""
        title = t.title
        if self.show_link:
            if t.key in t.title:
                vlink = red(t.link)
            else:
                vlink = yellow(t.link)
            if term_size > self.term_limit:
                title = t.title.strip().ljust(max_title + 1)
                vlink = " " + vlink
            else:
                vlink = "\n" + vlink
#        title = colour("uline", title) 

        def gen_saida():
            return f"    {vdone}  {lig}{vindex} {title}{vlink}"
        
        saida = gen_saida()

        clear_total = Color.len(saida)
        dif = clear_total - term_size
        if (dif < 0):
            return saida 
        title = title[:-dif - 3] + "..."

        return gen_saida()

    def sort_keys(self, keys):
        single = [k for k in keys if len(str(k)) == 1]
        double = [k for k in keys if len(str(k)) == 2]
        return sorted(single) + sorted(double)

    def print_cluster(self, cluster_name: str, line_types: List[Tuple[str, str]]):
        cluster_key = self.clusters_keys[cluster_name]
        opening = GSym.right
        if cluster_name in self.active:
            opening = GSym.down
        intro = [key for _, key in line_types]
        quests = [k for k in intro if k in self.quests]
        total = len(quests)
        init = yellow(self.get_number(len([v for v in quests if self.quests[v].in_progress()])))
        done = green(self.get_number(len([v for v in quests if self.quests[v].is_complete()])))
        todo = red(self.get_number(len([v for v in quests if self.quests[v].not_started()])))
        margin = len(cluster_key)
        title = self.control(cluster_name.strip()[:margin]) + colour("bold", cluster_name.strip()[margin:])
        opening = yellow(opening)
        if total > 0:
            print(f"{done}{init}{todo} {opening} {title}")
            if cluster_name in self.active:
                for line, t in line_types:
                    print(line)

    def find_cluster_keys(self) -> Dict[str, str]:
        data = sorted(self.game.cluster_order)
        keys = []
        for cluster in data:
            i = 2
            while (True):
                key = cluster[:i]
                if key not in keys:
                    keys.append(key)
                    break
                i += 1
        output = {}
        for k, v in zip(keys, data):
            output[k] = v
        return output

    def get_term_size(self):
        return shutil.get_terminal_size().columns

    def show_options(self):
        max_title = self.calculate_pad()
        index = 0

        clusters: Dict[str, List[Tuple[str, str]]] = {}

        for entry in self.sort_keys(self.quests.keys()):
            quest_output: List[Tuple[str, str]] = []
            q = self.quests[entry]
            quest_output.append((self.str_quest(entry, q, max_title), entry))
            if q.key in self.active and self.to_show_quest(q):
                for i, t in enumerate(q.tasks):
                    letter = self.calc_letter(index)
                    lig = "├─" if i < len(q.tasks) - 1 else "╰─"
                    quest_output.append((self.str_task(t, max_title, letter, lig), t.key))
                    index += 1
                    self.tasks[letter] = t

            if self.show_fold:
                if len(quest_output) > 0:
                    if q.group not in clusters:
                        clusters[q.group] = []
                    clusters[q.group] += [entry for entry in quest_output if entry[0] != ""]
            else:
                for line, _ in quest_output:
                    if line != "":
                        print(line)

        if self.show_fold:
            for group in self.game.cluster_order:
                if group in clusters.keys():
                    self.print_cluster(group, clusters[group])
        return

    @staticmethod
    def get_num_num(s):
        pattern = r"^(\d+)-(\d+)$"
        match = re.match(pattern, s)
        if match:
            return int(match.group(1)), int(match.group(2))
        else:
            return (None, None)

    @staticmethod
    def get_letter_letter(s):
        pattern = r"([a-zA-Z]+)-([a-zA-Z]+)"
        match = re.match(pattern, s)
        if match:
            print(match.group(1), match.group(2))
            return match.group(1), match.group(2)
        return (None, None)

    def expand_range(self, line) -> List[str]:
        line = line.replace(" - ", "-")
        actions = line.split()

        expand = []
        for t in actions:
            (start_number, end_number) = self.get_num_num(t)
            (start_letter, end_letter) = self.get_letter_letter(t)
            if start_number is not None and end_number is not None:
                expand += list(range(start_number, end_number + 1))
            elif start_letter is not None and end_letter is not None:
                start_index = self.calc_index(start_letter)
                end_index = self.calc_index(end_letter)
                print(start_index, end_index)
                limits = range(start_index, end_index + 1)
                expand += [self.calc_letter(i) for i in limits]
            else:
                expand.append(t)
        return expand

    def clear(self):
        subprocess.run("clear")
        pass

    def is_number(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def process_colapse(self):
        all_tasks_closed = True
        for v in self.active:
            if v not in self.clusters.values():
                all_tasks_closed = False
                break
        if all_tasks_closed:
            self.active = []
        else:
            self.active = [q for q in self.active if q in self.clusters.values()]

    def process_expand(self):
        self.update_reachable()
        # verify if all clusters are expanded
        all_clusters_expanded = True
        for k in self.clusters.values():
            if k not in self.active:
                all_clusters_expanded = False
                break
        clusters = [k for k in self.clusters.values()]
        if all_clusters_expanded:
            quests = [q.key for q in self.quests.values()]
            self.active = quests + clusters
        else:
            self.active = self.active + clusters

    def process_down(self, actions):
        for t in actions[1:]:
            if t in self.tasks:
                self.down_task(self.tasks[t])
            else:
                print(f"Tarefa {t} não encontrada")
                input()

    def process_clusters(self, actions):
        for t in actions:
            if t in self.clusters:
                key = self.clusters[t]
                if key not in self.active:
                    print(f"Expandindo {key}")
                    self.active.append(key)
                else:
                    print(f"Contraindo {key}")
                    self.active.remove(key)
                    for q in self.quests.values():
                        if q.group == key:
                            if q.key in self.active:
                                self.active.remove(q.key)
            else:
                print(f"Tópico {t} não processado")
                input("Digite enter para continuar")

    def process_quests(self, actions):
        for t in actions:
            if not self.is_number(t):
                print(f"Missão '{t}' não é um número")
                input("Digite enter para continuar")
                return
            if not str(t) in self.quests:
                print(self.quests.keys())
                print(f"Missão '{t}' não existe")
                input("Digite enter para continuar")
                return
            key = self.quests[str(t)].key
            if key not in self.active:
                self.active.append(key)
                continue
            else:
                self.active.remove(key)
                continue
    
    def process_tasks(self, actions):
        for t in actions:
            letter = "".join([c for c in t if c.isupper() and not c.isdigit()])
            number = "".join([c for c in t if c.isdigit()])
            if letter in self.tasks:
                t = self.tasks[letter]
                if len(number) > 0:
                    t.set_grade(number)
                else:
                    if t.grade == "":
                        t.set_grade("x")
                    else:
                        t.set_grade("")
            else:
                print(f"Talk {t} não processado")
                input("Digite enter para continuar")
    
    def process_see(self, actions):
        if len(actions) > 1:
            if actions[1] in self.tasks:
                # print(self.tasks[actions[1]].link)
                self.read_link(self.tasks[actions[1]].link)
            else:
                print(f"{actions[1]} não processado")
                input("Digite enter para continuar")

    def take_actions(self, actions):
        if len(actions) == 0:
            return
        cmd = actions[0]

        if cmd == "<":
            self.process_colapse()

        elif cmd == ">":
            self.process_expand()

        elif cmd == "m" or cmd == "man":
            self.clear()
            self.show_help()
        elif cmd == "c" or cmd == "cmd":
            self.help_index = (self.help_index + 1) % self.help_options
        # elif cmd == "f" or cmd == "full":
        #     self.show_done = True
        #     self.show_init = True
        #     self.show_todo = True
        # elif cmd == "i" or cmd == "init":
        #     self.show_done = False
        #     self.show_init = True
        #     self.show_todo = False
        # elif cmd == "d" or cmd == "done":
        #     self.show_done = True
        #     self.show_init = False
        #     self.show_todo = False
        # elif cmd == "t" or cmd == "todo":
        #     self.show_done = False
        #     self.show_init = False
        #     self.show_todo = True
        elif cmd == "l" or cmd == "link":
            self.show_link = not self.show_link
        elif cmd == "p" or cmd == "perc":
            self.show_perc = not self.show_perc
        # elif cmd == "j" or cmd == "join":
        #     self.show_fold = not self.show_fold
        elif cmd == "h" or cmd == "hack":
            self.show_hack = not self.show_hack
        elif cmd == "t" or cmd == "toolbar":
            self.show_view = not self.show_view
        elif cmd == "d" or cmd == "down":
            self.process_down(actions)
        elif len(str(cmd)) >= 2 and cmd[0].isupper() and cmd[1].islower():
            self.process_clusters(actions)
        elif self.is_number(cmd):
            self.process_quests(actions)
        elif cmd[0].isupper():
            self.process_tasks(actions)
        elif cmd == "s" or cmd == "see":
            self.process_see(actions)
        else:
            print(f"{cmd} não processado")
            input("Digite enter para continuar")

    def show_help(self):
        print(
            "Digite "
            + red("t")
            + " os números ou intervalo das tarefas para (marcar/desmarcar), exemplo:"
        )
        print(green("play $ ") + "t 1 3-5")
        input("Digite enter para continuar")

    def show_header(self):
        self.clear()
        ball = self.show_done and self.show_init and self.show_todo
        show_ajuda = green("Digite ") + red("c") + green(" para ajuda")

        full_count = len([q for q in self.quests.values()])
        done_count = len([q for q in self.quests.values() if q.is_complete()])
        init_count = len([q for q in self.quests.values() if q.in_progress()])
        todo_count = len([q for q in self.quests.values() if q.not_started()])

        def checkbox(value):
            return green(GSym.vcheck) if value else yellow(GSym.vuncheck)

        # vall = red("full") + (green(GSym.vcheck) if ball else yellow(GSym.vuncheck))
        # vdone = "(" + str(done_count).rjust(2, "0") + ")" + red("done") + checkbox(not ball and self.show_done)
        # vinit = "(" + str(init_count).rjust(2, "0") + ")" + red("init") + checkbox(not ball and self.show_init)
        # vtodo = "(" + str(todo_count).rjust(2, "0") + ")" + red("todo") + checkbox(not ball and self.show_todo)
        vlink = red("link") + ( checkbox(self.show_link) )
        vperc = red("perc") + ( checkbox(self.show_perc) )
        # vjoin = red("join") + ( checkbox(self.show_fold) )
        vhack = red("hack") + ( checkbox(self.show_hack) )
        vgame = red("game") + ( checkbox(False) )

        controles = green("Elementos em ") + self.control("azul") + green(" são controles")
        feitos = colour_bold("g", "1") + colour_bold("y", "2") + colour_bold("r", "3") + green(" Feitos") + "/" + yellow("Iniciados") + "/" + red("Não Iniciados")
        cluster = GSym.right + self.control(" Gr") + green("upo. Digite ") + self.control("Gr") + green(" para ver ou ocultar")
        numeros = GSym.right + self.control("  3") + green(" Missão. Dig ") + self.control("3") + green(" para ver ou ocultar")
        letras = colour("g", GSym.check) + self.control("  D") + green(" Tarefa. Dig ") + self.control("D") + green(" (des)marcar")
        graduar = colour("r", "4") + self.control("  X") + green(" Tarefa. Dig ") + self.control("X4") + green(" dar nota 4")
        todas = self.control("<") + " ou " + self.control(">") + yellow(" (Compactar ou Descompactar Tudo)")
        
        
        
        nomes_verm = green("Os nomes em vermelho são comandos")
        prime_letr = green("Basta a primeira letra do comando")
        read = red("see <LETRA>") + cyan(" {s B}") + yellow(" (Ler no terminal)")
        down = red("down <LETRA>") + cyan(" {d B}") + yellow(" (Baixar tarefa)")
        cmds = red("cmd") + yellow("  (Visualizar os comandos)")
        manu = red("man") + yellow("  (Mostrar manual detalhado)")
        sair = red("quit") + yellow(" (Sair do programa)")

        # sall  = red("full") + yellow(" (Mostrar todas as tarefas)")
        # sdone = red("done") + yellow(" (Mostrar tarefas concluídas)")
        # sinit = red("init") + yellow(" (Mostrar tarefas em andamento)")
        # stodo = red("todo") + yellow(" (Mostrar tarefas não iniciadas)")
        # fold  = red("join") + yellow(" (Juntar em categorias)")
        link  = red("link")    + yellow(" (Mostrar links das tarefas)")
        hack  = red("hack")    + yellow(" (Dá acesso a todas as tarefas)")
        perc  = red("perc") + yellow(" (Mostrar porcentagens)")
        exp  =  red("xp")      + yellow(" (Mostrar experiência)")


        #indicadores = f"{vall} {vdone} {vinit} {vtodo}"
        visoes = f"{vlink}  {vperc}  {vhack}  {vgame}"
        div0 = "──────────────────────────────────────"
        div1 = "───────────────── 1 ──────────────────"
        div2 = "───────────────── 2 ──────────────────"
        elementos = []
        vbar = red(" toolbar") + checkbox(self.show_view)
        if self.help_index == 0:
            intro = show_ajuda + " (1/2)" + vbar
            elementos = [ intro ] + ([ div0, visoes ] if self.show_view else [])
        elif self.help_index == 1:
            intro = show_ajuda + " (" + yellow("1") + "/2)" + vbar
            elementos = [ intro ] + ([ div0, visoes ] if self.show_view else [])
            elementos += [ div1, controles, feitos, todas, cluster, numeros, letras, graduar ]
        elif self.help_index == 2:
            intro = show_ajuda + " (1/" + yellow("2") + ")" + vbar
            elementos = [ intro ] + ([ div0, visoes ] if self.show_view else [])
            elementos += [ div2, nomes_verm, prime_letr, cmds, manu, down, read, perc, link, hack, sair ]
        # elif self.help_index == 3:
        #     intro = show_ajuda + " (1/2/" + yellow("3") + ")" + green(" - ") + red("view") + checkbox(self.show_view)
        #     elementos = [ intro ] + ([ div0, indicadores, visoes ] if self.show_view else [])
        #     elementos += [ div3, nomes_verm, prime_letr, sall, sdone, sinit, stodo, fold,  ]
        self.help_options = 3
        self.print_elementos(elementos)
        print(div0)

    def print_elementos(self, elementos):
        term_size = shutil.get_terminal_size().columns
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
        while True:
            self.tasks = {}
            self.update_reachable()
            self.show_header()
            self.show_options()
            print("\n" + green("play$") + " ", end="")
            line = input()
            if line != "" and "quit".startswith(line):
                break
            actions = self.expand_range(line)
            self.take_actions(actions)
            self.save_to_json()
