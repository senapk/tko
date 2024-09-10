from tko.play.keys import GuiActions, GuiKeys
from tko.game.xp import XP
from tko.play.opener import Opener
from tko.settings.settings import Settings
from tko.util.sentence import Sentence, Token,  RToken
from tko.util.symbols import symbols

from tko.play.fmt import Fmt
from tko.play.frame import Frame
from tko.play.border import Border
from tko.play.search import Search
from tko.play.config import Config
from tko.play.images import opening, random_get
from tko.play.floating import Floating
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
        self.config = Config(self.settings, self.rep, self.flagsman, self.fman)
        self.colors = self.settings.colors

        self.app = Settings().app
        self.wrap_size = Sentence(" ").join(self.build_bottom_array()).len()

    def get_help_others_after(self):
        color = "Y" if self.tree.in_focus else "W"
        help_others_after: List[Sentence] = [
            Sentence() + RToken(color, f"{GuiActions.baixar} [{GuiKeys.down_task}]"),
            Sentence() + RToken("Y", f"{GuiActions.navegar} [wasd]")
        ]
        return help_others_after

    def get_help_basic(self):
        color = "Y" if self.tree.in_focus else "W"
        help_basic: List[Sentence] = [
            Sentence() + RToken(color, f"{GuiActions.pesquisar}[{GuiKeys.pesquisar}]"),
            Sentence() + RToken(color, f"{GuiActions.marcar} {GuiKeys.inc_grade}{GuiKeys.dec_grade}"),
        ]
        return help_basic

    def get_help_fixed(self):
        color = "C" if self.tree.in_focus else "W"
        help_fixed: List[Sentence] = [
            Sentence() + RToken("C", f" {GuiActions.sair}  [{GuiKeys.key_quit}]"),
            Sentence() + RToken(color, f"{GuiActions.editar} [{GuiKeys.edit}]"),
            Sentence() + RToken("G", f"{GuiActions.ativar} [↲]"),
        ]
        return help_fixed

    def get_help_others_before(self):
        color = "Y" if self.tree.in_focus else "W"
        help_others_before: List[Sentence] = [
            Sentence() + RToken("Y", f" {GuiActions.ajuda} [{GuiKeys.key_help}]"),
            Sentence() + RToken(color, f"{GuiActions.github} [{GuiKeys.github_open}]"),
        ]
        return help_others_before

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
        top = Sentence()
        if self.two_column_mode() and self.app.has_full_hud() and not Flags.config.is_true():
            top.add(self.style.get_flag_sentence(Flags.config)).add(" ")

        alias_color = "R"
        top.add(self.style.border(alias_color, self.rep.alias.upper()))
        if Flags.admin.is_true():
            color = "W" if Flags.admin.is_true() else "K"
            top.add(self.style.border(color, "ADMIN"))
        top.add(self.style.border("G", self.rep.get_lang().upper()))

        if self.two_column_mode() and self.app.has_full_hud() and not Flags.config.is_true():
            top.add(" ").add(self.style.get_flag_sentence(Flags.skills))
        half = top.len() // 2
        x = frame.get_x()
        dy, dx = Fmt.get_size()
        full = Sentence().add("─" * ((dx//2) - x - 2 - half)).add(top)
        frame.set_header(full, "<")
        
        if self.two_column_mode() and not Flags.config.is_true():
            elems = self.build_bottom_array()
            line_up = Sentence(" ").join(elems[0 : 2] + elems[-2:])
            half = line_up.len() // 2
            _, adx = Fmt.get_size()
            if adx % 2 == 1:
                adx += 1 
            x = frame.get_x()
            full = Sentence().add("─" * ((adx//2) - x - 2 - half)).add(line_up)
            frame.set_footer(full, "<")
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
        if Flags.percent.is_true():
            text = f" XPTotal:{total_perc}%"
        else:
            text = f" XPTotal:{xp.get_xp_total_obtained()}"

        done = self.colors.main_bar_done + "/"
        todo = self.colors.main_bar_todo + "/"
        total_bar = self.style.build_bar(text, total_perc / 100, dx - 2, done, todo)
        frame_xp.set_header(Sentence().addf("/", "Skills"), "^", "{", "}")
        frame_xp.set_footer(Sentence().add(" ").add(self.app._rootdir).add(" "), "^")
        frame_xp.draw()

        total, obt = self.game.get_skills_resume([self.game.quests[key] for key in self.game.available_quests])
        elements: List[Sentence] = []
        for skill, value in total.items():
            if Flags.percent.is_true():
                text = f"{skill}:{int(100 * obt[skill] / value)}%"
            else:
                text = f"{skill}:{obt[skill]}/{value}"
            perc = obt[skill] / value
            done = self.colors.progress_skill_done + "/"
            todo = self.colors.progress_skill_todo + "/"
            skill_bar = self.style.build_bar(text, perc, dx - 2, done, todo)
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
        elements = self.config.get_elements()
        dy, dx = frame.get_inner()
        y = frame.get_y()
        lines, cols = Fmt.get_size()
        
        index = 0
        delta = 0
        if len(elements) > dy and self.config.index > dy - 2:
            delta = self.config.index - dy + 2
        elements = elements[delta:]
        target = self.config.index - delta

        while index < len(elements):
            item = elements[index]
            frame.print(0, item.sentence)
            if index == target and self.config.enabled:
                text = item.flag.get_description()
                focus = self.colors.focused_item
                Fmt.write(y + index + 1, cols - dx - len(text) - 4, Sentence().addf(focus, f" {text} ").add(self.style.sharpR(focus)))
            index += 1
            # if line_breaks > 0:
            #     line_breaks -= 1
            #     frame.print(0, Sentence())
            #     delta += 1

    def two_column_mode(self):
        _, cols = Fmt.get_size()
        return cols < self.wrap_size + 2 and self.app.has_full_hud()

    def build_list_sentence(self, items: List[Sentence]) -> List[Sentence]:
        out: List[Sentence] = []
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
            out.append(Sentence().add(left).add(middle).add(right))
        return out

    def build_bottom_array(self):
        array: List[Sentence] = []
        array += self.get_help_others_before()
        array += self.get_help_fixed()
        color = "G" if self.app.has_full_hud() else "Y"
        symbol = symbols.success if self.app.has_full_hud() else symbols.failure
        array.append(Sentence() + RToken(color, f" {symbol.text} {GuiActions.hud} [{GuiKeys.hud}]"))
        array += self.get_help_others_after()

        return self.build_list_sentence(array)

    def show_bottom_bar(self):
        lines, cols = Fmt.get_size()
        elems = self.build_bottom_array()
        if self.two_column_mode():
            line_down = Sentence(" ").join(elems[2:-2])
            Fmt.write(lines - 1, 0, line_down.center(cols))
        else:
            if self.app.has_full_hud():
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
            done = self.colors.main_bar_done
            todo = self.colors.main_bar_todo
            text = text.center(size)
        xpbar = self.style.build_bar(text, percent, len(text), done, todo)
        return xpbar

    def show_top_bar(self, frame: Frame):
        help = self.build_list_sentence(self.get_help_basic())
        pesquisar = help[0]
        marcar = help[1]
        config = self.style.get_flag_sentence(Flags.config)
        skills = self.style.get_flag_sentence(Flags.skills)
        others = self.app.has_full_hud()

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


    def show_help_config(self):
        _help: Floating = Floating("v>").warning().set_ljust_text().set_header(" Configurações ")
        self.fman.add_input(_help)
        _help.put_sentence(Sentence() + f"      Mínimo " + RToken("r", f"[{Flags.minimum.get_keycode()}]") + " - Mostrar os requisitos mínimos para completar a missão")
        _help.put_sentence(Sentence() + f"  Recompensa " + RToken("r", f"[{Flags.reward.get_keycode()}]") + " - Mostrar quanto de experiência cada atividade fornece")
        _help.put_sentence(Sentence() + f"  Percentual " + RToken("r", f"[{Flags.percent.get_keycode()}]") + " - Mostrar os valores em percentual")
        _help.put_sentence(Sentence() + f"  ModoAdmin " + RToken("r", f"Shift + [A]") + " - Liberar acesso a todas as missões" )
        _help.put_sentence(Sentence() + f"  PastaRaiz " + RToken("r", f"Shift + [{GuiKeys.set_root_dir}]") + " - Mudar a pasta padrão de download do tko" )
        _help.put_sentence(Sentence() + f"  Linguagem " + RToken("r", f"Shift + [{GuiKeys.set_lang}]") + " - Mudar a linguagem de download dos rascunhos" )


    def show_help(self):
        # def empty(value):
        #     pass
        _help: Floating = Floating("v>").set_ljust_text()
        self.fman.add_input(_help)

        _help.set_header_sentence(Sentence().add(" Ajuda "))
        # _help.put_text(" Movimentação ".center(dx, symbols.hbar.text))
        _help.put_sentence(Sentence("    Ajuda ").addf("r", GuiKeys.key_help).add("  Abre essa tela de ajuda")
        )

        _help.put_sentence(Sentence("  ").addf("r", "Shift + B")
                           .add("  Habilita ").addf("r", "").addf("R", "ícones").addf("r", "").add(" se seu ambiente suportar"))
        _help.put_sentence(Sentence() + "" + RToken("g", "setas") + ", " + RToken("g", "wasd")  + "  Para navegar entre os elementos")
        _help.put_sentence(Sentence() + f"{GuiActions.github} " + RToken("r", f"{GuiKeys.github_open}") + "  Abre tarefa em uma aba do browser")
        _help.put_sentence(Sentence() + f"   {GuiActions.baixar} " + RToken("r", f"{GuiKeys.down_task}") + "  Baixa tarefa de código para seu dispositivo")
        _help.put_sentence(Sentence() + f"   {GuiActions.editar} " + RToken("r", f"{GuiKeys.edit}") + "  Abre os arquivos no editor de código")
        _help.put_sentence(Sentence() + f"   {GuiActions.ativar} " + RToken("r", "↲") + "  Interage com o elemento")
        _help.put_sentence(Sentence() + f"   {GuiActions.marcar} " + RToken("r", f"{GuiKeys.inc_grade}") + RToken("r", f"{GuiKeys.dec_grade}") + " Muda a pontuação da tarefa")
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
        if not self.app.has_images():
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
        self.tree.set_focus(not self.config.enabled)
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
        if Flags.skills.is_true():
            skills_sx = left_size #max(20, main_sx // 4)
        elif Flags.config.is_true():
            flags_sx = left_size
        else:
            self.show_opening()
        
        task_sx = main_sx - flags_sx - skills_sx

        frame_top = Frame(top_y, 0).set_size(top_dy + 2, cols)
        self.show_top_bar(frame_top)

        # frame_bottom = Frame(lines - bottom_dy - 1, -1).set_size(bottom_dy + 2, cols + 2)
        self.show_bottom_bar()
        if task_sx > 5: 
            frame_main = Frame(mid_y, 0).set_size(mid_sy, task_sx).set_border_color(border_color)
            self.show_main_bar(frame_main)

        if Flags.config.is_true():
            frame_flags = Frame(mid_y, cols - flags_sx).set_size(mid_sy, flags_sx).set_border_color(border_color)
            self.show_config_bar(frame_flags)
            Fmt.write(1, cols - left_size - 3, Sentence().addf("r", f" {GuiActions.tab} "))

        if Flags.skills.is_true():
            frame_skills = Frame(mid_y, cols - skills_sx).set_size(mid_sy, skills_sx).set_border_color(border_color)
            self.show_skills_bar(frame_skills)
