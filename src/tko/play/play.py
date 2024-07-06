from ..game.game import Game
from ..game.cluster import Cluster
from ..game.quest import Quest
from ..game.task import Task
from ..game.xp import XP
from ..game.graph import Graph

from typing import List, Any
from ..settings.settings import RepSettings, GeralSettings
from ..down import Down
from ..util.symbols import symbols
from ..util.sentence import Sentence
from .style import Style
from .fmt import Fmt
from .frame import Frame
from .floating import Floating
import webbrowser

import os
import curses


class Entry:
    def __init__(self, obj: Any, sentence: Sentence):
        self.obj = obj
        self.sentence = sentence

    def get(self):
        return self.sentence


class Util:
    @staticmethod
    def build_bar(text: str, percent: float, length: int, fmt_true: str = "/kC",
                  fmt_false: str = "/kY") -> Sentence:
        prefix = (length - len(text)) // 2
        suffix = length - len(text) - prefix
        text = " " * prefix + text + " " * suffix
        xp_bar = Sentence()
        total = length
        full_line = text
        done_len = int(percent * total)
        xp_bar.addf(fmt_true, full_line[:done_len]).addf(fmt_false, full_line[done_len:])
        return xp_bar

    @staticmethod
    def test_color(scr):
        fg = "rgbymcwk"
        bg = " RGBYMCWK"
        scr.erase()
        for _l in range(8):
            for _c in range(9):
                cor = fg[_l] + bg[_c]
                Fmt.write(3 * _l, 5 * _c, Sentence().addf(cor, f" {cor} "))

        scr.refresh()
        scr.getch()

    @staticmethod
    def build_list_sentence(items: List[str]) -> Sentence:
        _help = Sentence()
        try:
            for x in items:
                label, key = x.split("[")
                key = "[" + key
                _help.addf("/", label).addt(key).addt(" ")
        except ValueError:
            raise ValueError("Desempacotando mensagens")
        _help.data.pop()

        return _help


class Const:
    key_left = "a"
    key_right = "d"
    key_down_task = "g"
    key_help = "h"
    key_set_lang = "l"
    key_open_link = "o"
    key_quit = "q"
    key_down = "s"
    key_up = "w"
    key_mass_toggle = "T"

    key_show_dots = "."
    tog_show_dots = "!dots"

    key_show_count = "C"
    tog_show_count = "count"

    key_show_down = "D"
    tog_show_down = "down"

    key_flags_bar = "F"
    tog_flags_bar = "flags_bar"

    key_group_prog = "G"
    tog_group_prog = "!group_bar"

    key_help_bar = "H"
    tog_help_bar = "help_bar"

    key_show_minimum = "M"
    tog_show_minimum = "minimum"

    key_show_opt = "O"
    tog_show_opt = "optional"

    key_show_percent = "P"
    tog_show_percent = "percent"

    key_skills_bar = "S"
    tog_skills_bar = "skills_bar"

    key_quest_bar = "Q"
    tog_quest_bar = "!quest_bar"

    key_show_xp = "X"
    tog_show_xp = "xp"

    key_admin = "A"
    tog_admin = "admin"


