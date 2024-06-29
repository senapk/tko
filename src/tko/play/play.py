from ..game.game import Game
from ..game.cluster import Cluster
from ..game.quest import Quest
from ..game.task import Task
from ..game.xp import XP
from ..game.graph import Graph

from typing import List, Dict, Tuple, Optional, Any
from ..settings import RepoSettings, LocalSettings
from ..down import Down
from ..util.tfmt import symbols
from ..game.sentence import Sentence
from .style import Style
from .cfmt import Fmt

import os
import curses



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
        self.flags_bar = "toolbar" in self.rep.view
        self.xp_bar = "xp" in self.rep.view
        self.admin_mode = "admin" in self.rep.view
        # self.mark_opt = "opt" in self.rep.view
        self.mark_opt = True
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

        self.index_selected = 0
        self.index_begin = 0
        self.y_begin = 2
        self.y_end = 3
        
        self.items: List[Entry] = []

        self.first_loop = True
        self.graph_ext = ""

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
        if self.flags_bar:
            self.rep.view.append("toolbar")
        # if self.mark_opt:
        #     self.rep.view.append("opt")
        if self.xp_bar:
            self.rep.view.append("xp")
            
        self.fnsave()

    def test_color(self, scr):
        fg = "rgbymcwk"
        bg = " RGBYMCWK"
        lines, cols = scr.getmaxyx()
        scr.erase()
        for l in range(8):
            for c in range(9):
                cor = fg[l] + bg[c]
                Fmt.write(scr, 3 * l, 5 * c, Sentence().addf(cor, f" {cor} "))
        
        scr.refresh()
        scr.getch()


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

        added_clusters = [c for c in self.avaliable_clusters if c not in old_clusters]
        added_quests = [q for q in self.avaliable_quests if q not in old_quests]
        
        for c in added_clusters:
            self.new_items.append(c.key)
        for q in added_quests:
            self.new_items.append(q.key)

    def add_focus(self, color, in_focus):
        if not in_focus:
            return color
        if color == "":
            return "k" + Style.focus
        return Style.focus + color

    def str_task(self, in_focus: bool, t: Task, ligc: str, ligq: str, min_value = 1) -> Sentence:
        output = Sentence()
        output.addt(" " + ligc + " " + ligq)\
              .concat(t.get_grade_symbol(min_value))\
              .addt(" ")

        value = Style.opt_task if self.mark_opt and t.opt else ""
        output.addf(self.add_focus(value, in_focus), t.title)
        
        if self.xp_bar:
            xp = ""
            for s, v in t.skills.items():
                xp += f" +{s}:{v}"
            output.addf(Style.skills, xp)
        return output
    
    def str_quest(self, in_focus: bool, q: Quest, lig: str) -> Sentence:
        con = "━─" if q.key not in self.expanded else "─┯"
        output: Sentence = Sentence().addt(" " + lig + con + " ")

        value = Style.opt_quest if self.mark_opt and q.opt else ""
        output.addf(self.add_focus(value, in_focus), q.title)

        for item in self.order:
            if item == "cont":
                output.addt(" ").concat(q.get_resume_by_tasks())
            elif item == "perc":
                output.addt(" ").concat(q.get_resume_by_percent())
            elif item == "goal":
                output.addt(" ").concat(q.get_requirement())
        if self.xp_bar:
            xp = ""
            for s,v in q.skills.items():
                xp += f" +{s}:{v}"
            output.addf(Style.skills, " " + xp)
                
        if q.key in self.new_items:
            output.addf(Style.new, " [new]")

        return output
        

    def str_cluster(self, in_focus: bool, cluster: Cluster, quests: List[Quest]) -> Sentence:
        output: Sentence = Sentence()
        opening = "━─"        
        if cluster.key in self.expanded:
            opening = "─┯"        
        output.addt(opening + " ")
        value = Style.cluster_title
        output.addf(self.add_focus(value, in_focus), cluster.title.strip())
        output.addt(" ").concat(cluster.get_resume_by_percent())
        if cluster.key in self.new_items:
            output.addf(Style.new, " [new]")

        return output
    
    def get_avaliable_quests_from_cluster(self, cluster: Cluster) -> List[Quest]:
        return [q for q in cluster.quests if q in self.avaliable_quests]

    def reload_options(self):
        index = 0
        self.items = []
        for cluster in self.avaliable_clusters:
            quests = self.get_avaliable_quests_from_cluster(cluster)
            sentence = self.str_cluster(self.index_selected == index, cluster, quests)
            self.items.append(Entry(cluster, sentence))
            index += 1

            if not cluster.key in self.expanded: # va para proximo cluster
                continue

            for q in quests:
                lig = "├" if q != quests[-1] else "╰"
                sentence = self.str_quest(self.index_selected == index, q, lig)
                self.items.append(Entry(q, sentence))
                index += 1
                if q.key in self.expanded:
                    for t in q.get_tasks():
                        ligc = "│" if q != quests[-1] else " "
                        ligq = "├ " if t != q.get_tasks()[-1] else "╰ "
                        sentence = self.str_task(self.index_selected == index, t, ligc, ligq, q.tmin)
                        self.items.append(Entry(t, sentence))
                        index += 1

        if self.index_selected >= len(self.items):
            self.index_selected = len(self.items) - 1


    def down_task(self, rootdir, task: Task, ext: str):
        output = []
        if task.key in task.title:
            output.append(f"tko down {self.repo_alias} {task.key} -l {ext}")
            Down.download_problem(rootdir, self.repo_alias, task.key, ext, output)
        else:
            output.append(f"Essa não é uma tarefa de código")
        return output

    def check_rootdir(self):
        if self.local.rootdir == "":
            print("Diretório raiz para o tko ainda não foi definido")
            print("Você deseja utilizer o diretório atual")
            print((Style.shell, "  " + os.getcwd()))
            print("como raiz para o repositório de " + self.repo_alias + "? (s/n) ", end="")
            answer = input()
            if answer == "s":
                self.local.rootdir = os.getcwd()
                self.fnsave()
                print("Você pode alterar o diretório raiz navegando para o diretório desejado e executando o comando")
                print((Style.shell, "  tko config --root"))
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
            print("Você pode mudar a linguagem de programação apertando e")

    def process_down(self):
        self.check_rootdir()
        self.check_language()
        rootdir = os.path.relpath(os.path.join(self.local.rootdir, self.repo_alias))
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Task):
            self.down_task(rootdir, obj, self.rep.lang)
        else:
            print("Essa não é uma tarefa de código")
        input("Digite enter para continuar")
    # def find_cluster(self, key) -> Optional[Cluster]:
    #     for c in self.game.clusters:
    #         if c.key == key:
    #             return c
    #     return None

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
    
    def process_ext(self, scr):
        while True:
            opcoes = ["", "c", "cpp", "py", "ts", "js", "java"]
            scr.erase()
            ext = Fmt.get_user_input(scr, f"Digite a extensão: .")
            scr.refresh()
            if ext in opcoes:
                self.rep.lang = ext
                self.fnsave()
                return
            else:
                scr.addstr(1, 0, "Extensão inválida")
                scr.addstr(2, 0, "Escolha uma das opções: " + ", ".join(opcoes))
                scr.refresh()
                scr.getch()

    def order_toggle(self, token):
        if token in self.order:
            self.order.remove(token)
        else:
            self.order.append(token)

    @staticmethod
    def checkbox(value) -> Sentence:
        return Sentence().addf(Style.check, symbols.opcheck) if value else Sentence().addf(Style.uncheck, symbols.opuncheck)

    def show_skills_bar(self, scr, size_footer):
        lines, cols = scr.getmaxyx()
        skills_line = Sentence()
        skills = self.game.get_skills_resume()
        if skills and self.xp_bar:
            i = 0
            for s, v in skills.items():
                if s != "xp":
                    skills_line.addf(Style.bar_skills, f"{s}:{v}")
                    if i < len(skills) - 1:
                        skills_line.addf(Style.bar_bg, "  ")
                        i += 1
        
        Fmt.write(scr, lines - 3, 0, skills_line.addf(Style.bar_bg, (size_footer - 1 - skills_line.len()) * " "))

    def show_task_link(self, scr):
        lines, cols = scr.getmaxyx()
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Task):
            link = obj.link
            if link:
                Fmt.write(scr, lines - 2, 0, Sentence().addt(link))

    def show_footer(self, scr) -> int:
        lines, cols = scr.getmaxyx()
        footer = Sentence()
        footer.addf(self.get_cb(self.flags_bar), f" Flags [f] ").addt(" ")
        footer.addf(self.get_cb(self.xp_bar), f" XP [x] ").addt(" ")

        msgs = [" Quit [q] ", " Down [d] ", " Grade [0-9] ", " Expand [>] ", " Collapse [<] ", " Toggle [space|enter] "]

        for x in msgs:
            footer.addf(Style.bar_skills, x).addt(" ")
        Play.trim_sentence(footer, cols - 1)
        Fmt.write(scr, lines - 1, 0, footer)
        return footer.len()


    def get_cb(self, value):
        return Style.bar_true if value else Style.bar_false

    @staticmethod
    def trim_sentence(sentence: Sentence, limit: int):
        for i in range(len(sentence.data) - 1, -1, -1):
            if sentence.len() >= limit:
                fmt, text = sentence.data[i]
                try:
                    sentence.data[i] = (fmt, "[" + text.split("[")[1].split("]")[0] + "]") 
                except IndexError:
                    pass


    def show_info(self, scr) -> Sentence:
        lines, cols = scr.getmaxyx()
        total_perc = 0
        header = Sentence()
        for q in self.game.quests.values():
            total_perc += q.get_percent()
        if self.game.quests:
            total_perc = total_perc // len(self.game.quests)
        

        xheader = Sentence()
        obt, total = self.game.get_xp_resume()
        cur_level = XP().get_level(obt)
        xp_next = XP().get_xp(cur_level + 1)
        xp_prev = XP().get_xp(cur_level)
        atual = obt - xp_prev
        needed = xp_next - xp_prev
        header.addf(Style.bar_main, f" {self.repo_alias.upper()} {total_perc}% ").addt(" ")
        if self.xp_bar:
            header.addf(Style.bar_xp, f" Level:{cur_level} ").addt(" ")
            header.addf(Style.bar_xp, f" XP:{str(atual)}/{str(needed)} ").addt(" ")
            # header.addf("wC", f" total:{obt}/{total} ").addt(" ")
            header.addf(Style.bar_xp, f" Total:{obt} ").addt(" ")

        header.addf(Style.bar_ext, f" Ext:{self.rep.lang} [e] ").addt(" ")

        if self.flags_bar:
            header.addf(self.get_cb("cont" in self.order), " Count [c] ").addt(" ")
            header.addf(self.get_cb("perc" in self.order), " Percent [p] ").addt(" ")
            header.addf(self.get_cb("goal" in self.order), " Goals [g] ").addt(" ")
            # header.addf(self.get_cb(self.mark_opt), " Optional [o] ").addt(" ")
            header.addf(self.get_cb(self.admin_mode), " Admin [A] ").addt(" ")

        Play.trim_sentence(header, cols - 1)


        self.show_task_link(scr)
        size_footer = self.show_footer(scr)
        self.show_skills_bar(scr, size_footer)

        bar = symbols.hbar
        Fmt.write(scr, 0, 0, header)
        total = size_footer - 1
        full_line = bar * total
        done_len = int((atual * total // needed))
        xheader.addf("g", full_line[:done_len]).addf("r", full_line[done_len:])
        Fmt.write(scr, 1, 0, xheader)

    def generate_graph(self, scr):
        if not self.first_loop:
            return
        if self.graph_ext == "":
            return
        reachable: List[str] = [q.key for q in self.avaliable_quests]
        counts = {}
        for q in self.game.quests.values():
            done = len([t for t in q.get_tasks() if t.is_complete()])
            init = len([t for t in q.get_tasks() if t.in_progress()])
            todo = len([t for t in q.get_tasks() if t.not_started()])
            counts[q.key] = f"{done} / {done + init + todo}\n{q.get_percent()}%"

        Graph(self.game).set_opt(self.mark_opt).set_reachable(reachable).set_counts(counts).set_graph_ext(self.graph_ext).generate()
        lines, _cols = scr.getmaxyx()
        if self.first_loop:
            text = Sentence().addt(f"Grafo gerado em graph{self.graph_ext}")
            Fmt.write(scr, lines - 1, 0, text)
            

    def update_new(self):
        self.new_items = [item for item in self.new_items if item not in self.expanded]

    def mass_mark(self):
        obj = self.items[self.index_selected].obj
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
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Task):
            obj.set_grade(grade - ord("0"))

    def arrow_right(self):
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Cluster):
            if obj.key not in self.expanded:
                self.expanded.append(obj.key)
            else:
                self.index_selected += 1
        elif isinstance(obj, Quest):
            if obj.key not in self.expanded:
                self.expanded.append(obj.key)
            else:
                while True:
                    self.index_selected += 1
                    obj = self.items[self.index_selected].obj
                    if isinstance(obj, Cluster) or isinstance(obj, Quest):
                        break
                    if self.index_selected == len(self.items) - 1:
                        break
        elif isinstance(obj, Task):
            while True:
                obj = self.items[self.index_selected].obj
                if isinstance(obj, Quest) or isinstance(obj, Cluster):
                    break
                if self.index_selected == len(self.items) - 1:
                    break
                self.index_selected += 1

    def arrow_left(self):
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Quest):
            if obj.key in self.expanded:
                self.expanded.remove(obj.key)
            else:
                while True:
                    if self.index_selected == 0:
                        break
                    self.index_selected -= 1
                    obj = self.items[self.index_selected].obj
                    if isinstance(obj, Cluster) or isinstance(obj, Quest) and obj.key in self.expanded:
                        break
                    if self.index_selected == 0:
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
                    if self.index_selected == 0:
                        break
                    self.index_selected -= 1
                    obj = self.items[self.index_selected].obj
                    if isinstance(obj, Cluster) or isinstance(obj, Quest):
                        break
                    if self.index_selected == 0:
                        break
        elif isinstance(obj, Task):
            while True:
                obj = self.items[self.index_selected].obj
                if isinstance(obj, Quest):
                    break
                self.index_selected -= 1
            
    def expand(self):
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Quest) or isinstance(obj, Cluster):
            if obj.key not in self.expanded:
                self.expanded.append(obj.key)

    def show_items(self, scr):

        self.reload_options()
        
        scr.erase()
        
        lines, _cols = scr.getmaxyx()

        self.show_info(scr)

        y = self.y_begin
        if len(self.items) < lines - self.y_end - self.y_begin:
            self.index_begin = 0
        else:
            if self.index_selected < self.index_begin:
                self.index_begin = self.index_selected
            elif self.index_selected >= self.index_begin + lines - self.y_end - self.y_begin:
                self.index_begin = self.index_selected - lines + self.y_end + self.y_begin + 1
        init = self.index_begin

        for i in range(init, len(self.items)):
            sentence = self.items[i].sentence
            if y >= lines - self.y_end:
                break
            Fmt.write(scr, y, 0, sentence)
            y += 1
        scr.refresh()

    def toggle(self):
        obj = self.items[self.index_selected].obj
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
            self.show_items(scr)
            self.generate_graph(scr)
            value = scr.getch()  # Aguarda o pressionamento de uma tecla antes de sair
            if value == ord("q"):
                break
            elif value == curses.KEY_UP:
                self.index_selected = max(0, self.index_selected - 1)
            elif value == curses.KEY_DOWN:
                self.index_selected = min(len(self.items) - 1, self.index_selected + 1)
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
                self.xp_bar = not self.xp_bar
                # if self.xp_bar:
                #     self.flags_bar = False
            elif value == ord("f"):
                self.flags_bar = not self.flags_bar
                # if self.flags_bar:
                #     self.xp_bar = False
            elif value == ord("A"):
                self.admin_mode = not self.admin_mode
                self.reload_options()
            elif value == ord(">"):
                self.process_expand()
            elif value == ord("<"):
                self.process_collapse()
            elif value == ord(" ") or value == ord("\n"):
                self.toggle()
            # elif value == ord("o"):
            #     self.mark_opt = not self.mark_opt
            elif value == ord("e"):
                self.process_ext(scr)
            elif value == ord("d"):
                return self.process_down
            # elif value == ord("\n"):
            #     self.mass_mark()
            elif value >= ord("0") and value <= ord("9"):
                self.set_grade(value)
            elif value == ord("T"):
                self.test_color(scr)
            self.save_to_json()
        
            if self.first_loop:
                self.first_loop = False

    
    # return True if the user wants to continue playing
    def play(self, graph_ext: str) -> bool:
        self.graph_ext = graph_ext
        while True:
            output = curses.wrapper(self.main)
            if output is None:
                return
            else:
                output()

