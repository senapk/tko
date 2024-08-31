from ..game.game import Game
from ..game.cluster import Cluster
from ..game.quest import Quest
from ..game.task import Task
from ..game.xp import XP
from ..game.graph import Graph
import random
from .opener import Opener
from ..run.basic import Success
from typing import List, Any, Dict, Callable, Tuple
from ..settings.settings import Settings
from ..settings.app_settings import AppSettings
from ..settings.rep_settings import languages_avaliable, RepData
from ..down import Down
from ..util.sentence import Sentence, Token,  RToken
from .fmt import Fmt
from .frame import Frame
from .style import Style
from .search import Search
from .images import opening, random_get
import datetime

from .floating import Floating
from .floating_manager import FloatingManager
from .flags import Flag, Flags, FlagsMan
from .tasktree import TaskTree
from ..actions import Run
from ..run.param import Param

class Actions:
    ler_online = "Github"
    sair = "Sair"
    ajuda = "Ajuda"
    baixar = "Baixar"
    ativar = "Ativar"
    navegar = "←↓→"
    editar = "Editar"
    marcar = "Marcar"
    desmarcar = "Desmarcar"
    colapsar = "Colapsar"
    pesquisar = "Buscar"

class Key:
    left = "a"
    right = "d"
    down = "s"
    up = "w"

    down_task = "b"
    select_task = "\n"
    ajuda = "h"
    expand = ">"
    expand2 = "."
    collapse = "<"
    collapse2 = ","
    inc_grade = "+"
    inc_grade2 = "="
    dec_grade = "-"
    dec_grade2 = "_"
    set_root_dir = "D"
    set_lang = "L"
    github_open = "g"
    quit = "q"
    edit= "e"
    cores = "C"
    bordas = "B"
    pesquisar = "/"
    graph = "G"


