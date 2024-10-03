from tko.play.keys import GuiActions, GuiKeys
from tko.game.xp import XP
from tko.play.opener import Opener
from tko.settings.settings import Settings
from tko.util.text import Text, Token,  RToken
from tko.util.symbols import symbols

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
        help_fixed: List[Text] = [
            Text() + RToken("C", f" {GuiActions.leave}  [{GuiKeys.key_quit}]"),
            Text() + RToken("Y", f"{GuiActions.palette} [{GuiKeys.palette}]"),
            Text() + RToken("G", f"{GuiActions.activate} [↲]"),
            Text() + RToken("Y", f"{GuiActions.edit} [{GuiKeys.edit}]"),
            # Text() + RToken("C", f"{GuiActions.navegar} [wasd]")
            Text() + RToken("C", f"{GuiActions.search} [{GuiKeys.search}]")
        ]
        return help_fixed

    # def make_flags_bar(self) -> Text:
    #     lista: list[Flag] = []
    #     lista.append(Flags.flags)
    #     lista.append(Flags.skills)
    #     lista.append(Flags.admin)
    #     lista.append(Flags.percent)
    #     lista.append(Flags.minimum)
    #     lista.append(Flags.reward)
    #     value = "1" if self.settings.app.has_borders() else "0"
    #     borders = Flag().set_values([value]).set_name("Bordas").set_keycode("B")
    #     lista.append(borders)
    #     value = "1" if self.settings.app.has_images() else "0"
    #     images = Flag().set_values([value]).set_name("Imagens").set_keycode("I")
    #     lista.append(images)

    #     values = [self.style.get_flag_sentence(flag, 0 , True, False, False) for flag in lista]
    #     return Text("").join(values)

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
        top.add(self.style.border(alias_color, self.rep.alias.upper()))
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
        frame_xp.set_footer(Text().add(" ").add(self.app._rootdir).add(" "), "^")
        frame_xp.draw()

        total, obt = self.game.get_skills_resume([self.game.quests[key] for key in self.game.available_quests])
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
        line_main = Text(" ").join(elems) # alignment adjust
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
            Text() + RToken("Y", f"{GuiActions.self_grade} {GuiKeys.inc_self}{GuiKeys.dec_self}"),
            Text() + RToken("Y", f"{GuiActions.progress} {GuiKeys.dec_prog}{GuiKeys.inc_prog}"),
            # Text() + RToken("Y", f"{GuiActions.pesquisar} {GuiKeys.pesquisar}"),
        ]
        help = self.build_list_sentence(lista)
        self_grade = help[0]
        progress = help[1]
        # pesquisar = help[2]

        pre: List[Text] = []
        pre.append(progress)

        pos: List[Text] = []
        # pos.append(pesquisar)
        # skills = self.style.get_flag_sentence(Flags.skills)
        pos.append(self_grade)
        # pos.append(skills)


        limit = frame.get_dx()
        size = limit - Text(" ").join(pre + pos).len() - 2
        main_label = self.make_xp_button(size)
        info = Text(" ").join(pre + [main_label] + pos)
        frame.write(0, 0, info.center(frame.get_dx()))

    def show_help(self):
        # def empty(value):
        #     pass
        _help: Floating = Floating("v>").set_text_ljust()
        self.fman.add_input(_help)

        _help.set_header_sentence(Text().add(" Ajuda "))
        # _help.put_text(" Movimentação ".center(dx, symbols.hbar.text))
        _help.put_sentence(Text("    Ajuda ").addf("r", GuiKeys.key_help).add("  Abre essa tela de ajuda")
        )

        _help.put_sentence(Text("  ").addf("r", "Shift + B")
                           .add("  Habilita ").addf("r", "").addf("R", "ícones").addf("r", "").add(" se seu ambiente suportar"))
        _help.put_sentence(Text() + "" + RToken("g", "setas") + ", " + RToken("g", "wasd")  + "  Para navegar entre os elementos")
        _help.put_sentence(Text() + f"{GuiActions.github} " + RToken("r", f"{GuiKeys.github_open}") + "  Abre tarefa em uma aba do browser")
        _help.put_sentence(Text() + f"   {GuiActions.download} " + RToken("r", f"{GuiKeys.down_task}") + "  Baixa tarefa de código para seu dispositivo")
        _help.put_sentence(Text() + f"   {GuiActions.edit} " + RToken("r", f"{GuiKeys.edit}") + "  Abre os arquivos no editor de código")
        _help.put_sentence(Text() + f"   {GuiActions.activate} " + RToken("r", "↲") + "  Interage com o elemento")
        _help.put_sentence(Text() + f"   {GuiActions.progress} " + RToken("r", f"{GuiKeys.inc_self}") + RToken("r", f"{GuiKeys.dec_self}") + " Muda a autoavaliação")
        _help.put_sentence(Text())
        _help.put_sentence(Text() + "Você pode mudar o editor padrão com o comando")
        _help.put_sentence(Text() + RToken("g", "             tko config --editor <comando>"))


    def build_xp_bar(self) -> Tuple[str, float]:
        xp = XP(self.game)
        if xp.get_xp_total_obtained() == xp.get_xp_total_available():
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

    def show_opening(self, frame: Frame):
        # if Fmt.get_size()[1] < 100:
        #     return
        # if not self.app.has_images():
        #     return
        _, cols = Fmt.get_size()
        
        now = datetime.datetime.now()
        parrot = random_get(opening, str(now.hour))
        parrot_lines = parrot.split("\n")
        max_len = max([len(line) for line in parrot_lines])
        yinit = 1
        for y, line in enumerate(parrot_lines):
            frame.write(y, self.tree.max_title + 27, Text().addf("g", line))

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
