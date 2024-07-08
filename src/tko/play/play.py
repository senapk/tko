from ..game.game import Game
from ..game.cluster import Cluster
from ..game.quest import Quest
from ..game.task import Task
from ..game.xp import XP
from ..game.graph import Graph

from typing import List, Any, Dict
from ..settings.settings import RepSettings, GeralSettings
from ..down import Down
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


class Flag:
    def __init__(self):
        self._name: str = ""
        self._text: str = ""  # description
        self._char: str = ""
        self._values: List[str] = ["0", "1"]
        self._index: int = 0
        self._location: str = ""
        self._bool = True  # many options

    def name(self, _name):
        self._name = _name
        return self

    def text(self, _text):
        self._text = _text
        return self

    def char(self, _key):
        self._char = _key
        return self

    def values(self, _values: List[str]):
        self._values = _values
        return self

    def index(self, _index):
        self._index = _index
        return self

    def location(self, value: str):
        self._location = value
        return self

    def toggle(self):
        self._index = (self._index + 1) % len(self._values)
        return self

    def many(self):
        self._bool = False
        return self
    
    def bool(self):
        self._bool = True
        return self
    
    def is_bool(self):
        return self._bool

    def get_location(self) -> str:
        return self._location

    def get_value(self) -> Any:
        return self._values[self._index]

    def is_true(self) -> bool:
        return self.get_value() == "1"

    def get_name(self) -> str:
        return self._name

    def get_description(self) -> str:
        return self._text

    def get_char(self) -> str:
        return self._char

    def get_index(self) -> int:
        return self._index

    def get_color(self) -> str:
        if self.get_value() == "1":
            return Flags.flag_on.get_value()
        return Flags.flag_off.get_value()

    def get_toggle_sentence(self, pad: int = 0) -> Sentence:
        if not self._bool:
            name = Sentence().addf(self.get_value(), f"{self._name}".ljust(pad))
            value = Sentence().addt(f"[{self.get_char()}]").addt(f"{self.get_value()}".rjust(2)).addt(" ").concat(name)
            return value
            
        char = self.get_char()
        text = self.get_name()
        color = self.get_color()
        extra = Sentence()
        if pad > 0:
            extra.addf(color, (pad - len(text)) * " ")
        visual = "━─"
        if self.is_true():
            visual = "─━"
        value = Sentence().addt(f"[{char}]").addf(color, f"{visual} ").addf(color + "/", text).concat(extra)
        return value
    

class Flags:
    count = Flag().name("Count").char("C").text("Mostra a contagem de tarefas").location("left")
    down = Flag().name("Down").char("D").text("Mostra o caminho para a tarefa baixadas").location("left")
    minimum = Flag().name("Minimum").char("M").text("Mostra a nota mínima para a tarefa").location("left")
    opt = Flag().name("Opt").char("O").text("Mostra tarefas opcionais").location("left")
    xp = Flag().name("Xp").char("X").text("Mostra a xp obtida").location("left")
    percent = Flag().name("Percent").char("P").text("Mostra a porcentagem de tarefas").location("left")
    admin = Flag().name("Admin").char("A").text("Mostra todas as missões e grupos").location("left")

    dots = Flag().name("Dots").char(".").values(["1", "0"]).text("Mostra o preenchimento com pontos").location("left")
    group_prog = Flag().name("Group").char("G").values(["1", "0"]).text("Mostra a barra de progresso dos grupos").location("left")
    quest_prog = Flag().name("Quest").char("Q").values(["1", "0"]).text("Mostra a barra de progresso das missões").location("left")

    help_bar = Flag().name("HelpBar").char("H").values(["1", "0"]).text("Mostra a barra de ajuda").location("top")
    skills_bar = Flag().name("SkillsBar").char("S").values(["1", "0"]).text("Mostra a barra de skills").location("top")
    flags_bar = Flag().name("FlagsBar").char("F").values(["1", "0"]).text("Mostra a barra de flags").location("top")

    focus     = Flag().name("Focus").char("z").values(["R", "B", "G", "Y", "wK", "kW"]).text("Cor do item em foco").many().location("left")
    prog_done = Flag().name("ProgDone").char("x").values(["g", "b", "c", "k", "w"]).text("Progresso Done").many().location("left")
    prog_todo = Flag().name("ProgTodo").char("c").values(["y", "m", "r", "k", "w"]).text("Progresso Todo").many().location("left")
    flag_on   = Flag().name("FlagTrue").char("v").values(["G", "W", "B", "C", "wK", "kW"]).text("Flag True").many().location("left")
    flag_off  = Flag().name("FlagFalse").char("b").values(["Y", "R", "M", "wK", "kW"]).text("Flag False").many().location("left")
    cmds      = Flag().name("Cmds").char("n").values(["B", "C", "M", "Y", "wK", "kW"]).text("CMDS").many().location("left")
    skill_done = Flag().name("SkillDone").char("y").values(["G", "B", "C", "wK", "kW"]).text("Skill Done").many().location("left")
    skill_todo = Flag().name("SkillTodo").char("u").values(["Y", "R", "M", "wK", "kW"]).text("Skill Todo").many().location("left")
    main_done = Flag().name("MainDone").char("i").values(["B", "G", "C", "wK", "kW"]).text("Main Done").many().location("left")
    main_todo = Flag().name("MainTodo").char("p").values(["M", "R", "Y", "wK", "kW"]).text("Main Todo").many().location("left")


