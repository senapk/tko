from .game import Game, Task, Quest, Cluster, Graph, XP, Sentence
from .settings import RepoSettings, LocalSettings
from .down import Down
import shutil
import os
import re
from typing import List, Dict, Tuple, Optional, Any

def debug(text):
    print(text)

import curses
from typing import List, Tuple



class Fmt:
    # Definindo constantes para as cores
    CM = {
        "r": 1, # Red on White
        "g": 2, # Green on White
        "y": 3, # Yellow on White
        "b": 4, # Blue on White
        "m": 5,
        "c": 6,
        "w": 7,
        "k": 8,
    }

    @staticmethod
    def init_colors():
        # Inicializa as cores e define os pares de cores
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(Fmt.CM["r"], curses.COLOR_RED    , -1)
        curses.init_pair(Fmt.CM["g"], curses.COLOR_GREEN  , -1)
        curses.init_pair(Fmt.CM["y"], curses.COLOR_YELLOW , -1)
        curses.init_pair(Fmt.CM["b"], curses.COLOR_BLUE   , -1)
        curses.init_pair(Fmt.CM["m"], curses.COLOR_MAGENTA, -1)
        curses.init_pair(Fmt.CM["c"], curses.COLOR_CYAN   , -1)
        curses.init_pair(Fmt.CM["w"], curses.COLOR_WHITE  , -1)
        curses.init_pair(Fmt.CM["k"], curses.COLOR_BLACK  , -1)


    @staticmethod
    def write_line(stdscr, x: int, y: int, text: str, fmt: str):
        bold = False
        italic = False
        underline = False
        if "*" in fmt:
            bold = True
            fmt = fmt.replace("*", "")
        if "/" in fmt:
            italic = True
            fmt = fmt.replace("/", "")
        if "_" in fmt:
            underline = True
            fmt = fmt.replace("_", "")
        color = -1
        try:
            color = Fmt.CM[fmt]
        except KeyError:
            color = -1
        if bold:
            stdscr.attron(curses.A_BOLD)
        if italic:
            stdscr.attron(curses.A_ITALIC)
        if underline:
            stdscr.attron(curses.A_UNDERLINE)
        if color != -1:
            stdscr.attron(curses.color_pair(color))  # Ativa o par de cores especificado
        stdscr.addstr(y, x, text)
        if color != -1:
            stdscr.attroff(curses.color_pair(color))  # Desativa o par de cores
        if bold:
            stdscr.attroff(curses.A_BOLD)
        if italic:
            stdscr.attroff(curses.A_ITALIC)
        if underline:
            stdscr.attroff(curses.A_UNDERLINE)

    @staticmethod
    def write(stdscr, x: int, y: int, sentence: Sentence):
        # Escreve um texto na tela com cores diferentes
        lines, cols = stdscr.getmaxyx()
        x_ini = x
        for fmt, text in sentence.get():
            if x < cols and y < lines:
                if x + len(text) >= cols:
                    text = text[:cols - x]
                Fmt.write_line(stdscr, x, y, text, fmt)
            x += len(text)  # Move a posição x para a direita após o texto

    @staticmethod
    def get_user_input(stdscr, prompt: str) -> str:
        curses.echo()  # Ativa a exibição dos caracteres digitados
        stdscr.addstr(curses.LINES - 1, 0, prompt)
        stdscr.refresh()
        input_str = stdscr.getstr(curses.LINES - 1, len(prompt), 20).decode('utf-8')  # Captura o input do usuário
        curses.noecho()  # Desativa a exibição dos caracteres digitados
        return input_str


class DD:
    cluster_key = "*b"
    cluster_title = "*"
    quest_key = "/*b"
    tasks = "*y"
    opt = "/m"
    opt_task = "/c"
    lcmd = "*r"
    cmd = "r"
    code_key = "*"
    skills = "c*"


    play = "g"
    new = "*g"

    nothing = "m"
    started = "r"
    required = "y"
    complete = "g"

    dots = "y" # ...
    shell = "r" # extern shell cmds

    htext = "w"

    check = "g"
    uncheck = "y"

    param = "c"