class Gui:

    def __init__(self, rep: RepData, rep_alias: str, game: Game, tree: TaskTree, flagsman: FlagsMan, search: Search, fman: FloatingManager):
        self.rep = rep
        self.rep_alias = rep_alias
        self.game = game
        self.tree = tree
        self.flagsman = flagsman
        self.fman = fman
        self.search = search
        self.gen_graph: bool = False

        self.app = Settings().app

        self.help_basic: List[Sentence] = [
            Sentence() + RToken("Y", f"{Actions.pesquisar}[{Key.pesquisar}]"),
            Sentence() + RToken("Y", f"{Actions.marcar} {Key.inc_grade}{Key.dec_grade}"),
        ]

        self.help_fixed: List[Sentence] = [
            Sentence() + RToken("C", f"  {Actions.sair}[{Key.quit}]"),
            Sentence() + RToken("C", f"{Actions.editar}[{Key.edit}]"),
            Sentence() + RToken("G", f"{Actions.ativar}[↲]"),
        ]
        self.help_others_before: List[Sentence] = [
            Sentence() + RToken("Y", f" {Actions.ajuda}[{Key.ajuda}]"),
            Sentence() + RToken("Y", f"{Actions.ler_online}[{Key.github_open}]"),
        ]
        self.help_others_after: List[Sentence] = [
            Sentence() + RToken("Y", f"{Actions.baixar}[{Key.down_task}]"),
            Sentence() + RToken("Y", f"{Actions.navegar}[wasd]")
        ]

        self.wrap_size = Sentence(" ").join(self.build_bottom_array()).len()


    @staticmethod
    def disable_on_resize():
        _, cols = Fmt.get_size()
        if cols < 50 and Flags.skills.is_true() and Flags.config.is_true():
            Flags.skills.toggle()
        elif cols < 30 and Flags.skills.is_true():
            Flags.skills.toggle()
        elif cols < 35 and Flags.config.is_true():
            Flags.config.toggle()


    def show_main_bar(self, frame: Frame):
        dy, dx = frame.get_inner()
        top = Sentence()
        if self.two_column_mode() and Flags.others.is_true(): 
            top.add(Style.get_flag_sentence(Flags.config)).add(" ")

        alias_color = "R"
        top.add(Style.border_sharp(alias_color, self.rep_alias.upper()))
        if Flags.others.is_true():
            color = "W" if Flags.admin.is_true() else "K"
            top.add(Style.border_sharp(color, "ADMIN"))
        top.add(Style.border_sharp("G", self.rep.get_lang().upper()))

        if self.two_column_mode() and Flags.others.is_true(): 
            top.add(" ").add(Style.get_flag_sentence(Flags.skills))

        frame.set_header(top, "^")
        
        if self.two_column_mode():
            elems = self.build_bottom_array()
            line_up = Sentence(" ").join(elems[0 : 2] + elems[-2:])
            frame.set_footer(line_up, "")
        frame.draw()

        for y, sentence in enumerate(self.tree.get_senteces(dy)):
            if sentence.len() > dx:
                sentence.trim_end(dx - 3)
                sentence.addf("r", "...")
            frame.write(y, 0, sentence)

    def show_inventary_bar(self, frame_xp):
        dy, dx = frame_xp.get_inner()
        xp = XP(self.game)
        total_perc = int(
            100 * (xp.get_xp_total_obtained() / xp.get_xp_total_available())
        )
        if Flags.percent.is_true():
            text = f" XPTotal:{total_perc}%"
        else:
            text = f" XPTotal:{xp.get_xp_total_obtained()}"

        done = Style.main_done() + "/"
        todo = Style.main_todo() + "/"
        total_bar = Style.build_bar(text, total_perc / 100, dx - 2, done, todo)
        frame_xp.set_header(Sentence().addf("/", "Skills"), "^", "{", "}")
        frame_xp.set_footer(Sentence().add(" ").add(self.app.get_rootdir()).add(" "), "^")
        frame_xp.draw()

        total, obt = self.game.get_skills_resume([self.game.quests[key] for key in self.game.available_quests])
        elements: List[Sentence] = []
        for skill, value in total.items():
            if Flags.percent.is_true():
                text = f"{skill}:{int(100 * obt[skill] / value)}%"
            else:
                text = f"{skill}:{obt[skill]}/{value}"
            perc = obt[skill] / value
            done = Style.skill_done() + "/"
            todo = Style.skill_todo() + "/"
            skill_bar = Style.build_bar(text, perc, dx - 2, done, todo)
            elements.append(skill_bar)
            
        elements.append(total_bar)

        line_breaks = dy - len(elements)
        for skill_bar in elements:
            frame_xp.print(1, skill_bar)
            if line_breaks > 0:
                line_breaks -= 1
                frame_xp.print(1, Sentence())

    def show_config_bar(self, frame: Frame):
        frame.set_header(Sentence().addf("/", "Config"), "^", "{", "}")
        frame.draw()

        elements: List[Sentence] = []
        pad = 11
        for flag in self.flagsman.left:
            elements.append(Style.get_flag_sentence(flag, pad))


        colored = Flag().name("Colorido").char("C").values(["1" if self.app.is_colored() else "0"]).text("Ativa ou desativa as cores").bool()
        elements.append(Style.get_flag_sentence(colored, pad))
        bordas = Flag().name("Bordas").char("B").values(["1" if self.app.is_nerdfonts() else "0"]).text("Ativa ou desativa as bordas").bool()
        elements.append(Style.get_flag_sentence(bordas, pad))
        grafo = Flag().name("Grafo").char("G").values(["1" if self.gen_graph else "0"]).text("Ativa a geração do grafo").bool()
        elements.append(Style.get_flag_sentence(grafo, pad))


        color = "W" if not self.app.is_colored() else "C"

        elements.append(Style.border_round(color, "DirDestino [D]"))
        elements.append(Style.border_round(color, "Linguagem  [L]"))

        dy, dx = frame.get_inner()
        line_breaks = dy - len(elements)
        for i, elem in enumerate(elements):
            frame.print(0, elem)
            if line_breaks > 0:
                line_breaks -= 1
                frame.print(0, Sentence())

    def two_column_mode(self):
        _, cols = Fmt.get_size()
        return cols < self.wrap_size + 2 and Flags.others.is_true()

    def build_list_sentence(self, items: List[Sentence]) -> List[Sentence]:
        out: List[Sentence] = []
        for x in items:
            color_ini = x.data[0].fmt if self.app.is_colored() else "W"
            color_end = x.data[-1].fmt if self.app.is_colored() else "W"
            left = Style.roundL(color_ini)
            right = Style.roundR(color_end)
            middle = x.clone()
            if x.data[0].text == "!":
                left = Style.sharpL(color_ini)
                right = Style.sharpR(color_end)
                middle.data = x.data[1:]
            out.append(Sentence().add(left).add(middle).add(right))
        return out

    def build_bottom_array(self):
        array: List[Sentence] = []
        array += self.help_others_before
        array += self.help_fixed
        if self.app.is_colored():
            color = "G" if Flags.others.is_true() else "Y"
        else:
            color = "W" if Flags.others.is_true() else "K"

        array.append(Sentence() + RToken(color, "!Outros[o]"))
        array += self.help_others_after

        return self.build_list_sentence(array)

    def show_bottom_bar(self):
        lines, cols = Fmt.get_size()
        elems = self.build_bottom_array()
        if self.two_column_mode():
            line_down = Sentence(" ").join(elems[2:-2])
            Fmt.write(lines - 1, 0, line_down.center(cols))
        else:
            if Flags.others.is_true():
                line_all = Sentence(" ").join(elems)
                Fmt.write(lines - 1, 0, line_all.center(cols))
            else:
                line_main = Sentence(" ").join(elems[2: -2]) # alignment adjust
                Fmt.write(lines - 1, 0, line_main.center(cols))   

    def make_xp_button(self, size):
        if self.search.search_mode:
            text = " Busca: " + self.tree.search_text + "┊"
            percent = 0.0
            done = "W"
            todo = "W"
            text = text.ljust(size)
        else:
            text, percent = self.build_xp_bar()
            done = Style.main_done()
            todo = Style.main_todo()
            text = text.center(size)
        xpbar = Style.build_bar(text, percent, len(text), done, todo)
        return xpbar

    def show_top_bar(self, frame: Frame):
        help = self.build_list_sentence(self.help_basic)
        pesquisar = help[0]
        marcar = help[1]
        config = Style.get_flag_sentence(Flags.config)
        skills = Style.get_flag_sentence(Flags.skills)
        others = Flags.others.is_true()

        pre: List[Sentence] = []
        pre.append(marcar)
        if others and not self.two_column_mode():
            pre.append(config)

        pos: List[Sentence] = []
        if others and not self.two_column_mode():
            pos.append(skills)
        pos.append(pesquisar)

        limit = self.wrap_size
        if frame.get_dx() < self.wrap_size:
            limit = frame.get_dx()
        size = limit - Sentence(" ").join(pre + pos).len() - 2
        main_label = self.make_xp_button(size)
        info = Sentence(" ").join(pre + [main_label] + pos)
        frame.write(0, 0, info.center(frame.get_dx()))


        # frame.set_border_none()
        # frame.set_border_rounded()
        # frame.draw()

    def show_help_config(self):
        _help: Floating = Floating("v>").warning().set_ljust_text().set_header(" Configurações ")
        self.fman.add_input(_help)
        _help.put_sentence(Sentence() + f"      Mínimo " + RToken("r", f"[{Flags.minimum.get_char()}]") + " - Mostrar os requisitos mínimos para completar a missão")
        _help.put_sentence(Sentence() + f"  Recompensa " + RToken("r", f"[{Flags.reward.get_char()}]") + " - Mostrar quanto de experiência cada atividade fornece")
        _help.put_sentence(Sentence() + f"  Percentual " + RToken("r", f"[{Flags.percent.get_char()}]") + " - Mostrar os valores em percentual")
        _help.put_sentence(Sentence() + f"  ModoAdmin " + RToken("r", f"Shift + [A]") + " - Liberar acesso a todas as missões" )
        _help.put_sentence(Sentence() + f"  PastaRaiz " + RToken("r", f"Shift + [{Key.set_root_dir}]") + " - Mudar a pasta padrão de download do tko" )
        _help.put_sentence(Sentence() + f"  Linguagem " + RToken("r", f"Shift + [{Key.set_lang}]") + " - Mudar a linguagem de download dos rascunhos" )


    def show_help(self):
        # def empty(value):
        #     pass
        _help: Floating = Floating("v>").set_ljust_text()
        self.fman.add_input(_help)

        _help.set_header_sentence(Sentence().add(" Ajuda "))
        # _help.put_text(" Movimentação ".center(dx, symbols.hbar.text))
        _help.put_sentence(Sentence("    Ajuda ").addf("r", Key.ajuda).add("  Abre essa tela de ajuda")
        )

        _help.put_sentence(Sentence("  ").addf("r", "Shift + B")
                           .add("  Habilita ").addf("r", "").addf("R", "ícones").addf("r", "").add(" se seu ambiente suportar"))
        _help.put_sentence(Sentence() + "" + RToken("g", "setas") + ", " + RToken("g", "wasd")  + "  Para navegar entre os elementos")
        _help.put_sentence(Sentence() + f"{Actions.ler_online} " + RToken("r", f"{Key.github_open}") + "  Abre tarefa em uma aba do browser")
        _help.put_sentence(Sentence() + f"   {Actions.baixar} " + RToken("r", f"{Key.down_task}") + "  Baixa tarefa de código para seu dispositivo")
        _help.put_sentence(Sentence() + f"   {Actions.editar} " + RToken("r", f"{Key.edit}") + "  Abre os arquivos no editor de código")
        _help.put_sentence(Sentence() + f"   {Actions.ativar} " + RToken("r", "↲") + "  Interage com o elemento")
        _help.put_sentence(Sentence() + f"   {Actions.marcar} " + RToken("r", f"{Key.inc_grade}") + RToken("r", f"{Key.dec_grade}") + " Muda a pontuação da tarefa")
        _help.put_sentence(Sentence())
        _help.put_sentence(Sentence() + "Você pode mudar o editor padrão com o comando")
        _help.put_sentence(Sentence() + RToken("g", "             tko config --editor <comando>"))


    def build_xp_bar(self) -> Tuple[str, float]:
        xp = XP(self.game)
        if xp.get_xp_total_obtained() == xp.get_xp_total_available():
            text = "Você atingiu o máximo de xp!"
            percent = 100.0
        else:
            # lang = self.rep.get_lang().upper()
            level = xp.get_level()
            percent = float(xp.get_xp_level_current()) / float(xp.get_xp_level_needed())
            if Flags.percent.is_true():
                xpobt = int(100 * xp.get_xp_level_current() / xp.get_xp_level_needed())
                text = "Level:{} XP:{}%".format(level, xpobt)
            else:
                xpobt1 = xp.get_xp_level_current()
                xpobt2 = xp.get_xp_level_needed()
                text = "Level:{} XP:{}/{}".format(level, xpobt1, xpobt2)

        return text, percent

    def show_opening(self):
        if Fmt.get_size()[1] < 100:
            return
        if not Flags.images.is_true():
            return
        _, cols = Fmt.get_size()
        
        now = datetime.datetime.now()
        parrot = random_get(opening, str(now.hour))
        parrot_lines = parrot.split("\n")
        max_len = max([len(line) for line in parrot_lines])
        yinit = 1
        for y, line in enumerate(parrot_lines):
            Fmt.write(yinit + y, cols - max_len - 2, Sentence().addf("g", line))

    def show_items(self):
        border_color = "r" if Flags.admin.is_true() else ""
        Fmt.clear()
        self.tree.reload_sentences()
        lines, cols = Fmt.get_size()
        main_sx = cols  # tamanho em x livre
        main_sy = lines  # size em y avaliable

        top_y = -1
        top_dy = 1  #quantas linhas o topo usa
        bottom_dy = 1 # quantas linhas o fundo usa
        mid_y = top_dy # onde o meio começa
        mid_sy = main_sy - top_dy - bottom_dy # tamanho do meio

        skills_sx = 0
        if Flags.skills.is_true():
            skills_sx = max(20, main_sx // 4)
        else:
            self.show_opening()

        flags_sx = 0
        if Flags.config.is_true():
            flags_sx = 18            

        task_sx = main_sx - flags_sx - skills_sx

        frame_top = Frame(top_y, 0).set_size(top_dy + 2, cols)
        self.show_top_bar(frame_top)

        # frame_bottom = Frame(lines - bottom_dy - 1, -1).set_size(bottom_dy + 2, cols + 2)
        self.show_bottom_bar()
        if task_sx > 5: 
            frame_main = Frame(mid_y, flags_sx).set_size(mid_sy, task_sx).set_border_color(border_color)
            self.show_main_bar(frame_main)

        if Flags.config.is_true():
            frame_flags = Frame(mid_y, 0).set_size(mid_sy, flags_sx).set_border_color(border_color)
            self.show_config_bar(frame_flags)

        if Flags.skills.is_true():
            frame_skills = Frame(mid_y, cols - skills_sx).set_size(mid_sy, skills_sx).set_border_color(border_color)
            self.show_inventary_bar(frame_skills)
