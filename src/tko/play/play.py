from ..game.game import Game
from ..game.cluster import Cluster
from ..game.quest import Quest
from ..game.task import Task
from ..game.xp import XP
from ..game.graph import Graph

from typing import List, Dict, Tuple, Optional, Any
from ..settings import RepoSettings, LocalSettings
from ..down import Down
from ..util.symbols import symbols
from ..util.sentence import Sentence
from .style import Style
from .fmt import Fmt
from .frame import Frame
from .input import Input
import time
import webbrowser

import os
import curses

class Entry:
    def __init__(self, obj: Any, sentence: Sentence):
        self.obj = obj
        self.sentence = sentence

    def get(self):
        return self.sentence

class Flags:
    percent = "percent"
    count = "count"
    xp    = "xp"
    goals = "goals"
    down = "down"
    admin = "admin"
    flags_bar = "flags_bar"
    skills_bar = "skills_bar"
    help_bar = "help_bar"
    top_bar = "top_bar"
    group_bar = "group_bar"
    quest_bar = "quest_bar"

class Play:
    cluster_prefix = "'"

    def __init__(self, local: LocalSettings, game: Game, rep: RepoSettings, repo_alias: str, fnsave):
        self.fnsave = fnsave
        self.local = local
        self.repo_alias = repo_alias
        self.rep = rep

        self.input_layer: List[Input] = []

        # self.mark_opt = "opt" in self.rep.view
        self.mark_opt = True
        order = [entry for entry in self.rep.view if entry.startswith("order:")]
        if len(order) > 0:
            self.flags = [v for v in order[0][6:].split(",") if v != '']
        else:
            self.flags = []

        self.game: Game = game
        self.expanded: List[str] = [x for x in self.rep.expanded]
        self.new_items: List[str] = [x for x in self.rep.new_items]
        self.avaliable_quests: List[Quest] = [] # avaliable quests
        self.avaliable_clusters: List[Cluster] = [] # avaliable clusters

        self.index_selected = 0
        self.index_begin = 0
  
        
        self.items: List[Entry] = []

        self.first_loop = True
        self.graph_ext = ""

        self.load_rep()

        self.help_base = ["Quit[q]", "Help[h]", "Move[wasd]", "Mark[enter]"]
        self.help_extra = ["OpenLink[o]", "GetTask[g]", "Grade[0-9]", "Lang[l]", "Expand[>]", "Collapse[<]",  "MassMark[M]"]

    def save_to_json(self):
        self.rep.expanded = [x for x in self.expanded]
        self.rep.new_items = [x for x in self.new_items]

        self.rep.tasks = {}
        for t in self.game.tasks.values():
            if t.grade != 0:
                self.rep.tasks[t.key] = str(t.grade)
        self.rep.view = []
        self.rep.view.append("order:" + ",".join(self.flags))
            
        self.fnsave()

    def test_color(self, scr):
        fg = "rgbymcwk"
        bg = " RGBYMCWK"
        lines, cols = scr.getmaxyx()
        scr.erase()
        for l in range(8):
            for c in range(9):
                cor = fg[l] + bg[c]
                Fmt.write(3 * l, 5 * c, Sentence().addf(cor, f" {cor} "))
        
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
        if self.flags_on(Flags.admin):
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

        if self.flags_on(Flags.down):
            path = os.path.join(self.local.rootdir, self.repo_alias, t.key)
            if os.path.isdir(path):
                output.addt(" ").addf("y", f"[{path}]")

        if self.flags_on(Flags.xp):
            xp = ""
            for s, v in t.skills.items():
                xp += f" +{s}:{v}"
            output.addf(Style.skills, xp)
        return output
    
    def str_quest(self, in_focus: bool, q: Quest, lig: str) -> Sentence:
        con = "━─" if q.key not in self.expanded else "─┯"
        output: Sentence = Sentence().addt(" " + lig + con + " ")

        value = Style.opt_quest if self.mark_opt and q.opt else ""
        title = q.title
        if in_focus:
            output.addf(self.add_focus(value, in_focus), q.title)
        else:
            if self.flags_on(Flags.quest_bar):
                output.concat(self.build_bar(title, q.get_percent() / 100, len(title), "b" + value, "m" + value))
            else:
                output.addf(value, title)

        for item in self.flags:
            if item == Flags.count:
                if self.flags_on(Flags.percent):
                    output.addt(" ").concat(q.get_resume_by_percent())
                else:
                    output.addt(" ").concat(q.get_resume_by_tasks())
            elif item == Flags.goals:
                output.addt(" ").concat(q.get_requirement())
        if self.flags_on(Flags.xp):
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
        title = cluster.title
        if in_focus:
            output.addf(self.add_focus(value, in_focus), title)
        else:
            if self.flags_on(Flags.group_bar):
                output.concat(self.build_bar(title, cluster.get_percent() / 100, len(title), "g", "y"))
            else:
                output.addf(value, title)
        if self.flags_on(Flags.count):
            if self.flags_on(Flags.percent):
                output.addt(" ").concat(cluster.get_resume_by_percent())
            else:
                output.addt(" ").concat(cluster.get_resume_by_quests())
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

    def down_task(self, rootdir, obj: Any, ext: str):
        if isinstance(obj, Task) and obj.key in obj.title:
            task: Task = obj
            down_frame = Input().warning().set_header(Sentence().addt(" Baixando tarefa "))
            down_frame.addt(f"tko down {self.repo_alias} {task.key} -l {ext}")
            self.add_input(down_frame)

            def fnprint(text):
                down_frame.addt(text)
                down_frame.draw()
                Fmt.refresh()

            Down.download_problem(rootdir, self.repo_alias, task.key, ext, fnprint)
        else:
            if isinstance(obj, Quest):
                self.add_input(Input().addt("Essa é uma missão").addt("você só pode baixar tarefas").error())
            elif isinstance(obj, Cluster):
                self.add_input(Input().addt("Esse é um grupo").addt("você só pode baixar tarefas").error())
            else:
                self.add_input(Input().addt("Essa não é uma tarefa de código").error())



    def set_rootdir(self):
        def chama(value):
            if value == "yes":
                self.local.rootdir = os.getcwd()
                self.fnsave()
                self.add_input(Input()\
                    .addt("Diretório raiz definido como ")\
                    .addt("  " +  self.local.rootdir)\
                    .addt("Você pode alterar o diretório raiz navegando para o")\
                    .addt("diretório desejado e executando o comando")\
                    .addt("  tko config --root")\
                    .addt("")\
                    .set_exit_fn(self.set_language)
                    .warning())
            else:
                self.add_input(Input()\
                    .addt("Navague para o diretório desejado e execute o comando")\
                    .addt("  tko config --root")\
                    .addt("ou rode o tko play novamente na pasta desejada").warning())

        
        self.add_input(Input().addt("Diretório raiz para o tko ainda não foi definido")\
            .addt("Você deseja utilizar o diretório atual")\
            .addt(os.getcwd())\
            .addt("como raiz para o repositório de " + self.repo_alias + "?")\
            .set_options(["yes", "no"])\
            .get_answer(chama))
    
    def set_language(self):

        def back(value):
            self.rep.lang = value
            self.fnsave()
            self.add_input(Input()\
            .addt("      Linguagem alterada para " + value)\
            .addt("Você pode mudar a linguagem de programação")\
            .adds(Sentence().addt("            apertando ").addf("G", "l"))\
            .warning())
            

        self.add_input(Input()\
            .addt("   Escolha a extensão")\
            .addt(" default para os rascunhos") \
            .addt("")\
            .addt(" Selecione e tecle enter")\
            .set_options(["c", "cpp", "py", "ts", "js", "java", "hs"])\
            .get_answer(back))

    def process_down(self):

        if self.local.rootdir == "":
            self.set_rootdir()
            return

        if self.rep.lang == "":
            self.set_language()
            return
    
        rootdir = os.path.relpath(os.path.join(self.local.rootdir, self.repo_alias))
        obj = self.items[self.index_selected].obj
        self.down_task(rootdir, obj, self.rep.lang)
        

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
    
    def flags_toggle(self, token):
        if token in self.flags:
            self.flags.remove(token)
        else:
            self.flags.append(token)


    @staticmethod
    def checkbox(value) -> Sentence:
        return Sentence().addf(Style.check, symbols.opcheck) if value else Sentence().addf(Style.uncheck, symbols.opuncheck)

    def build_bar_links(self) -> str:
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Task):
            link = obj.link
            if link:
                return link
        return ""

    def flags_on(self, value):
        return value in self.flags

    def flags_color(self, flag: str) -> str:
        if self.flags_on(flag):
            return Style.flags_true
        return Style.flags_false

    def build_bar(self, text:str, percent: float, length: int, fmt_true: str = "/kC", fmt_false: str = "/kY") -> Sentence:
        prefix = (length - len(text)) // 2
        sufix = length - len(text) - prefix
        text = " " * prefix + text + " " * sufix
        xp_bar = Sentence()
        total = length
        full_line = text
        done_len = int(percent * total)
        xp_bar.addf(fmt_true, full_line[:done_len]).addf(fmt_false, full_line[done_len:])
        return xp_bar

    def show_main_bar(self, frame: Frame):
        frame.set_header(Sentence().addt("{").addf("/", f"Tarefas lang:{self.rep.lang}").addt("}"))
        frame.set_footer(Sentence().addt("{" + self.build_bar_links() + "}"))
        frame.draw()

        dy, dx = frame.get_inner()
        y = 0
        if len(self.items) < dy:
            self.index_begin = 0
        else:
            if self.index_selected < self.index_begin: # subiu na tela
                self.index_begin = self.index_selected
            elif self.index_selected >= dy + self.index_begin: # desceu na tela
                self.index_begin = self.index_selected - dy + 1
        init = self.index_begin
    
        for i in range(init, len(self.items)):
            sentence = self.items[i].sentence
            frame.write(y, 0, sentence)
            y += 1

    def show_skills_bar(self, frame_xp):
            dy, dx = frame_xp.get_inner()
            xp = XP(self.game)
            total_perc = int(100 * (xp.get_xp_total_obtained() / xp.get_xp_total_available()))
            if self.flags_on(Flags.percent):
                text =  f" Total:{total_perc}%"
            else:
                text =  f" Total:{xp.get_xp_total_obtained()}"
    

            total_bar = self.build_bar(text, total_perc / 100, dx - 2, "/kC", "/kM")
            frame_xp.set_header(Sentence().addt("{").addf("/", "Skills").addt("}"), "^")
            frame_xp.set_footer(Sentence().concat(total_bar), "^")
            frame_xp.draw()

            total, obt = self.game.get_skills_resume()
            index = 0
            for skill, value in total.items():
                if self.flags_on(Flags.percent):
                    text = f"{skill}:{int(100 * obt[skill] / value)}%"
                else:
                    text = f"{skill}:{obt[skill]}/{value}"
    
                perc = obt[skill]/value
                skill_bar = self.build_bar(text, perc, dx - 2, "/kC", "/kR")
                frame_xp.write(index, 1, skill_bar)
                index += 2

    def show_flags_bar(self, frame: Frame):
        frame.set_header(Sentence().addt("{").addf("/", "Flags").addt("}"), "^")
        frame.draw()

        def add_flag(_flag, _text, _key):
            color = self.flags_color(_flag)
            if self.flags_on(_flag):
                s = Sentence().addf(color, _text).addf(color, (8 - len(_text)) * " ").addf("", _key)
            else:
                s = Sentence().addf("", _key).addf(color, (8 - len(_text)) * " ").addf(color, _text)
            frame.print(1, s)


        add_flag(Flags.count,   "Count",   "[C]")
        add_flag(Flags.goals,   "Goals",   "[G]")
        add_flag(Flags.down,    "Down",    "[D]")
        add_flag(Flags.xp,    "XP",    "[X]")
        add_flag(Flags.percent, "Percent", "[P]")
        add_flag(Flags.admin,   "Admin",   "[A]")
        add_flag(Flags.group_bar, "GroupBar", "[r]")
        add_flag(Flags.quest_bar, "QuestBar", "[t]")



    def build_list_sentence(self, items: List[str]) -> Sentence:
        help = Sentence()
        try:
            for x in items:
                label, key = x.split("[")
                key = "[" + key
                help.addf("/", label).addt(key).addt(" ")
        except ValueError:
            raise ValueError("Desempacotando mensagens")        
        help.data.pop()

        return help

    def show_help(self):
        help: Input = Input().add_extra_exit("h").warning()
        self.add_input(help)
        help.set_header(Sentence().addf("/", " Help "))
        help.addt("Barras alternáveis")
        help.adds(Sentence().addt("  ").addf("", "F").addt(" - Mostrar ou esconder a barra de flags"))
        help.adds(Sentence().addt("  ").addf("", "H").addt(" - Mostrar ou esconder a barra de ajuda"))
        help.adds(Sentence().addt("  ").addf("", "S").addt(" - Mostrar ou esconder a barra de skills"))
        help.addt("")
        help.addt("Comandos")
        help.addt("  q - Fechar o aplicativo")
        help.addt("  h - Mostrar essa tela de ajuda")
        help.addt("")
        help.addt("Controles")
        help.addt("  setas ou wasd   - Para navegar entre os elementos")
        help.addt("  enter ou espaço - Marcar ou desmarcar, expandir ou contrair")
        help.addt("  0 a 9 - Definir a nota parcial para uma tarefa")
        help.addt("      o - Abrir tarefa em uma aba do browser")
        help.addt("      g - Baixar um tarefa de código para seu dispositivo")
        help.addt("")
        help.addt("Flags")
        help.addt("  Muda a forma de exibição dos elementos")
        help.addt("  Ligue ou desligue e veja o resultado")
        help.addt("")
        help.addt("Extra")
        help.addt("  l - Mudar a linguagem de download dos rascunhos")
        help.addt("  > - Expandir tudo")
        help.addt("  < - Contrair tudo")

    def desable_on_resize(self):
        lines, cols = Fmt.get_size()
        if cols < 50 and self.flags_on("skills_bar") and self.flags_on("flags_bar"):
            self.flags_toggle("skills_bar")
        elif cols < 30 and self.flags_on("flags_bar"):
            self.flags_toggle("flags_bar")
        elif cols < 35 and self.flags_on("skills_bar"):
            self.flags_toggle("skills_bar")

    def draw_warnings(self):
        if len(self.input_layer) > 0:
            if not self.input_layer[0].enable:
                self.input_layer = self.input_layer[1:]

        if len(self.input_layer) > 0 and self.input_layer[0].enable:
            self.input_layer[0].draw()

    def show_bottom_bar(self, frame: Frame):
        help = self.build_list_sentence(self.help_extra)
        for s in help:
            if s.text.startswith("["):
                s.fmt = ""
            elif not s.text.startswith(" "):
                s.fmt = "B"
        dx = frame.get_dx()
        # help.trim_spaces(dx)
        help.trim_alfa(dx)
        help.trim_end(dx)
        frame.set_header(help, "^")
        # frame.set_border_square()
        frame.set_border_none()
        frame.draw()

    def show_top_bar(self, frame: Frame) -> None:
        help = self.build_list_sentence(self.help_base)
        dx = frame.get_dx()
        help.trim_alfa(dx)
        help.trim_end(dx)
        for s in help:
            if s.text.startswith("["):
                s.fmt = ""
            elif not s.text.startswith(" "):
                s.fmt = "B"
        frame.set_footer(help, "^")
        frame.draw()


        content = Sentence().addt(" ")
        content.addf("C", f"({self.repo_alias.upper()})").addt(" ")

        def add_flag(flag, text, key):
            color = self.flags_color(flag)
            if self.flags_on(flag):
                content.addf(color + "/", text).addf(color, key).addt(" ")
            else:
                content.addf(color, key).addf(color + "/", text).addt(" ")
        
        add_flag(Flags.flags_bar, "FlagsBar", "[F]")
        add_flag(Flags.help_bar, "HelpBar", "[H]")
        add_flag(Flags.skills_bar, "SkillsBar", "[S]")
        
        for s in content:
            if s.text.startswith("["):
                s.fmt = ""

        xp = XP(self.game)

        if xp.get_xp_total_obtained() == xp.get_xp_total_available():
            text = "Você atingiu o máximo de xp!"
            percent = 100.0
        else:
            if self.flags_on(Flags.percent):
                text = f"L:{xp.get_level()} XP:{int(100 * xp.get_xp_level_current() / xp.get_xp_level_needed())}%"
            else:
                text = f"L:{xp.get_level()} XP:{xp.get_xp_level_current()}/{xp.get_xp_level_needed()}"
            percent = float(xp.get_xp_level_current()) / float(xp.get_xp_level_needed())
        size = max(15, dx - content.len() - 1)
        xp_bar = self.build_bar(text, percent, size).addt(" ")

        limit = dx - xp_bar.len()
        content.trim_spaces(limit)
        content.trim_alfa(limit)
        content.trim_end(limit)

        frame.write(0, 0, content.concat(xp_bar))
        return content

    def show_items(self):
        self.desable_on_resize()
        self.reload_options()        
        Fmt.erase()

        lines, cols = Fmt.get_size()
        main_sx = cols  # tamanho em x livre
        main_sy = lines #size em y avaliable
        
        top_y = -1
        top_dy = 3
        frame_top = Frame(top_y, 0).set_size(3, main_sx)
        self.show_top_bar(frame_top)
        
        bottom_sy = 0
        if self.flags_on(Flags.help_bar):
            bottom_sy = 1
            frame_bottom = Frame(lines - 1, 0).set_size(3, main_sx)
            self.show_bottom_bar(frame_bottom)

        mid_y = top_y + top_dy
        mid_sy = main_sy - (top_y + top_dy + bottom_sy)

        skills_sx= 0
        if self.flags_on("skills_bar"):
            skills_sx = max(20, main_sx // 4)
            frame_skills = Frame(mid_y, cols - skills_sx).set_size(mid_sy, skills_sx)
            self.show_skills_bar(frame_skills)

        flags_sx = 0
        if self.flags_on("flags_bar"):
            flags_sx = 15
            frame_flags = Frame(mid_y, 0).set_size(mid_sy, flags_sx)
            self.show_flags_bar(frame_flags)

        task_sx = main_sx - flags_sx - skills_sx
        frame_main = Frame(mid_y, flags_sx).set_size(mid_sy, task_sx)
        self.show_main_bar(frame_main)

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
            Fmt.write(lines - 1, 0, text)
            
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

    def open_link(self):
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Task):
            task: Task = obj
            if task.link.startswith("http"):
                webbrowser.open_new_tab(task.link)
            self.add_input(Input().set_header(Sentence().addf("/", " Abrindo link ")).addt(task.link).warning())
        elif isinstance(obj, Quest):
            self.add_input(Input().timer(1).addt("Essa é uma missão").addt("você só pode abrir o link").addt("de tarefas").error())
        else:
            self.add_input(Input().timer(1).addt("Esse é um grupo").addt("você só pode abrir o link").addt("de tarefas").error())
        


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

    def add_input(self, value: Input):
        self.input_layer.append(value)

    def check_disable_flags(self):
        lines, cols = Fmt.get_size()
        if cols < 50:
            if self.flags_on("flags_bar"):
                self.flags_toggle("flags_bar")

    def check_disable_skills(self):
        lines, cols = Fmt.get_size()
        if cols < 50:
            if self.flags_on(Flags.skills_bar):
                self.flags_toggle("skills_bar")
        
    def send_ligado(self, msg: str, flag: bool, key: str) -> Sentence:
        if self.flags_on(flag):
            opt = Sentence().addt(msg).addf("G", "ligado")
        else:
            opt = Sentence().addt(msg).addf("R", "desligado")
        
        self.add_input(Input().adds(opt).warning().timer(0.5).add_extra_exit(key))


    def main(self, scr):
        # scr.nodelay(True)
        curses.curs_set(0)  # Esconde o cursor
        Fmt.init_colors()  # Inicializa as cores
        Fmt.set_scr(scr)  # Define o scr como global

        # Exemplo de uso da função escrever
        while True:
            self.update_avaliable_quests()
            self.update_new()
            self.show_items()
            self.draw_warnings()
            self.generate_graph(scr)

            if len(self.input_layer) > 0 and self.input_layer[0].enable:
                value = self.input_layer[0].get_input()
            else:
                value = scr.getch()

            if value == ord("Q"):
                break
            elif value == ord("q") or value == 27:
                self.add_input(Input().addt("Saindo do aplicativo").set_exit_key("Q").add_extra_exit("q").warning())
            elif value == curses.KEY_UP or value == ord("w"):
                self.index_selected = max(0, self.index_selected - 1)
            elif value == curses.KEY_DOWN or value == ord("s"):
                self.index_selected = min(len(self.items) - 1, self.index_selected + 1)
            elif value == curses.KEY_LEFT or value == ord("a"):
                self.arrow_left()
            elif value == curses.KEY_RIGHT or value == ord("d"):
                self.arrow_right()
            elif value == ord("H"):
                self.flags_toggle("help_bar")
            elif value == ord("S"):
                self.flags_toggle(Flags.skills_bar)
                self.check_disable_flags()
            elif value == ord("F"):
                self.flags_toggle(Flags.flags_bar)
                self.check_disable_skills()
            elif value == ord("h"):
                self.show_help()
            elif value == ord("C"):
                self.flags_toggle(Flags.count)
                self.send_ligado("Mostrando contagem de tarefas feitas ", Flags.count, "C")
            elif value == ord("X"):
                self.flags_toggle(Flags.xp)
                self.send_ligado("Mostrando xp em missões e tarefas ", Flags.xp, "X")
            elif value == ord("P"):
                self.flags_toggle(Flags.percent)
                self.send_ligado("Mostrando percentuais ", Flags.percent, "P")
            elif value == ord("G"):
                self.flags_toggle(Flags.goals)
                self.send_ligado("Mostrando metas para conclusão de Missão ", Flags.goals, "G")
            elif value == ord("D"):
                self.flags_toggle(Flags.down)
                self.send_ligado("Mostrando caminho das tarefas baixadas ", Flags.down, "D")
            elif value == ord("r"):
                self.flags_toggle(Flags.group_bar)
                self.send_ligado("Mostrando barra de porcentagem nos Grupos ", Flags.group_bar, "r")
            elif value == ord("t"):
                self.flags_toggle(Flags.quest_bar)
                self.send_ligado("Mostrando barra de porcentagem nas Missões ", Flags.quest_bar, "t")
            elif value == ord("A"):
                self.flags_toggle(Flags.admin)
                self.send_ligado("Desbloqueando acesso a todas as missões ", Flags.admin, "A")
                self.reload_options()
            elif value == ord(">"):
                self.process_expand()
            elif value == ord("<"):
                self.process_collapse()
            elif value == ord(" ") or value == ord("\n"):
                self.toggle()
            elif value == ord("o"):
                self.open_link()
            elif value == ord("l"):
                self.set_language()
            elif value == ord("g"):
                self.process_down()
            elif value == ord("M"):
                self.mass_mark()
            elif value >= ord("0") and value <= ord("9"):
                self.set_grade(value)
            self.save_to_json()
        
            if self.first_loop:
                self.first_loop = False

    def play(self, graph_ext: str):
        self.graph_ext = graph_ext
        while True:
            output = curses.wrapper(self.main)
            if output is None:
                return
            else:
                output()