class Play:
    cluster_prefix = "'"

    def __init__(self, local: GeralSettings, game: Game, rep: RepSettings, rep_alias: str, fn_save):
        self.fn_save = fn_save
        self.local = local
        self.rep_alias = rep_alias
        self.rep = rep
        self.exit = False
        self.input_layer: List[Floating] = []

        self.flags = self.rep.get(RepSettings.flags)
        self.new_items: List[str] = self.rep.get(RepSettings.new_items)
        self.expanded: List[str] = self.rep.get(RepSettings.expanded)


        self.game: Game = game

        tasks = self.rep.get(RepSettings.tasks)
        for key, grade in tasks.items():
            if key in self.game.tasks:
                self.game.tasks[key].set_grade(int(grade))

        self.available_quests: List[Quest] = []  # available quests
        self.available_clusters: List[Cluster] = []  # available clusters

        self.index_selected = 0
        self.index_begin = 0

        self.items: List[Entry] = []

        self.first_loop = True
        self.graph_ext = ""

        self.max_title = 0


        self.help_base = [f"Quit[{Const.key_quit}]", f"Help[{Const.key_help}]", "Move[wasd]", "Mark[enter]"]
        self.help_extra = [f"OpenLink[{Const.key_open_link}]", f"GetTask[{Const.key_down_task}]", "Grade[0-9]",
                           f"Lang[{Const.key_set_lang}]", "Expand[>]", "Collapse[<]",
                           f"MassMark[{Const.key_mass_toggle}]"]

    def save_to_json(self):
        self.rep.set(RepSettings.flags, self.flags)
        self.rep.set(RepSettings.expanded, self.expanded)
        self.rep.set(RepSettings.new_items, self.new_items)
        tasks = {}
        for t in self.game.tasks.values():
            if t.grade != 0:
                tasks[t.key] = str(t.grade)
        self.rep.set(RepSettings.tasks, tasks)
        self.rep.set(RepSettings.flags, self.flags)

        self.fn_save()

    def update_available_quests(self):
        old_quests = [q for q in self.available_quests]
        old_clusters = [c for c in self.available_clusters]
        if self.flags_on(Const.tog_admin):
            self.available_quests = list(self.game.quests.values())
            self.available_clusters = [c for c  in self.game.clusters]
        else:
            self.available_quests = self.game.get_reachable_quests()
            self.available_clusters = []
            for c in self.game.clusters:
                if any([q in self.available_quests for q in c.quests]):
                    self.available_clusters.append(c)

        removed_clusters = [c for c in old_clusters if c not in self.available_clusters]
        for c in removed_clusters:
            if c.key in self.expanded:
                self.expanded.remove(c.key)
        removed_quests = [q for q in old_quests if q not in self.available_quests]
        for q in removed_quests:
            if q.key in self.expanded:
                self.expanded.remove(q.key)

        added_clusters = [c for c in self.available_clusters if c not in old_clusters]
        added_quests = [q for q in self.available_quests if q not in old_quests]

        for c in added_clusters:
            if c.key not in self.new_items:
                self.new_items.append(c.key)
        for q in added_quests:
            if q.key not in self.new_items:
                self.new_items.append(q.key)

    def str_task(self, in_focus: bool, t: Task, lig_cluster: str, lig_quest: str, min_value=1) -> Sentence:
        output = Sentence()
        output.addt(" " + lig_cluster + " " + lig_quest) \
            .concat(t.get_grade_symbol(min_value)) \
            .addt(" ")

        color = ""
        if self.flags_on(Const.tog_show_opt) and t.opt:
            color = Style.opt_task + color
        if in_focus:
            color = Style.focus + color
        output.addf(color, t.title)

        if self.flags_on(Const.tog_show_down):
            path = os.path.join(self.local.rootdir, self.rep_alias, t.key)
            if os.path.isdir(path):
                output.addt(" ").addf("y", f"[{path}]")

        if self.flags_on(Const.tog_show_xp):
            xp = ""
            for s, v in t.skills.items():
                xp += f" +{s}:{v}"
            output.addf(Style.skills, xp)
        return output

    def update_max_title(self):
        items = []
        for c in self.available_clusters:
            items.append(len(c.title))
            if c.key in self.expanded:
                for q in c.quests:
                    items.append(len(q.title) + 2)
                    # if q.key in self.expanded:
                    #     for t in q.get_tasks():
                    #         items.append(len(t.title) + 4)
        self.max_title = max(items)

    def str_quest(self, in_focus: bool, q: Quest, lig: str) -> Sentence:
        con = "━─" if q.key not in self.expanded else "─┯"
        output: Sentence = Sentence().addt(" " + lig + con + " ")

        color = ""
        if self.flags_on(Const.tog_show_opt) and q.opt:
            color = Style.opt_quest + color
        if in_focus:
            color = Style.focus + color

        title = q.title
        if self.flags_on(Const.tog_show_dots):
            title = title.ljust(self.max_title - 2, ".")
        if self.flags_on(Const.tog_quest_bar):
            done = Style.progress_done + color
            todo = Style.progress_todo + color
            output.concat(Util.build_bar(title, q.get_percent() / 100, len(title), done, todo))
        else:
            output.addf(color, title)

        if self.flags_on(Const.tog_show_count):
            if self.flags_on(Const.tog_show_percent):
                output.addt(" ").concat(q.get_resume_by_percent())
            else:
                output.addt(" ").concat(q.get_resume_by_tasks())
    

        if self.flags_on(Const.tog_show_minimum):
            output.addt(" ").concat(q.get_requirement())

        if self.flags_on(Const.tog_show_xp):
            xp = ""
            for s, v in q.skills.items():
                xp += f" +{s}:{v}"
            output.addf(Style.skills, " " + xp)

        if q.key in self.new_items:
            output.addf(Style.new, " [new]")

        return output

    def str_cluster(self, in_focus: bool, cluster: Cluster) -> Sentence:
        output: Sentence = Sentence()
        opening = "━─"
        if cluster.key in self.expanded:
            opening = "─┯"
        output.addt(opening + " ")
        color = Style.cluster_title
        if in_focus:
            color += Style.focus + color
        title = cluster.title
        if self.flags_on(Const.tog_show_dots):
            title = cluster.title.ljust(self.max_title, ".")

        if self.flags_on(Const.tog_group_prog):
            done = Style.progress_done + color
            todo = Style.progress_todo + color
            output.concat(Util.build_bar(title, cluster.get_percent() / 100, len(title), done, todo))
        else:
            output.addf(color, title)

        if self.flags_on(Const.tog_show_count):
            if self.flags_on(Const.tog_show_percent):
                output.addt(" ").concat(cluster.get_resume_by_percent())
            else:
                output.addt(" ").concat(cluster.get_resume_by_quests())
        if cluster.key in self.new_items:
            output.addf(Style.new, " [new]")

        return output

    def get_avaliable_quests_from_cluster(self, cluster: Cluster) -> List[Quest]:
        return [q for q in cluster.quests if q in self.available_quests]

    def reload_options(self):
        self.update_max_title()
        index = 0
        self.items = []
        for cluster in self.available_clusters:
            quests = self.get_avaliable_quests_from_cluster(cluster)
            sentence = self.str_cluster(self.index_selected == index, cluster)
            self.items.append(Entry(cluster, sentence))
            index += 1

            if cluster.key not in self.expanded:  # va para proximo cluster
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
            down_frame = Floating().warning().set_header(Sentence().addt(" Baixando tarefa "))
            down_frame.addt(f"tko down {self.rep_alias} {task.key} -l {ext}")
            self.add_input(down_frame)

            def fnprint(text):
                down_frame.addt(text)
                down_frame.draw()
                Fmt.refresh()

            Down.download_problem(rootdir, self.rep_alias, task.key, ext, fnprint)
        else:
            if isinstance(obj, Quest):
                self.add_input(Floating().addt("Essa é uma missão").addt("você só pode baixar tarefas").error())
            elif isinstance(obj, Cluster):
                self.add_input(Floating().addt("Esse é um grupo").addt("você só pode baixar tarefas").error())
            else:
                self.add_input(Floating().addt("Essa não é uma tarefa de código").error())

    def set_rootdir(self):
        def chama(value):
            if value == "yes":
                self.local.rootdir = os.getcwd()
                self.fn_save()
                self.add_input(Floating()
                               .addt("Diretório raiz definido como ")
                               .addt("  " + self.local.rootdir)
                               .addt("Você pode alterar o diretório raiz navegando para o")
                               .addt("diretório desejado e executando o comando")
                               .addt("  tko config --root")
                               .addt("")
                               .set_exit_fn(self.set_language)
                               .warning())
            else:
                self.add_input(Floating()
                               .addt("Navague para o diretório desejado e execute o comando")
                               .addt("  tko config --root")
                               .addt("ou rode o tko play novamente na pasta desejada").warning())

        self.add_input(Floating().addt("Diretório raiz para o tko ainda não foi definido")
                       .addt("Você deseja utilizar o diretório atual")
                       .addt(os.getcwd())
                       .addt("como raiz para o repositório de " + self.rep_alias + "?")
                       .set_options(["yes", "no"])
                       .answer(chama))

    def set_language(self):

        def back(value):
            self.rep.lang = value
            self.fn_save()
            self.add_input(Floating()
                           .addt("Linguagem alterada para " + value)
                           .addt("Você pode mudar a linguagem")
                            .addt("de programação apertando")
                           .adds(Sentence().addf("G", "l"))
                           .warning())

        self.add_input(Floating()
                       .addt("   Escolha a extensão")
                       .addt(" default para os rascunhos")
                       .addt("")
                       .addt(" Selecione e tecle enter")
                       .set_options(["c", "cpp", "py", "ts", "js", "java", "hs"])
                       .answer(back))

    def process_down(self):

        if self.local.rootdir == "":
            self.set_rootdir()
            return

        if self.rep.lang == "":
            self.set_language()
            return

        rootdir = os.path.relpath(os.path.join(self.local.rootdir, self.rep_alias))
        obj = self.items[self.index_selected].obj
        self.down_task(rootdir, obj, self.rep.lang)

    def process_collapse(self):
        quest_keys = [q.key for q in self.available_quests]
        if any([q in self.expanded for q in quest_keys]):
            self.expanded = [key for key in self.expanded if key not in quest_keys]
        else:
            self.expanded = []

    def process_expand(self):
        # if any cluster outside expanded
        expand_clusters = False
        for c in self.available_clusters:
            if c.key not in self.expanded:
                expand_clusters = True
        if expand_clusters:
            for c in self.available_clusters:
                if c.key not in self.expanded:
                    self.expanded.append(c.key)
        else:
            for q in self.available_quests:
                if q.key not in self.expanded:
                    self.expanded.append(q.key)

    def flags_toggle(self, token):
        if token in self.flags:
            self.flags.remove(token)
        else:
            self.flags.append(token)

    @staticmethod
    def checkbox(value) -> Sentence:
        return Sentence().addf(Style.check, symbols.opcheck) if value else Sentence().addf(Style.uncheck,
                                                                                           symbols.opuncheck)

    def build_bar_links(self) -> str:
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Task):
            link = obj.link
            if link:
                return link
        return ""

    def flags_on(self, value: str):
        if not value.startswith("!"):
            return value in self.flags
        return value not in self.flags

    def flags_color(self, flag: str) -> str:
        if self.flags_on(flag):
            return Style.flags_true
        return Style.flags_false

    def show_main_bar(self, frame: Frame):
        frame.set_header(Sentence().addt("{").addf("/", f"Tarefas lang:{self.rep.lang}").addt("}"))
        frame.set_footer(Sentence().addt("{" + self.build_bar_links() + "}"))
        frame.draw()

        dy, dx = frame.get_inner()
        y = 0
        if len(self.items) < dy:
            self.index_begin = 0
        else:
            if self.index_selected < self.index_begin:  # subiu na tela
                self.index_begin = self.index_selected
            elif self.index_selected >= dy + self.index_begin:  # desceu na tela
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
        if self.flags_on(Const.tog_show_percent):
            text = f" Total:{total_perc}%"
        else:
            text = f" Total:{xp.get_xp_total_obtained()}"

        total_bar = Util.build_bar(text, total_perc / 100, dx - 2, "/kC", "/kM")
        frame_xp.set_header(Sentence().addt("{").addf("/", "Skills").addt("}"), "^")
        frame_xp.set_footer(Sentence().concat(total_bar), "^")
        frame_xp.draw()

        total, obt = self.game.get_skills_resume()
        index = 0
        for skill, value in total.items():
            if self.flags_on(Const.tog_show_percent):
                text = f"{skill}:{int(100 * obt[skill] / value)}%"
            else:
                text = f"{skill}:{obt[skill]}/{value}"

            perc = obt[skill] / value
            skill_bar = Util.build_bar(text, perc, dx - 2, "/kC", "/kR")
            frame_xp.write(index, 1, skill_bar)
            index += 2

    def show_flags_bar(self, frame: Frame):
        frame.set_header(Sentence().addt("{").addf("/", "Flags").addt("}"), "^")
        frame.draw()

        def add_flag(_flag, _text, _key):
            color = self.flags_color(_flag)
            if self.flags_on(_flag):
                s = Sentence().addf(color + "/", _text).addf(color, (8 - len(_text)) * " ").addf("", _key)
            else:
                s = Sentence().addf("", _key).addf(color, (8 - len(_text)) * " ").addf(color + "/", _text)
            frame.print(1, s)

        add_flag(Const.tog_show_percent, "Percent", f"[{Const.key_show_percent}]")
        add_flag(Const.tog_show_count, "Count", f"[{Const.key_show_count}]")
        add_flag(Const.tog_show_minimum, "Minimum", f"[{Const.key_show_minimum}]")
        add_flag(Const.tog_show_xp, "XP", f"[{Const.key_show_xp}]")
        add_flag(Const.tog_show_down, "Down", f"[{Const.key_show_down}]")
        add_flag(Const.tog_show_dots, "Dots", f"[{Const.key_show_dots}]")
        add_flag(Const.tog_group_prog, "GroupBar", f"[{Const.key_group_prog}]")
        add_flag(Const.tog_quest_bar, "QuestBar", f"[{Const.key_quest_bar}]")
        add_flag(Const.tog_admin, "Admin", f"[{Const.key_admin}]")

    def show_help(self):
        _help: Floating = Floating().warning().ljust()
        self.add_input(_help)
        _help.set_header(Sentence().addf("/", " Help "))
        _help.addt("Barras alternáveis")
        _help.adds(
            Sentence().addt("  ").addf("", f"{Const.key_flags_bar}").addt(" - Mostrar ou esconder a barra de flags"))
        _help.adds(
            Sentence().addt("  ").addf("", f"{Const.key_help_bar}").addt(" - Mostrar ou esconder a barra de ajuda"))
        _help.adds(
            Sentence().addt("  ").addf("", f"{Const.key_skills_bar}").addt(" - Mostrar ou esconder a barra de skills"))
        _help.addt("")
        _help.addt("Controles")
        _help.addt("  setas ou wasd   - Para navegar entre os elementos")
        _help.addt("  enter ou espaço - Marcar ou desmarcar, expandir ou contrair")
        _help.addt("  0 a 9 - Definir a nota parcial para uma tarefa")
        _help.addt(f"      {Const.key_open_link} - Abrir tarefa em uma aba do browser")
        _help.addt(f"      {Const.key_down_task} - Baixar um tarefa de código para seu dispositivo")
        _help.addt("")
        _help.addt("Flags")
        _help.addt("  Muda a forma de exibição dos elementos")
        _help.addt("")
        _help.addt("Extra")
        _help.addt(f"  {Const.key_set_lang} - Mudar a linguagem de download dos rascunhos")

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
            if not self.input_layer[0]._enable:
                self.input_layer = self.input_layer[1:]

        if len(self.input_layer) > 0 and self.input_layer[0]._enable:
            self.input_layer[0].draw()

    def show_bottom_bar(self, frame: Frame):
        _help = Util.build_list_sentence(self.help_extra)
        for s in _help:
            if s.text.startswith("["):
                s.fmt = ""
            elif not s.text.startswith(" "):
                s.fmt = "B"
        dx = frame.get_dx()
        # help.trim_spaces(dx)
        _help.trim_alfa(dx)
        _help.trim_end(dx)
        frame.set_header(_help, "^")
        # frame.set_border_square()
        frame.set_border_none()
        frame.draw()

    def show_top_bar(self, frame: Frame) -> None:
        _help = Util.build_list_sentence(self.help_base)
        dx = frame.get_dx()
        _help.trim_alfa(dx)
        _help.trim_end(dx)
        for s in _help:
            if s.text.startswith("["):
                s.fmt = ""
            elif not s.text.startswith(" "):
                s.fmt = "B"
        frame.set_footer(_help, "^")
        frame.draw()

        content = Sentence().addt(" ")
        content.addf("C", f"({self.rep_alias.upper()})").addt(" ")

        def add_flag(flag, _text, _key):
            color = self.flags_color(flag)
            if self.flags_on(flag):
                content.addf(color + "/", _text).addf(color, _key).addt(" ")
            else:
                content.addf(color, _key).addf(color + "/", _text).addt(" ")

        add_flag(Const.tog_flags_bar, "FlagsBar", f"[{Const.key_flags_bar}]")
        add_flag(Const.tog_help_bar, "HelpBar", f"[{Const.key_help_bar}]")
        add_flag(Const.tog_skills_bar, "SkillsBar", f"[{Const.key_skills_bar}]")

        for s in content:
            if s.text.startswith("["):
                s.fmt = ""

        xp = XP(self.game)

        if xp.get_xp_total_obtained() == xp.get_xp_total_available():
            text = "Você atingiu o máximo de xp!"
            percent = 100.0
        else:
            if self.flags_on(Const.tog_show_percent):
                text = f"L:{xp.get_level()} XP:{int(100 * xp.get_xp_level_current() / xp.get_xp_level_needed())}%"
            else:
                text = f"L:{xp.get_level()} XP:{xp.get_xp_level_current()}/{xp.get_xp_level_needed()}"
            percent = float(xp.get_xp_level_current()) / float(xp.get_xp_level_needed())
        size = max(15, dx - content.len() - 1)
        xp_bar = Util.build_bar(text, percent, size).addt(" ")

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
        main_sy = lines  # size em y avaliable

        top_y = -1
        top_dy = 3
        frame_top = Frame(top_y, 0).set_size(3, main_sx)
        self.show_top_bar(frame_top)

        bottom_sy = 0
        if self.flags_on(Const.tog_help_bar):
            bottom_sy = 1
            frame_bottom = Frame(lines - 1, 0).set_size(3, main_sx)
            self.show_bottom_bar(frame_bottom)

        mid_y = top_y + top_dy
        mid_sy = main_sy - (top_y + top_dy + bottom_sy)

        skills_sx = 0
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
        reachable: List[str] = [q.key for q in self.available_quests]
        counts = {}
        for q in self.game.quests.values():
            done = len([t for t in q.get_tasks() if t.is_complete()])
            init = len([t for t in q.get_tasks() if t.in_progress()])
            todo = len([t for t in q.get_tasks() if t.not_started()])
            counts[q.key] = f"{done} / {done + init + todo}\n{q.get_percent()}%"

        mark_opt = self.flags_on(Const.tog_show_opt)
        Graph(self.game).set_opt(mark_opt).set_reachable(reachable).set_counts(counts).set_graph_ext(
            self.graph_ext).generate()
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
            self.add_input(Floating().set_header(Sentence().addf("/", " Abrindo link ")).addt(task.link).warning())
        elif isinstance(obj, Quest):
            self.add_input(
                Floating().addt("Essa é uma missão").addt("você só pode abrir o link").addt("de tarefas").error())
        else:
            self.add_input(
                Floating().addt("Esse é um grupo").addt("você só pode abrir o link").addt("de tarefas").error())

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

    def add_input(self, value: Floating):
        self.input_layer.append(value)

    def check_disable_flags(self):
        lines, cols = Fmt.get_size()
        if cols < 50:
            if self.flags_on("flags_bar"):
                self.flags_toggle("flags_bar")

    def check_disable_skills(self):
        lines, cols = Fmt.get_size()
        if cols < 50:
            if self.flags_on(Const.tog_skills_bar):
                self.flags_toggle("skills_bar")

    def send_input_msg(self, msg: str, flag: str, key: str):
        f = Floating("v").warning()
        f.addt(msg)
        if self.flags_on(flag):
            f.adds(Sentence().addf("G", "ligado"))
        else:
            f.adds(Sentence().addf("R", "desligado"))
        self.add_input(f)

    def set_exit(self):
        self.exit = True

    def main(self, scr):
        # scr.nodelay(True)
        curses.curs_set(0)  # Esconde o cursor
        Fmt.init_colors()  # Inicializa as cores
        Fmt.set_scr(scr)  # Define o scr como global

        # Exemplo de uso da função escrever
        while not self.exit:
            self.update_available_quests()
            self.update_new()
            self.show_items()
            self.draw_warnings()
            self.generate_graph(scr)

            if len(self.input_layer) > 0 and self.input_layer[0]._enable:
                value = self.input_layer[0].get_input()
            else:
                value = scr.getch()

            if value == ord(Const.key_quit) or value == 27:
                self.add_input(
                    Floating("v").addt("Saindo do aplicativo").set_exit_fn(self.set_exit).warning())
            elif value == curses.KEY_UP or value == ord(Const.key_up):
                self.index_selected = max(0, self.index_selected - 1)
            elif value == curses.KEY_DOWN or value == ord(Const.key_down):
                self.index_selected = min(len(self.items) - 1, self.index_selected + 1)
            elif value == curses.KEY_LEFT or value == ord(Const.key_left):
                self.arrow_left()
            elif value == curses.KEY_RIGHT or value == ord(Const.key_right):
                self.arrow_right()
            elif value == ord(Const.key_help_bar):
                self.flags_toggle(Const.tog_help_bar)
            elif value == ord(Const.key_skills_bar):
                self.flags_toggle(Const.tog_skills_bar)
                self.check_disable_flags()
            elif value == ord(Const.key_flags_bar):
                self.flags_toggle(Const.tog_flags_bar)
                self.check_disable_skills()
            elif value == ord(Const.key_help):
                self.show_help()
            elif value == ord(Const.key_show_count):
                self.flags_toggle(Const.tog_show_count)
                self.send_input_msg("Mostrando contagem de tarefas feitas", Const.tog_show_count, Const.key_show_count)
            elif value == ord(Const.key_show_xp):
                self.flags_toggle(Const.tog_show_xp)
                self.send_input_msg("Mostrando xp em missões e tarefas", Const.tog_show_xp, Const.key_show_xp)
            elif value == ord(Const.key_show_percent):
                self.flags_toggle(Const.tog_show_percent)
                self.send_input_msg("Mostrando percentuais ", Const.tog_show_percent, Const.key_show_percent)
            elif value == ord(Const.key_show_minimum):
                self.flags_toggle(Const.tog_show_minimum)
                self.send_input_msg("Mostrando mínimo valor para conclusão de Missão", Const.tog_show_minimum,
                                 Const.key_show_minimum)
            elif value == ord(Const.key_show_down):
                self.flags_toggle(Const.tog_show_down)
                self.send_input_msg("Mostrando caminho das tarefas baixadas", Const.tog_show_down, Const.key_show_down)
            elif value == ord(Const.key_group_prog):
                self.flags_toggle(Const.tog_group_prog)
                self.send_input_msg("Mostrando barra de porcentagem nos Grupos", Const.tog_group_prog,
                                 Const.key_group_prog)
            elif value == ord(Const.key_quest_bar):
                self.flags_toggle(Const.tog_quest_bar)
                self.send_input_msg("Mostrando barra de porcentagem nas Missões", Const.tog_quest_bar,
                                 Const.key_quest_bar)
            elif value == ord(Const.key_show_dots):
                self.flags_toggle(Const.tog_show_dots)
                self.send_input_msg("Fazendo o preenchimento de Missões e Grupos", Const.tog_show_dots,
                                 Const.key_show_dots)

            elif value == ord(Const.key_admin):
                self.flags_toggle(Const.tog_admin)
                self.send_input_msg("Desbloqueando acesso a todas as missões", Const.tog_admin, Const.key_admin)
                self.reload_options()
            elif value == ord(">"):
                self.process_expand()
            elif value == ord("<"):
                self.process_collapse()
            elif value == ord(" ") or value == ord("\n"):
                self.toggle()
            elif value == ord(Const.key_open_link):
                self.open_link()
            elif value == ord(Const.key_set_lang):
                self.set_language()
            elif value == ord(Const.key_down_task):
                self.process_down()
            elif value == ord(Const.key_mass_toggle):
                self.mass_mark()
            elif ord("0") <= value <= ord("9"):
                self.set_grade(value)
            self.save_to_json()

            if self.first_loop:
                self.first_loop = False

    def play(self, graph_ext: str):
        self.graph_ext = graph_ext
        try:
            output = curses.wrapper(self.main)
            if output is None:
                return
        except Exception as e:
            print(e)