class Util:
    @staticmethod
    def get_number(value: int):
        if 0 <= value <= 9:
            return str(value)
        return "*"
    
    @staticmethod
    def get_term_size():
        return curses.COLS

    @staticmethod
    def get_percent(value, color2: str = "", pad = 0) -> Sentence:
        text = f"{str(value)}%".rjust(pad)
        if value == 100:
            return Sentence().addf(DD.complete +  color2, "100%")
        if value >= 70:
            return Sentence().addf(DD.required +  color2, text)
        if value == 0:
            return Sentence().addf(DD.nothing +  color2, text)
        return Sentence().addf(DD.started +  color2, text)
    
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
   
class Entry:
    def __init__(self, obj: Any, sentence: Sentence):
        self.obj = obj
        self.sentence = sentence

    def get(self):
        return self.sentence
    
class Play:
    cluster_prefix = "'"

    def __init__(self, local: LocalSettings, game: Game, rep: RepoSettings, repo_alias: str, fnsave):
        self.fnsave = fnsave
        self.local = local
        self.repo_alias = repo_alias

        self.rep = rep
        self.show_toolbar = "toolbar" in self.rep.view
        self.admin_mode = "admin" in self.rep.view
        self.mark_opt = "opt" in self.rep.view
        order = [entry for entry in self.rep.view if entry.startswith("order:")]
        if len(order) > 0:
            self.order = [v for v in order[0][6:].split(",") if v != '']
        else:
            self.order = []

        self.game: Game = game
        self.expanded: List[str] = [x for x in self.rep.expanded]
        self.new_items: List[str] = [x for x in self.rep.new_items]
        self.avaliable_quests: List[Quest] = [] # avaliable quests
        self.avaliable_clusters: List[Cluster] = [] # avaliable clusters

        self.index = 0
        self.y_begin = 1
        self.y_end = 1
        self.items: List[Entry] = []

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

    def str_task(self, in_focus: bool, t: Task, ligc: str, ligq: str, min_value = 1) -> Sentence:
        output = Sentence()
        output.addt(" " + ligc + " " + ligq)\
              .concat(t.get_grade_symbol(min_value))\
              .addt(" ")

        focus = ""
        if in_focus:
            focus = "_"
        if self.mark_opt and t.opt:
            output.addf(DD.opt_task + focus, t.title)
        else:
            output.addf("" + focus, t.title)
        
        if "xp" in self.order:
            xp = ""
            for s, v in t.skills.items():
                xp += f" +{s}:{v}"
            output.addf(DD.skills, xp)
        return output
    
    def str_quest(self, in_focus: bool, q: Quest, lig: str) -> Sentence:
        con = "━─" if q.key not in self.expanded else "─┯"
        output: Sentence = Sentence().addt(" " + lig + con + " ")

        opt = "" if not q.opt else DD.opt
        focus = "" if not in_focus else "_"
        output.addf(opt + focus, q.title)

        for item in self.order:
            if item == "cont":
                output.addt(" ").concat(q.get_resume_by_tasks())
            elif item == "perc":
                output.addt(" ").concat(q.get_resume_by_percent())
            elif item == "goal":
                output.addt(" ").concat(q.get_requirement())
            elif item == "xp":
                xp = ""
                for s,v in q.skills.items():
                    xp += f" +{s}:{v}"
                output.addf((DD.skills, " " + xp))
                
        if q.key in self.new_items:
            output.addf(DD.new, " [new]")

        return output
        

    def str_cluster(self, in_focus: bool, cluster: Cluster, quests: List[Quest]) -> Sentence:
        output: Sentence = Sentence()
        opening = "━─"        
        if cluster.key in self.expanded:
            opening = "─┯"        
        output.addt(opening + " ")
        focus = ""
        if in_focus:
            focus = "_"
        output.addf(DD.cluster_title + focus, cluster.title.strip())
        output.addt(" ").concat(cluster.get_resume_by_percent())
        if cluster.key in self.new_items:
            output.addf(DD.new, " [new]")

        return output
    
    def get_avaliable_quests_from_cluster(self, cluster: Cluster) -> List[Quest]:
        return [q for q in cluster.quests if q in self.avaliable_quests]

    def load_options(self):
        index = 0
        self.items = []
        for cluster in self.avaliable_clusters:
            quests = self.get_avaliable_quests_from_cluster(cluster)
            sentence = self.str_cluster(self.index == index, cluster, quests)
            self.items.append(Entry(cluster, sentence))
            index += 1

            if not cluster.key in self.expanded: # va para proximo cluster
                continue

            for q in quests:
                lig = "├" if q != quests[-1] else "╰"
                sentence = self.str_quest(self.index == index, q, lig)
                self.items.append(Entry(q, sentence))
                index += 1
                if q.key in self.expanded:
                    for t in q.get_tasks():
                        ligc = "│" if q != quests[-1] else " "
                        ligq = "├ " if t != q.get_tasks()[-1] else "╰ "
                        sentence = self.str_task(self.index == index, t, ligc, ligq, q.tmin)
                        self.items.append(Entry(t, sentence))
                        index += 1


    def down_task(self, rootdir, task: Task, ext: str):
        if task.key in task.title:
            cmd = (DD.shell, f"tko down {self.repo_alias} {task.key} -l {ext}")
            print(f"{cmd}")
            Down.download_problem(rootdir, self.repo_alias, task.key, ext)
        else:
            print(f"Essa não é uma tarefa de código")

    def check_rootdir(self):
        if self.local.rootdir == "":
            print("Diretório raiz para o tko ainda não foi definido")
            print("Você deseja utilizer o diretório atual")
            print((DD.shell, "  " + os.getcwd()))
            print("como raiz para o repositório de " + self.repo_alias + "? (s/n) ", end="")
            answer = input()
            if answer == "s":
                self.local.rootdir = os.getcwd()
                self.fnsave()
                print("Você pode alterar o diretório raiz navegando para o diretório desejado e executando o comando")
                print((DD.shell, "  tko config --root"))
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
            print((DD.cmd, "  ext <Extensão>"))

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
    
    def process_link(self, actions):
        if len(actions) == 1:
            print("Após o comando passe a letra da tarefa para ver o link")
            return False
        for t in actions[1:]:
            if t in self.vtasks:
                # print(self.tasks[actions[1]].link)
                key = (DD.tasks, t)
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

    # @staticmethod
    # def checkbox(value):
    #     return colour(DD.check, symbols.opcheck) if value else colour(DD.uncheck, symbols.opuncheck)

    def show_header(self):
        Util.clear()
        # total_perc = 0
        
        # for q in self.game.quests.values():
        #     total_perc += q.get_percent()
        # if self.game.quests:
        #     total_perc = total_perc // len(self.game.quests)
        
        # vrep = colour(DD.htext + ",*", "[")+ colour(DD.tasks, self.repo_alias) + colour(DD.htext + ",*", "]")
        # vtotal = colour(DD.htext + ",*", "Total: ") #+ Util.get_percent(total_perc, "bold", 4)

        # intro = vtotal + " " + "│" + colour(DD.htext, " Digite ") + colour(DD.lcmd, "h") + colour(DD.cmd, "elp")
        # intro += colour(DD.htext, " ou ") + colour(DD.lcmd, "t") + colour(DD.cmd, "oolbar") 
        # intro += Play.checkbox(self.show_toolbar)
        # vlink = colour(DD.lcmd, "c") + colour(DD.cmd, "ont") + (Play.checkbox("cont" in self.order))
        # vperc = colour(DD.lcmd, "p") + colour(DD.cmd, "erc") + (Play.checkbox("perc" in self.order))
        # vgoal = colour(DD.lcmd, "g") + colour(DD.cmd, "oal") + (Play.checkbox("goal" in self.order))
        # vxp__ = colour(DD.lcmd, "x") + colour(DD.cmd, "p") + (Play.checkbox("xp" in self.order))
        # vopt_ = colour(DD.lcmd, "o") + colour(DD.cmd, "pt") + (Play.checkbox(self.mark_opt))

        # vadmi = colour(DD.lcmd, "a") + colour(DD.cmd, "dmin") + (Play.checkbox(self.admin_mode))
        
        # vext = colour(DD.lcmd, "e") + colour(DD.cmd, "xt") + "(" + colour(DD.param, self.rep.lang) + ")"
        # visoes = f"{vlink} {vperc} {vgoal} {vxp__} {vopt_} {vadmi} "

        # # XP        
        # obt, total = self.game.get_xp_resume()
        # cur_level = XP().get_level(obt)
        # xp_next = XP().get_xp(cur_level + 1)
        # xp_prev = XP().get_xp(cur_level)
        # xpresume = colour(DD.skills, f"{obt}/{total}")
        # atual = obt - xp_prev
        # needed = xp_next - xp_prev
        # nbar = 35
        # nbarobt = int((atual * nbar // needed))
        # level = colour("bold, green", str(cur_level))
        # vxpall = f"{vrep} {vext} {xpresume} Level:{level} "
        # vxpall += colour("y", f"{str(atual).rjust(3)}/{str(needed).rjust(3)} ")
        # vxpnext = colour("y", "xp:") + "#" * nbarobt + "-" * (nbar - nbarobt)

        # def adding_break(base: str, added: str, lim: int):
        #     last = base.split("\n")[-1]
        #     if Color.len(last) + Color.len(added) > lim:
        #         return base + "\n" + added
        #     return base + added

        # skills = self.game.get_skills_resume()
        # vskills = ""
        # if skills:
        #     for s, v in skills.items():
        #         if s != "xp":
        #             vskills = adding_break(vskills, f"{colour(DD.skills, s)}:{v} ", nbar)

        # div0 = "────────────┴─────────────────────────"

        # div1 = "──────────────────────────────────────"

        # elementos = [intro]
        # if self.show_toolbar:
        #     elementos += [div0, visoes, div1, vxpall, vxpnext]
        #     if vskills:
        #         elementos += [vskills]
        # elementos += [div1]


        # # elementos = [intro] + ([div0, visoes, div1, vxpall, vxpnext, vskills] if self.show_toolbar else []) + [div1]
        # self.print_elementos(elementos)

    # def show_cmds(self):
        # controles = colour(DD.htext, "Números ") + colour(DD.cluster_key, "azul") + colour(DD.htext, " para expandir/colapsar")
        # letrass = colour(DD.htext, "Letras ") + colour(DD.tasks, "amarelo") + colour(DD.htext, " para marcar/desmarcar")
        # intervalos1 = colour(DD.htext, "Você pode digitar intervalos: ") + colour(DD.cluster_key, "1-3")
        # intervalos2 = colour(DD.htext, "Você pode digitar intervalos: ") + colour(DD.cluster_key, "B-F")

        # numeros = "─┯" + colour(DD.cluster_key, "3") + "  Digite " + colour(DD.cluster_key, "3") + (" para ver ou ocultar")
        
        # letras = " ├─" + colour(DD.tasks, "D ") + colour(DD.nothing, symbols.uncheck)
        # letras += " Tarefa. Dig " + colour(DD.cluster_key, "D") + " (des)marcar"
        
        # graduar = " ╰─" + colour(DD.tasks, "X ") + colour(DD.started, "4")  + " Tarefa. Dig " + colour(DD.cluster_key, "X4") + " dar nota 4"
        # todas = colour(DD.cluster_key, "<") + " ou " + colour(DD.cluster_key, ">") + colour(DD.htext, " (Compactar ou Descompactar Tudo)")
        
        # nomes_verm = colour(DD.htext, "Os nomes em vermelho são comandos")
        # prime_letr = colour(DD.htext, "Basta a primeira letra do comando")
        # vdown = colour(DD.lcmd, "d") + colour(DD.cmd, "own") + colour(DD.param, " <TaskID ...>") + colour(DD.htext, " (Download)")
        # vlink = colour(DD.lcmd, "l") + colour(DD.cmd, "ink") + colour(DD.param, " <TaskID ...>") + colour(DD.htext, " (Ver links)")
        # vexte = colour(DD.lcmd, "e") + colour(DD.cmd, "xt") + colour(DD.param, "  <EXT>") + colour(DD.htext, " (Mudar linguagem default)")
        # vsair = colour(DD.lcmd, "q") + colour(DD.cmd, "uit") + colour(DD.htext, " (Sair do programa)")
        # vcont = colour(DD.lcmd, "c") + colour(DD.cmd, "ont") + colour(DD.htext, " (Alterna contador de tarefas)")
        # vperc = colour(DD.lcmd, "p") + colour(DD.cmd, "erc") + colour(DD.htext, " (Alterna mostrar porcentagem)")
        # vgoal = colour(DD.lcmd, "g") + colour(DD.cmd, "oal") + colour(DD.htext, " (Alterna mostrar meta mínima)")
        # vopt_ = colour(DD.lcmd, "o") + colour(DD.cmd, "pt") + colour(DD.htext, " (Alterna ressaltar opcionais)")
        # vupda = colour(DD.lcmd, "u") + colour(DD.cmd, "pdate") + colour(DD.htext, " (Recarrega o repositório)")
        # vrota = colour(DD.lcmd, "r") + colour(DD.cmd, "otate") + colour(DD.htext, " (Rotaciona elementos visuais)")
        # vgame = colour(DD.lcmd, "a") + colour(DD.cmd, "dmin") + colour(DD.htext, " (Libera todas as missões)")

        # div0 = "──────────────────────────────────────"
        # div1 = "───────────── " + colour(DD.cluster_key, "Controles") + "──────────────"
        # div2 = "───────────────── " + colour(DD.lcmd, "Flags") + " ──────────────"
        # div3 = "───────────── " + colour(DD.lcmd, "Comandos") + " ───────────────"

        # elementos = []
        # elementos += [div1, controles, letrass, todas, numeros, letras, graduar, intervalos1, intervalos2]
        # elementos += [div2, nomes_verm, prime_letr, vcont, vperc, vgoal, vgame, div3, vdown, vlink, vexte, vupda, vrota, vsair]

        # self.print_elementos(elementos)
        # print(div0)
        # return False


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

    def mass_mark(self):
        obj = self.items[self.index].obj
        if isinstance(obj, Cluster):
            if obj.key not in self.expanded:
                self.expanded.append(obj.key)
                return
            full_open = True
            for q in self.get_avaliable_quests_from_cluster(obj):
                if q.key not in self.expanded:
                    self.expanded.append(q.key)
                    full_open = False
            if not full_open:
                return
            
            value = None
            for q in obj.quests:
                for t in q.get_tasks():
                    if value is not None:
                        t.set_grade(value)
                    else:
                        value = 10 if t.grade < 10 else 0
                        t.set_grade(value)
        elif isinstance(obj, Quest):
            if obj.key not in self.expanded:
                self.expanded.append(obj.key)
            else:
                value = None
                for t in obj.get_tasks():
                    if value is not None:
                        t.set_grade(value)
                    else:
                        value = 10 if t.grade < 10 else 0
                        t.set_grade(value)
        else:
            obj.set_grade(10 if obj.grade < 10 else 0)

    def set_grade(self, grade):
        obj = self.items[self.index].obj
        if isinstance(obj, Task):
            obj.set_grade(grade - ord("0"))

    def arrow_right(self):
        obj = self.items[self.index].obj
        if isinstance(obj, Cluster):
            if obj.key not in self.expanded:
                self.expanded.append(obj.key)
            else:
                self.index += 1
        elif isinstance(obj, Quest):
            if obj.key not in self.expanded:
                self.expanded.append(obj.key)
            else:
                while True:
                    self.index += 1
                    obj = self.items[self.index].obj
                    if isinstance(obj, Cluster) or isinstance(obj, Quest):
                        break
                    if self.index == len(self.items) - 1:
                        break
        elif isinstance(obj, Task):
            while True:
                obj = self.items[self.index].obj
                if isinstance(obj, Quest) or isinstance(obj, Cluster):
                    break
                if self.index == len(self.items) - 1:
                    break
                self.index += 1

    def arrow_left(self):
        obj = self.items[self.index].obj
        if isinstance(obj, Quest):
            if obj.key in self.expanded:
                self.expanded.remove(obj.key)
            else:
                while True:
                    self.index -= 1
                    obj = self.items[self.index].obj
                    if isinstance(obj, Cluster) or isinstance(obj, Quest) and obj.key in self.expanded:
                        break
                    if self.index == 0:
                        break
        elif isinstance(obj, Cluster):
            if obj.key in self.expanded:
                self.expanded.remove(obj.key)
                for q in obj.quests:
                    try:
                        self.expanded.remove(q.key)
                    except ValueError:
                        pass
            else:
                while True:
                    self.index -= 1
                    obj = self.items[self.index].obj
                    if isinstance(obj, Cluster) or isinstance(obj, Quest):
                        break
                    if self.index == 0:
                        break
        elif isinstance(obj, Task):
            while True:
                obj = self.items[self.index].obj
                if isinstance(obj, Quest):
                    break
                self.index -= 1
            
    def expand(self):
        obj = self.items[self.index].obj
        if isinstance(obj, Quest) or isinstance(obj, Cluster):
            if obj.key not in self.expanded:
                self.expanded.append(obj.key)

    def show_items(self, scr):

        if self.index >= len(self.items):
            self.index = len(self.items) - 1
            self.load_options()
            
        scr.clear()
        scr.refresh()
        lines, cols = scr.getmaxyx()
        scr.addstr(0, 0, f"lines: {lines} cols: {cols}")
        y = self.y_begin
        init = 0
        if len(self.items) > lines - self.y_end:
            init = max(0, self.index - (lines - self.y_end) + 1)
        for i in range(init, len(self.items)):
            sentence = self.items[i].sentence
            if lines - self.y_end <= y:
                break
            Fmt.write(scr, 0, y, sentence)
            y += 1
        scr.refresh()

    def toggle(self):
        obj = self.items[self.index].obj
        if isinstance(obj, Task):
            if obj.grade < 10:
                obj.set_grade(10)
            else:
                obj.set_grade(0)
        elif isinstance(obj, Quest) or isinstance(obj, Cluster):
            if obj.key in self.expanded:
                self.expanded.remove(obj.key)
            else:
                self.expanded.append(obj.key)

    def main(self, scr):
        curses.curs_set(0)  # Esconde o cursor
        Fmt.init_colors()  # Inicializa as cores

        # Exemplo de uso da função escrever
        while True:
            self.update_avaliable_quests()
            self.update_new()
            self.load_options()
            self.show_items(scr)

            value = scr.getch()  # Aguarda o pressionamento de uma tecla antes de sair
            if value == ord("q"):
                break
            elif value == curses.KEY_UP:
                self.index = max(0, self.index - 1)
            elif value == curses.KEY_DOWN:
                self.index = min(len(self.items) - 1, self.index + 1)
            elif value == curses.KEY_LEFT:
                self.arrow_left()
            elif value == curses.KEY_RIGHT:
                self.arrow_right()
            elif value == ord("c"):
                self.order_toggle("cont")
            elif value == ord("p"):
                self.order_toggle("perc")
            elif value == ord("g"):
                self.order_toggle("goal")
            elif value == ord("x"):
                self.order_toggle("xp")
            elif value == ord("a"):
                self.admin_mode = not self.admin_mode
            elif value == ord(">"):
                self.process_expand()
            elif value == ord("<"):
                self.process_collapse()
            elif value == ord(" "):
                self.toggle()
            elif value == ord("\n"):
                self.mass_mark()
            elif value >= ord("0") and value <= ord("9"):
                self.set_grade(value)
            elif value == curses.KEY_CANCEL:
                texto = Fmt.get_user_input(scr, "Digite um texto: ")
            self.save_to_json()

    

    # return True if the user wants to continue playing
    def play(self, graph_ext: str) -> bool:
        curses.wrapper(self.main)
        # success = True
        # first_graph_msg = True

        # while True:
        #     if success:
        #         self.reset_view()

        #     if graph_ext != "":
        #         self.generate_graph(graph_ext)
        #         if first_graph_msg:
        #             print("\nGrafo gerado em graph" + graph_ext)
        #             first_graph_msg = False

        #     print("\n" + colour(DD.play, "play$") + " ", end="")
        #     line = input()
        #     if line == "":
        #         success = True
        #         continue
        #     if line == "q" or line == "quit":
        #         return False
        #     if line == "u" or line == "update":
        #         return True
        #     # actions = Util.expand_range(line)
        #     actions = line.split(" ")
        #     success = self.take_actions(actions)
        #     self.save_to_json()