class FlagsMan:
    def __init__(self, data: Dict[str, int]):
        self.flags: Dict[str, Flag] = {}
        self.left: List[Flag] = []
        self.top: List[Flag] = []

        for flag in Flags.__dict__.values():
            if isinstance(flag, Flag):
                self.flags[flag.get_name()] = flag
                if flag.get_location() == "left":
                    self.left.append(flag)
                elif flag.get_location() == "top":
                    self.top.append(flag)

        for key, _index in data.items():
            if key in self.flags:
                self.flags[key].index(_index)

    def get_data(self) -> Dict[str, int]:
        data = {}
        for name, flag in self.flags.items():
            data[name] = flag.get_index()
        return data


class Play:
    cluster_prefix = "'"

    def __init__(self, local: GeralSettings, game: Game, rep: RepSettings, rep_alias: str, fn_save):
        self.fn_save = fn_save
        self.local = local
        self.rep_alias = rep_alias
        self.rep = rep
        self.exit = False
        self.input_layer: List[Floating] = []

        self.new_items: List[str] = self.rep.get(RepSettings.new_items)
        self.expanded: List[str] = self.rep.get(RepSettings.expanded)
        self.flagsman = FlagsMan(self.rep.get(RepSettings.flags))
        self.rep.lang = self.rep.get(RepSettings.lang)

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

        self.help_base = [f"Quit[{self.Key.quit}]", f"Help[{self.Key.help}]", "Move[wasd]", "Mark[enter]"]
        self.help_extra = [f"OpenLink[{self.Key.open_link}]", f"GetTask[{self.Key.down_task}]", "Grade[0-9]",
                           f"Lang[{self.Key.set_lang}]", f"Expand[{self.Key.expand}]", f"Collapse[{self.Key.collapse}]",
                           f"MassMark[{self.Key.mass_toggle}]", f"ResetColors[{self.Key.reset}]"]

    def save_to_json(self):
        self.rep.set(RepSettings.expanded, self.expanded)
        self.rep.set(RepSettings.new_items, self.new_items)
        tasks = {}
        for t in self.game.tasks.values():
            if t.grade != 0:
                tasks[t.key] = str(t.grade)
        self.rep.set(RepSettings.tasks, tasks)
        self.rep.set(RepSettings.flags, self.flagsman.get_data())
        self.rep.set(RepSettings.lang, self.rep.lang)

        self.fn_save()

    def update_available_quests(self):
        old_quests = [q for q in self.available_quests]
        old_clusters = [c for c in self.available_clusters]
        if Flags.admin.is_true():
            self.available_quests = list(self.game.quests.values())
            self.available_clusters = [c for c in self.game.clusters]
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
        if Flags.opt.is_true() and t.opt:
            color = Style.opt_task + color
        if in_focus:
            color = Flags.focus.get_value() + color
        output.addf(color, t.title)

        if Flags.down.is_true():
            path = os.path.join(self.local.rootdir, self.rep_alias, t.key)
            if os.path.isdir(path):
                output.addt(" ").addf("y", f"[{path}]")

        if Flags.xp.is_true():
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
        if Flags.opt.is_true() and q.opt:
            color = Style.opt_quest + color
        if in_focus:
            color = Flags.focus.get_value() + color

        title = q.title
        if Flags.dots.is_true():
            title = title.ljust(self.max_title - 2, ".")
        if Flags.quest_prog.is_true():
            done = color + Flags.prog_done.get_value()
            todo = color + Flags.prog_todo.get_value()
            output.concat(Util.build_bar(title, q.get_percent() / 100, len(title), done, todo))
        else:
            output.addf(color, title)

        if Flags.count.is_true():
            if Flags.percent.is_true():
                output.addt(" ").concat(q.get_resume_by_percent())
            else:
                output.addt(" ").concat(q.get_resume_by_tasks())

        if Flags.minimum.is_true():
            output.addt(" ").concat(q.get_requirement())

        if Flags.xp.is_true():
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
            color += Flags.focus.get_value() + color
        title = cluster.title
        if Flags.dots.is_true():
            title = cluster.title.ljust(self.max_title, ".")

        if Flags.group_prog.is_true():
            done = color + Flags.prog_done.get_value()
            todo = color + Flags.prog_todo.get_value()
            output.concat(Util.build_bar(title, cluster.get_percent() / 100, len(title), done, todo))
        else:
            output.addf(color, title)

        if Flags.count.is_true():
            if Flags.percent.is_true():
                output.addt(" ").concat(cluster.get_resume_by_percent())
            else:
                output.addt(" ").concat(cluster.get_resume_by_quests())
        if cluster.key in self.new_items:
            output.addf(Style.new, " [new]")

        return output

    def get_available_quests_from_cluster(self, cluster: Cluster) -> List[Quest]:
        return [q for q in cluster.quests if q in self.available_quests]

    def reload_options(self):
        self.update_max_title()
        index = 0
        self.items = []
        for cluster in self.available_clusters:
            quests = self.get_available_quests_from_cluster(cluster)
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

    def build_bar_links(self) -> str:
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Task):
            link = obj.link
            if link:
                return link
        return ""

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
        if Flags.percent.is_true():
            text = f" Total:{total_perc}%"
        else:
            text = f" Total:{xp.get_xp_total_obtained()}"

        done = "/k" + Flags.main_done.get_value()
        todo = "/k" + Flags.main_todo.get_value()
        total_bar = Util.build_bar(text, total_perc / 100, dx - 2, done, todo)
        frame_xp.set_header(Sentence().addt("{").addf("/", "Skills").addt("}"), "^")
        frame_xp.set_footer(Sentence().concat(total_bar), "^")
        frame_xp.draw()

        total, obt = self.game.get_skills_resume()
        index = 0
        for skill, value in total.items():
            if Flags.percent.is_true():
                text = f"{skill}:{int(100 * obt[skill] / value)}%"
            else:
                text = f"{skill}:{obt[skill]}/{value}"

            perc = obt[skill] / value
            skill_bar = Util.build_bar(text, perc, dx - 2, "/k" + Flags.skill_done.get_value(), "/k" + Flags.skill_todo.get_value())
            frame_xp.write(index, 1, skill_bar)
            index += 2

    def show_flags_bar(self, frame: Frame):
        frame.set_header(Sentence().addt("{").addf("/", "Flags").addt("}"), "^")
        frame.draw()

        frame.print(0, Sentence().addt("-----VISUAL-----"))
        for flag in self.flagsman.left:
            if flag.is_bool():
                frame.print(0, flag.get_toggle_sentence(7))

        frame.print(0, Sentence().addt("-----CORES-----"))

        for flag in self.flagsman.left:
            if not flag.is_bool():
                frame.print(0, flag.get_toggle_sentence())


    def show_help(self):
        _help: Floating = Floating().warning().ljust()
        self.add_input(_help)
        _help.set_header(Sentence().addf("/", " Help "))
        _help.addt("Controles")
        _help.addt("  setas ou wasd   - Para navegar entre os elementos")
        _help.addt("  enter ou espaço - Marcar ou desmarcar, expandir ou contrair")
        _help.addt("  0 a 9 - Definir a nota parcial para uma tarefa")
        _help.addt(f"      {self.Key.open_link} - Abrir tarefa em uma aba do browser")
        _help.addt(f"      {self.Key.down_task} - Baixar um tarefa de código para seu dispositivo")
        _help.addt("")
        _help.addt("Flags")
        _help.addt("  Muda a forma de exibição dos elementos")
        _help.addt("")
        _help.addt("Extra")
        _help.addt(f"  {self.Key.set_lang} - Mudar a linguagem de download dos rascunhos")

    @staticmethod
    def disable_on_resize():
        lines, cols = Fmt.get_size()
        if cols < 50 and Flags.skills_bar.is_true() and Flags.flags_bar.is_true():
            Flags.skills_bar.toggle()
        elif cols < 30 and Flags.skills_bar.is_true():
            Flags.skills_bar.toggle()
        elif cols < 35 and Flags.flags_bar.is_true():
            Flags.flags_bar.toggle()

    def draw_warnings(self):
        if len(self.input_layer) > 0:
            if not self.input_layer[0].is_enable():
                self.input_layer = self.input_layer[1:]

        if len(self.input_layer) > 0 and self.input_layer[0].is_enable():
            self.input_layer[0].draw()

    def show_bottom_bar(self, frame: Frame):
        _help = Util.build_list_sentence(self.help_extra)
        for s in _help:
            if s.text.startswith("["):
                s.fmt = ""
            elif not s.text.startswith(" "):
                s.fmt = Flags.cmds.get_value()
        dx = frame.get_dx()
        # help.trim_spaces(dx)
        _help.trim_alfa(dx)
        _help.trim_end(dx)
        frame.set_header(_help, "^")
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
                s.fmt = Flags.cmds.get_value()
        frame.set_footer(_help, "^")
        frame.draw()

        content = Sentence().addt(" ")
        content.addf(Flags.cmds.get_value(), f"({self.rep_alias.upper()})").addt(" ")

        for f in self.flagsman.top:
            content.concat(f.get_toggle_sentence()).addt(" ")

        for s in content:
            if s.text.startswith("["):
                s.fmt = ""

        xp = XP(self.game)

        if xp.get_xp_total_obtained() == xp.get_xp_total_available():
            text = "Você atingiu o máximo de xp!"
            percent = 100.0
        else:
            if Flags.percent.is_true():
                text = f"L:{xp.get_level()} XP:{int(100 * xp.get_xp_level_current() / xp.get_xp_level_needed())}%"
            else:
                text = f"L:{xp.get_level()} XP:{xp.get_xp_level_current()}/{xp.get_xp_level_needed()}"
            percent = float(xp.get_xp_level_current()) / float(xp.get_xp_level_needed())
        size = max(15, dx - content.len() - 1)
        done = "/k" + Flags.main_done.get_value()
        todo = "/k" + Flags.main_todo.get_value()
        xp_bar = Util.build_bar(text, percent, size, done, todo).addt(" ")

        limit = dx - xp_bar.len()
        content.trim_spaces(limit)
        content.trim_alfa(limit)
        content.trim_end(limit)

        frame.write(0, 0, content.concat(xp_bar))

    def show_items(self):
        # self.disable_on_resize()
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
        if Flags.help_bar.is_true():
            bottom_sy = 1
            frame_bottom = Frame(lines - 1, 0).set_size(3, main_sx)
            self.show_bottom_bar(frame_bottom)

        mid_y = top_y + top_dy
        mid_sy = main_sy - (top_y + top_dy + bottom_sy)

        skills_sx = 0
        if Flags.skills_bar.is_true():
            skills_sx = max(20, main_sx // 4)
            frame_skills = Frame(mid_y, cols - skills_sx).set_size(mid_sy, skills_sx)
            self.show_skills_bar(frame_skills)

        flags_sx = 0
        if Flags.flags_bar.is_true():
            flags_sx = 17
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

        mark_opt = Flags.dots.is_true()
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
            for q in self.get_available_quests_from_cluster(obj):
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

    def set_grade(self, grade: int):
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Task):
            obj.set_grade(grade)

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

    # @staticmethod
    # def check_disable_flags():
    #     lines, cols = Fmt.get_size()
    #     if cols < 50:
    #         if Flags.flags_bar.is_true():
    #             Flags.flags_bar.toggle()

    # def check_disable_skills(self):
    #     lines, cols = Fmt.get_size()
    #     if cols < 50:
    #         if self.flags_on(Keys.tog_skills_bar):
    #             self.flags_toggle("skills_bar")


    class Key:
        left = "a"
        right = "d"
        down_task = "g"
        help = "h"
        expand = ">"
        collapse = "<"
        set_lang = "l"
        open_link = "o"
        quit = "q"
        down = "s"
        up = "w"
        reset = "r"
        mass_toggle = "T"
        toggle_space = " "
        toggle_enter = "\n"

    class FlagFunctor:
        def __init__(self, input_layer, flag: Flag):
            self.input_layer = input_layer
            self.flag = flag

        def __call__(self):
            self.flag.toggle()
            if self.flag.get_location() == "left" and self.flag.is_bool():
                f = Floating("v").warning()
                f.addt(self.flag.get_description())
                if self.flag.is_true():
                    f.adds(Sentence().addf("G", "ligado"))
                else:
                    f.adds(Sentence().addf("R", "desligado"))
                self.input_layer.append(f)

    class GradeFunctor:
        def __init__(self, grade: int, fn):
            self.grade = grade
            self.fn = fn

        def __call__(self):
            self.fn(self.grade)

    def make_callback(self) -> Dict[str, Any]:
        def set_exit():
            self.exit = True

        def move_up():
            self.index_selected = max(0, self.index_selected - 1)

        def move_down():
            self.index_selected = min(len(self.items) - 1, self.index_selected + 1)

        def reset_colors():
            for flag in self.flagsman.left:
                if not flag.is_bool():
                    flag.index(0)

        calls = {}

        def add_int(_key: int, fn):
            if _key in calls.keys():
                raise ValueError(f"Chave duplicada {chr(_key)}")
            calls[_key] = fn

        def add_str(str_key: str, fn):
            add_int(ord(str_key), fn)

        add_int(curses.KEY_RESIZE, self.disable_on_resize)
        add_str(self.Key.quit, lambda: self.add_input(Floating("v").addt("Bye Bye").set_exit_fn(set_exit).warning()))

        add_str(self.Key.up, move_up)
        add_int(curses.KEY_UP, move_up)

        add_str(self.Key.down, move_down)
        add_int(curses.KEY_DOWN, move_down)

        add_str(self.Key.left, self.arrow_left)
        add_int(curses.KEY_LEFT, self.arrow_left)

        add_str(self.Key.right, self.arrow_right)
        add_int(curses.KEY_RIGHT, self.arrow_right)

        add_str(self.Key.help, self.show_help)
        add_str(self.Key.expand, self.process_expand)
        add_str(self.Key.collapse, self.process_collapse)

        add_str(self.Key.toggle_enter, self.toggle)
        add_str(self.Key.toggle_space, self.toggle)
        add_str(self.Key.open_link, self.open_link)
        add_str(self.Key.set_lang, self.set_language)
        add_str(self.Key.down_task, self.process_down)
        add_str(self.Key.mass_toggle, self.mass_mark)
        add_str(self.Key.reset, reset_colors)

        for value in range(10):
            add_str(str(value), self.GradeFunctor(int(value), self.set_grade))

        for flag in self.flagsman.left:
            add_str(flag.get_char(), self.FlagFunctor(self.input_layer, flag))

        for flag in self.flagsman.top:
            add_str(flag.get_char(), self.FlagFunctor(self.input_layer, flag))


        return calls

    def main(self, scr):
        curses.curs_set(0)  # Esconde o cursor
        Fmt.init_colors()  # Inicializa as cores
        Fmt.set_scr(scr)  # Define o scr como global

        while not self.exit:
            self.update_available_quests()
            self.update_new()
            self.show_items()
            self.draw_warnings()
            self.generate_graph(scr)
            calls = self.make_callback()

            if len(self.input_layer) > 0 and self.input_layer[0].is_enable():
                value = self.input_layer[0].get_input()
            else:
                value = scr.getch()

            if value in calls.keys():
                calls[value]()

            self.reload_options()
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
