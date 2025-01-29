from tko.play.keys import GuiActions, GuiKeys
from tko.game.xp import XP
from tko.play.opener import Opener
from tko.settings.settings import Settings
from tko.util.text import Text, Token,  RToken
from tko.util.symbols import symbols
import os

from tko.play.fmt import Fmt
from tko.play.frame import Frame
from tko.play.border import Border
from tko.play.search import Search
from tko.play.language_setter import LanguageSetter
from tko.play.images import opening, random_get
from tko.play.floating import Floating, FloatingInput
from tko.play.floating_manager import FloatingManager
from tko.play.flags import Flag, Flags, FlagsMan
from tko.play.tasktree import TaskTree

from tko.game.quest import Quest
from tko.game.task import Task
from tko.game.cluster import Cluster
from tko.play.task_graph import TaskGraph
from tko.play.week_graph import WeekGraph

from typing import List, Any, Dict, Callable, Tuple
import datetime

class Gui:

    def __init__(self, tree: TaskTree, flagsman: FlagsMan, fman: FloatingManager):
        self.rep = tree.rep
        self.game = tree.game
        self.tree = tree
        self.flagsman = flagsman
        self.fman = fman
        self.settings = tree.settings
        self.search = Search(tree=self.tree, fman=self.fman)
        self.style: Border = Border(self.settings.app)
        self.language = LanguageSetter(self.rep, self.flagsman, self.fman)
        self.colors = self.settings.colors

        self.app = Settings().app


    def get_help_fixed(self):
        color = "W"
        try:
            selected = self.tree.get_selected_throw()
            if isinstance(selected, Task):
                color = "Y"
        except IndexError:
            pass

        help_fixed: List[Text] = [
            Text() + RToken("C", f"{GuiActions.palette} [{GuiKeys.palette}]"),
            Text() + RToken(color, f"{GuiActions.evaluate}[.]"),
            Text() + RToken("G", f"{self.get_activate_label()} [↲]"),
            Text() + RToken(color, f"{GuiActions.edit} [{GuiKeys.edit}]"),
            # Text() + RToken("C", f"{GuiActions.navegar} [wasd]")
            Text() + RToken("C", f"{GuiActions.search} [{GuiKeys.search}]")
        ]
        return help_fixed

    def get_activate_label(self) -> str:
        output: str = GuiActions.activate
        try:
            obj = self.tree.get_selected_throw()
        except IndexError:
            return " Retornar"
        if isinstance(obj, Quest):
            quest: Quest = obj
            if not Flags.admin and not quest.is_reachable():
                output = "Bloqueado"
            elif quest.key in self.tree.expanded:
                output = " Contrair"
            else:
                output = " Expandir"
        elif isinstance(obj, Cluster):
            cluster: Cluster = obj
            if cluster.key in self.tree.expanded:
                output = " Contrair"
            else:
                output = " Expandir"
        elif isinstance(obj, Task):
            output = self.tree.get_task_action(obj)

        return output

    def center_header_footer(self, value: Text, frame: Frame) -> Text:
        half = value.len() // 2
        x = frame.get_x()
        dy, dx = Fmt.get_size()
        color = "r" if Flags.admin else ""
        full = Text().addf(color, "─" * ((dx//2) - x - 2 - half)).add(value)
        return full

    def show_main_bar(self, frame: Frame):
        top = Text()
        alias_color = "R"
        dirname = self.rep.get_rep_dir()
        dirname = os.path.basename(dirname).upper()
        top.add(self.style.border(alias_color, dirname))
        if Flags.admin:
            color = "W" if Flags.admin else "K"
            top.add(self.style.border(color, "ADMIN"))
        top.add(self.style.border("G", self.rep.get_lang().upper()))
        full = self.center_header_footer(top, frame)
        frame.set_header(full, "<")
        
        # if Flags.flags:
        #     value = self.make_flags_bar()
        #     full = self.center_header_footer(value, frame)
        #     frame.set_footer(full, "<")
        frame.draw()

        dy, dx = frame.get_inner()
        for y, sentence in enumerate(self.tree.get_senteces(dy)):
            if sentence.len() > dx:
                sentence.trim_end(dx - 3)
                sentence.addf("r", "...")
            frame.write(y, 0, sentence)



    def show_skills_bar(self, frame_xp):
        dy, dx = frame_xp.get_inner()
        xp = XP(self.game)
        total_perc = int(
            100 * (xp.get_xp_total_obtained() / xp.get_xp_total_available())
        )
        if Flags.percent:
            text = f" XPTotal:{total_perc}%"
        else:
            text = f" XPTotal:{xp.get_xp_total_obtained()}"

        done = self.colors.main_bar_done
        todo = self.colors.main_bar_todo
        total_bar = self.style.build_bar(text, total_perc / 100, dx - 2, done, todo)
        frame_xp.set_header(Text().addf("/", "Skills"), "^", "{", "}")
        frame_xp.set_footer(Text().add(" ").add(" "), "^")
        frame_xp.draw()

        reachable_quests = [q for q in self.game.quests.values() if q.is_reachable()]
        total, obt = self.game.get_skills_resume(reachable_quests)
        elements: List[Text] = []
        for skill, value in total.items():
            if Flags.percent:
                text = f"{skill}:{int(100 * obt[skill] / value)}%"
            else:
                text = f"{skill}:{obt[skill]}/{value}"
            perc = obt[skill] / value
            done = self.colors.progress_skill_done
            todo = self.colors.progress_skill_todo
            skill_bar = self.style.build_bar(text, perc, dx - 2, done, todo)
            elements.append(skill_bar)
            
        elements.append(total_bar)

        line_breaks = dy - len(elements)
        for skill_bar in elements:
            frame_xp.print(1, skill_bar)
            if line_breaks > 0:
                line_breaks -= 1
                frame_xp.print(1, Text())


    def build_list_sentence(self, items: List[Text]) -> List[Text]:
        out: List[Text] = []
        for x in items:
            color_ini = x.data[0].fmt
            color_end = x.data[-1].fmt
            left = self.style.roundL(color_ini)
            right = self.style.roundR(color_end)
            middle = x.clone()
            if x.data[0].text == "!":
                left = self.style.sharpL(color_ini)
                right = self.style.sharpR(color_end)
                middle.data = x.data[1:]
            out.append(Text().add(left).add(middle).add(right))
        return out

    def build_bottom_array(self):
        array: List[Text] = []
        array += self.get_help_fixed()
        return self.build_list_sentence(array)

    def show_bottom_bar(self):
        lines, cols = Fmt.get_size()
        elems = self.build_bottom_array()
        line_main = Text().add(" ").join(elems) # alignment adjust
        Fmt.write(lines - 1, 0, line_main.center(cols))

    def make_xp_button(self, size):
        if self.search.search_mode:
            text = " Busca: " + self.tree.search_text + symbols.cursor.text
            percent = 0.0
            done = "W"
            todo = "W"
            text = text.ljust(size)
        else:
            text, percent = self.build_xp_bar()
            done = self.colors.main_bar_done
            todo = self.colors.main_bar_todo
            text = text.center(size)
        xpbar = self.style.build_bar(text, percent, len(text), done, todo)
        return xpbar

    def show_top_bar(self, frame: Frame):
        lista = [
            Text() + RToken("Y", f"Sair  [q]"),
            Text() + RToken("Y", f"Ajuda [?]"),
        ]
        help = self.build_list_sentence(lista)
        search = help[0]
        evaluate = help[1]

        pre: List[Text] = []
        pre.append(search)

        pos: List[Text] = []
        pos.append(evaluate)

        limit = frame.get_dx()
        size = limit - Text().add(" ").join(pre + pos).len() - 2
        main_label = self.make_xp_button(size)
        info = Text().add(" ").join(pre + [main_label] + pos)
        frame.write(0, 0, info.center(frame.get_dx()))

    def show_help(self):
        # def empty(value):
        #     pass
        _help: Floating = Floating("v>").set_text_ljust()
        self.fman.add_input(_help)

        _help.set_header_text(Text().add(" Ajuda "))
        # _help.put_text(" Movimentação ".center(dx, symbols.hbar.text))
        _help.put_sentence(Text.format("    Ajuda ").addf("r", GuiKeys.key_help).add("  Abre essa tela de ajuda")
        )

        _help.put_sentence(Text.format("  ").addf("r", "Shift + B")
                           .add("  Habilita ").addf("r", "").addf("R", "ícones").addf("r", "").add(" se seu ambiente suportar"))
        _help.put_sentence(Text() + "" + RToken("g", "setas") + ", " + RToken("g", "wasd")  + "  Para navegar entre os elementos")
        _help.put_sentence(Text() + f"   {GuiActions.palette} " + RToken("r", f"{GuiKeys.palette}") + "  Abre o menu de ações e configurações")
        _help.put_sentence(Text() + f"   {GuiActions.github} " + RToken("r", f"{GuiKeys.github_open}") + "  Abre tarefa em uma aba do browser")
        _help.put_sentence(Text() + f"   {GuiActions.download} " + RToken("r", f"{GuiKeys.down_task}") + "  Baixa tarefa de código para seu dispositivo")
        _help.put_sentence(Text() + f"   {GuiActions.edit} " + RToken("r", f"{GuiKeys.edit}") + "  Abre os arquivos no editor de código")
        _help.put_sentence(Text() + f"   {GuiActions.activate} " + RToken("r", "↲") + "  Interage com o elemento de acordo com o contexto")
        _help.put_sentence(Text() + "             (baixar, visitar, escolher, compactar, expandir)")
        _help.put_sentence(Text() + f"  {GuiActions.evaluate} " + RToken("r", ".") + "  Abre tela para auto avaliação")
        _help.put_sentence(Text() + f"{GuiActions.search} " + RToken("r", f"{GuiKeys.search}") + "  Abre a barra de pesquisa")

        _help.put_sentence(Text())
        _help.put_sentence(Text() + "Você pode mudar o editor padrão com o comando")
        _help.put_sentence(Text() + RToken("g", "             tko config --editor <comando>"))


    def build_xp_bar(self) -> Tuple[str, float]:
        xp = XP(self.game)
        available = xp.get_xp_total_available()
        if available > 0 and xp.get_xp_total_obtained() == available:
            text = "Você atingiu o máximo de xp!"
            percent = 100.0
        else:
            # lang = self.rep.get_lang().upper()
            level = xp.get_level()
            percent = float(xp.get_xp_level_current()) / float(xp.get_xp_level_needed())
            if Flags.percent:
                xpobt = int(100 * xp.get_xp_level_current() / xp.get_xp_level_needed())
                text = "Level:{} XP:{}%".format(level, xpobt)
            else:
                xpobt1 = xp.get_xp_level_current()
                xpobt2 = xp.get_xp_level_needed()
                text = "Level:{} XP:{}/{}".format(level, xpobt1, xpobt2)

        return text, percent

    def print_task_graph(self, frame, x, task_key: str, width: int, height: int):
        tg = TaskGraph(self.settings, self.rep, task_key, width, height, minutes_mode=not Flags.graph)
        if len(tg.collected) == 1:
            return False
        graph = tg.get_graph()
        for y, line in enumerate(graph):
            frame.write(y, x, Text().addf("g", line))
        return True
    
    def print_week_graph(self, frame, x, width: int, height: int, week_mode: bool = False):
        tg = WeekGraph(width, height, week_mode)
        if len(tg.collected) == 1:
            return False
        graph = tg.get_graph()
        for y, line in enumerate(graph):
            frame.write(y, x, Text().addf("g", line))
        return True

    def show_opening(self, frame: Frame):
        if not self.app.get_use_images():
            return
        lines, cols = frame.get_inner()
        
        now = datetime.datetime.now()
        parrot = random_get(opening, str(now.hour))
        parrot_lines = parrot.splitlines()
        max_len = max([len(line) for line in parrot_lines])
        yinit = 1
        distance = 27
        try:
            selected = self.tree.get_selected_throw()
            width = cols - self.tree.max_title - distance - 7
            if width < 5:
                width = 5
            height = lines - 4
            if height < 3:
                height = 3
            if isinstance(selected, Task):
                if self.print_task_graph(frame, self.tree.max_title + distance, selected.key, width, height):
                    return
            elif isinstance(selected, Cluster) or isinstance(selected, Quest):
                week_mode = isinstance(selected, Cluster)
                if self.print_week_graph(frame, self.tree.max_title + distance, width, height, week_mode):
                    return

        except IndexError:
            pass
        for y, line in enumerate(parrot_lines):
            frame.write(y, self.tree.max_title + distance, Text().addf("g", line))

    def show_items(self):
        border_color = "r" if Flags.admin else ""
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
        left_size = 25
        skills_sx = 0
        flags_sx = 0
        if Flags.skills:
            skills_sx = left_size #max(20, main_sx // 4)
        
        task_sx = main_sx - flags_sx - skills_sx

        frame_top = Frame(top_y, 0).set_size(top_dy + 2, cols)
        self.show_top_bar(frame_top)

        # frame_bottom = Frame(lines - bottom_dy - 1, -1).set_size(bottom_dy + 2, cols + 2)
        self.show_bottom_bar()
        if task_sx > 5: 
            frame_main = Frame(mid_y, 0).set_size(mid_sy, task_sx).set_border_color(border_color)
            self.show_main_bar(frame_main)
        self.show_opening(frame_main)

        if Flags.skills:
            frame_skills = Frame(mid_y, cols - skills_sx).set_size(mid_sy, skills_sx).set_border_color(border_color)
            self.show_skills_bar(frame_skills)
