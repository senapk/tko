from tko.play.keys import GuiActions
from tko.game.xp import XP
from tko.settings.settings import Settings
from tko.util.text import Text
from tko.util.symbols import symbols
import os

from tko.play.fmt import Fmt
from tko.play.frame import Frame
from tko.play.border import Border
from tko.play.search import Search
from tko.play.language_setter import LanguageSetter
from tko.play.images import opening
from tko.play.floating import Floating
from tko.play.floating_manager import FloatingManager
from tko.play.flags import Flags, FlagsMan
from tko.play.tasktree import TaskTree, TaskAction

from tko.play.keys import GuiKeys
from tko.game.quest import Quest
from tko.game.task import Task
from tko.game.cluster import Cluster
from tko.play.task_graph import TaskGraph
from tko.play.week_graph import DailyGraph

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
        self.language = LanguageSetter(self.settings, self.rep, self.flagsman, self.fman)
        self.colors = self.settings.colors
        self.need_update = False

        self.app = Settings().app

    def set_need_update(self):
        self.need_update = True

    def get_help_fixed(self):
        color = "W"
        try:
            selected = self.tree.get_selected_throw()
            if isinstance(selected, Task):
                color = "Y"
        except IndexError:
            pass
        act_color, act_text = self.get_activate_label()
        help_fixed: list[Text] = [
            Text().addf("C", f"{GuiActions.move} [{GuiKeys.up}{GuiKeys.left}{GuiKeys.down}{GuiKeys.right}]"),
            Text().addf("C", f"{GuiActions.config} [{GuiKeys.palette}]"),
            Text().addf(act_color, f"{act_text} [↲]"),
            Text().addf("G", f"{GuiActions.search} [{GuiKeys.search}]"),
            Text().addf(color, f"{GuiActions.edit} [{GuiKeys.edit}]"),
            Text().addf(color, f"{GuiActions.grade} [{GuiKeys.grade_play}]"),
        ]
        return help_fixed

    def get_activate_label(self) -> tuple[str, str]:
        try:
            obj = self.tree.get_selected_throw()
        except IndexError:
            return "R", " Retornar"
        if isinstance(obj, Quest):
            quest: Quest = obj
            if Flags.quests.get_value() != "2" and not quest.is_reachable():
                output = TaskAction.BLOQUEIO
            elif quest.key in self.tree.expanded:
                output = TaskAction.CONTRAIR
            else:
                output = TaskAction.EXPANDIR
            return "Y", output
        elif isinstance(obj, Cluster):
            cluster: Cluster = obj
            if cluster.key in self.tree.expanded:
                output = TaskAction.CONTRAIR
            else:
                output = TaskAction.EXPANDIR
            return "Y", output
        elif isinstance(obj, Task):
            color, output = self.tree.get_task_action(obj)
            return color, output
        return "R", " ERRO"

    @staticmethod
    def get_admin_color() -> str:
        if Flags.quests.get_value() == "0":
            return "g"
        if Flags.quests.get_value() == "1":
            return "y"
        return "c"

    @staticmethod
    def center_header_footer(value: Text, frame: Frame) -> Text:
        half = value.len() // 2
        x = frame.get_x()
        _, dx = Fmt.get_size()
        color = Gui.get_admin_color()
        full = Text().addf(color, "─" * ((dx//2) - x - 2 - half)).add(value)
        return full

    def show_main_bar(self, frame: Frame):
        color = self.settings.colors.filters
        top = Text()

        graph: str = f"Gráficos [{GuiKeys.graph}]"
        for i in range(2):
            if Flags.graph.get_value() == str(i):
                graph += symbols.closed_circle.text
            else:
                graph += symbols.open_circle.text
        top.add(self.style.border(color, graph))

        trilhas: str = (f"Trilhas[{GuiKeys.tracks}]")
        for i in range(3):
            if Flags.tracks.get_value() == str(i):
                trilhas += symbols.closed_circle.text
            else:
                trilhas += symbols.open_circle.text
        top.add(self.style.border(color, trilhas))

        quests: str = f"Tópicos [{GuiKeys.show_quests}]"
        for i in range(3):
            if Flags.quests.get_value() == str(i):
                quests += symbols.closed_circle.text
            else:
                quests += symbols.open_circle.text
        top.add(self.style.border(color, quests))

        tasks: str = f"Tarefas [{GuiKeys.show_tasks}]"
        for i in range(3):
            if Flags.tasks.get_value() == str(i):
                tasks += symbols.closed_circle.text
            else:
                tasks += symbols.open_circle.text
        top.add(self.style.border(color, tasks))
        


        # full = self.center_header_footer(top, frame)
        frame.set_header(top, "^")
        # footer            
        text = Text()
        alias_color = "R"
        dirname: str = self.rep.paths.get_rep_dir()
        dirname = os.path.basename(dirname).upper()
        text.add(self.style.border(alias_color, dirname))
        text.add(self.style.border("G", self.rep.get_lang().upper()))
        if self.need_update:
            text = Text().addf("r", " TKO DESATUALIZADO!").addf("y"," Atualize com: ").addf("g", "pipx upgrade tko ")
        text = self.center_header_footer(text, frame)
        frame.set_footer(text, "<")
        
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



    def show_skills_bar(self, frame_xp: Frame):
        dy, dx = frame_xp.get_inner()
        reachable_quests = [q for q in self.game.quests.values() if q.is_reachable()]
        obtained, priority, complete = self.game.get_skills_resume(reachable_quests)

        frame_xp.set_header(Text().addf("/", "Trilhas"), "^", "{", "}")
        frame_xp.draw()

        elements: list[Text] = []
        for skill, value in complete.items():
            if Flags.tracks.get_value() == "1":
                obtained_value = int(100 * obtained.get(skill, 0) / priority.get(skill, 1))
                possible_value = int(100 * value / priority.get(skill, 1))
                text = f"{skill}: {obtained_value:03d}%  {possible_value:03d}%"
            else:
                obtained_value = round(obtained.get(skill, 0))
                priority_value = round(priority.get(skill, 0))
                complete_value = round(value)
                text = f"{skill}:{obtained_value:03d}/{priority_value:03d}/{complete_value:03d}"
                # text = f"{skill}:{round(obtained.get(skill, 0))}/{round(value)}"
            perc = obtained.get(skill, 0) / priority.get(skill, 1)
            done_color = self.colors.progress_skill_done
            todo_color = self.colors.progress_skill_todo
            text = text.rjust(dx - 4)
            skill_bar = self.style.build_bar(text=text, percent=perc, length=dx - 2, fmt_true=done_color, fmt_false=todo_color)
            elements.append(skill_bar)
        
        # Total bar
        total_obtained, total_priority, total_complete = self.game.sum_xp(obtained, priority, complete)
        if total_priority == 0:
            grade = 0
        else:
            grade = total_obtained / total_priority * 10.0

        if Flags.tracks.get_value() == "1":
            text = f" Nota: {grade:.1f}       "
        else:
            text = f"Nota: {grade:.1f} :{round(total_obtained):03d}/{round(total_priority):03d}/{round(total_complete):03d}"
        text = text.rjust(dx - 4)
        done_color = self.colors.main_bar_done
        todo_color = self.colors.main_bar_todo
        percent = total_obtained / total_priority if total_priority > 0 else 0.0
        total_bar = self.style.build_bar(text, percent , dx - 2, done_color, todo_color)
        elements.append(total_bar)

        # printing calculating line breaks
        line_breaks = dy - len(elements)
        for skill_bar in elements:
            frame_xp.print(1, skill_bar)
            if line_breaks > 0:
                line_breaks -= 1
                frame_xp.print(1, Text())


    def build_list_sentence(self, items: list[Text]) -> list[Text]:
        out: list[Text] = []
        for x in items:
            color_ini = x.data[0].fmt
            color_end = x.data[-1].fmt
            left = self.style.round_l(color_ini)
            right = self.style.round_r(color_end)
            middle = x.clone()
            if x.data[0].text == "!":
                left = self.style.sharp_l(color_ini)
                right = self.style.sharp_r(color_end)
                middle.data = x.data[1:]
            out.append(Text().add(left).add(middle).add(right))
        return out

    def build_bottom_array(self):
        array: list[Text] = []
        array += self.get_help_fixed()
        return self.build_list_sentence(array)

    def show_bottom_bar(self):
        lines, cols = Fmt.get_size()
        elems = self.build_bottom_array()
        line_main = Text().add(" ").join(elems) # alignment adjust
        Fmt.write(lines - 1, 0, line_main.center(cols))

    def make_xp_button(self, size: int):
        if self.search.search_mode:
            text = " Busca: " + self.tree.search_text + symbols.cursor.text
            percent = 0.0
            done_color = "W"
            todo_color = "W"
            text = text.ljust(size)
            return self.style.build_bar(text, percent, len(text), done_color, todo_color)
            # text, percent = self.build_xp_bar()
            # done_color = self.colors.main_bar_done
            # todo_color = self.colors.main_bar_todo
            # text = text.center(size)
            # xpbar = self.style.build_bar(text, percent, len(text), done_color, todo_color)

        reachable_quests = [q for q in self.game.quests.values() if q.is_reachable()]
        obtained, priority, complete = self.game.get_skills_resume(reachable_quests)

        keys_to_remove: list[str] = []
        for skill, value in obtained.items():
            if value < 1:
                keys_to_remove.append(skill)
        for key in keys_to_remove:
            if key in obtained:
                del obtained[key]
            if key in priority:
                del priority[key]
            if key in complete:
                del complete[key]

        qtd = len(obtained)
        if qtd == 0:
            text = " Nenhuma habilidade disponível "
            percent = 0.0
            return self.style.build_bar(text, percent, size, "W", "W")
        
        skill_size = int(size / qtd)

        elements: list[Text] = []
        for skill, _ in complete.items():
            text = f"{skill}"
            perc = obtained.get(skill, 0) / priority.get(skill, 1)
            done_color = self.colors.main_bar_done
            todo_color = self.colors.main_bar_todo
            # text = text.rjust(skill_size - 4)
            skill_bar = self.style.build_bar(text=text, percent=perc, length=skill_size - 2, fmt_true=done_color, fmt_false=todo_color, rounded=False)
            elements.append(skill_bar)
        cover_color = 'K'
        xpbar = Text().add(self.style.round_l(cover_color)).addf(cover_color.lower(), '█')
        for skill_bar in elements:
            xpbar.add(skill_bar).addf(cover_color.lower(), '█')
        xpbar.add(self.style.round_r(cover_color))

        return xpbar

    def show_top_bar(self, frame: Frame):
        lista = [
            Text().addf('Y', f"Sair [q]"),
            Text().addf("Y", f"Ajuda[?]"),
        ]
        help_list = self.build_list_sentence(lista)
        pre: list[Text] = [help_list[0]]
        pos: list[Text] = [help_list[1]]

        limit = frame.get_dx()
        size = limit - Text().add(" ").join(pre + pos).len() - 2
        main_label = self.make_xp_button(size)
        info = Text().add(" ").join(pre + [main_label] + pos)
        frame.write(0, 0, info.center(frame.get_dx()))

    def show_help(self):
        # def empty(value):
        #     pass
        _help: Floating = Floating(self.settings, "v>").set_text_ljust()
        self.fman.add_input(_help)

        _help.set_header_text(Text().add(" Ajuda "))
        _help.put_sentence(Text.format("    Ajuda ").addf("r", GuiKeys.key_help).add("  Abre essa tela de ajuda")
        )

        _help.put_sentence(Text.format("  ").addf("r", "Shift + B")
                           .add("  Habilita ").addf("r", "").addf("R", "ícones").addf("r", "").add(" se seu ambiente suportar"))
        _help.put_sentence(Text() + "  " + Text.r_token("g", "setas") + "      Para navegar entre os elementos")
        _help.put_sentence(Text() + "   " + Text.r_token("g", f"{GuiKeys.left}{GuiKeys.down}{GuiKeys.up}{GuiKeys.right}") + "      Para navegar entre os elementos")
    
        _help.put_sentence(Text() + f"   {GuiActions.config} " + Text.r_token("r", f"{GuiKeys.palette}") + "  Abre o menu de ações e configurações")
        _help.put_sentence(Text() + f"   {GuiActions.github} " + Text.r_token("r", f"{GuiKeys.open_url}") + "  Abre tarefa em uma aba do browser")
        _help.put_sentence(Text() + f"   {GuiActions.download} " + Text.r_token("r", f"{GuiKeys.down_task}") + "  Baixa tarefa de código para seu dispositivo")
        _help.put_sentence(Text() + f"   {GuiActions.edit} " + Text.r_token("r", f"{GuiKeys.edit}") + "  Abre os arquivos no editor de código")
        _help.put_sentence(Text() + f"   {GuiActions.activate} " + Text.r_token("r", "↲") + "  Interage com o elemento de acordo com o contexto")
        _help.put_sentence(Text() + "             (baixar, visitar, escolher, compactar, expandir)")
        _help.put_sentence(Text() + f"  {GuiActions.grade} " + Text.r_token("r", GuiKeys.grade_play) + "  Abre tela para auto avaliação")
        _help.put_sentence(Text() + f"    {GuiActions.search} " + Text.r_token("r", f"{GuiKeys.search}") + "  Abre a barra de pesquisa")

        _help.put_sentence(Text())
        _help.put_sentence(Text() + "Você pode mudar o editor padrão com o comando")
        _help.put_sentence(Text() + Text.r_token("g", "             tko config --editor <comando>"))


    # def build_xp_bar(self) -> tuple[str, float]:
    #     xp = XP(self.game)
    #     available = xp.get_xp_total_available()
    #     if 0 < available == xp.get_xp_total_obtained():
    #         text = "Você atingiu o máximo de xp!"
    #         percent = 100.0
    #     else:
    #         # lang = self.rep.get_lang().upper()
    #         level = xp.get_level()
    #         percent = float(xp.get_xp_level_current()) / float(xp.get_xp_level_needed())
    #         if Flags.percent:
    #             xpobt = int(100 * xp.get_xp_level_current() / xp.get_xp_level_needed())
    #             text = "Level:{} XP:{}%".format(level, xpobt)
    #         else:
    #             xpobt1 = round(xp.get_xp_level_current())
    #             xpobt2 = round(xp.get_xp_level_needed())
    #             text = "Level:{} XP:{}/{}".format(level, xpobt1, xpobt2)

    #     return text, percent

    def get_task_graph(self, task_key: str, width: int, height: int) -> tuple[bool, list[Text]]:
        tg = TaskGraph(self.settings, self.rep, task_key, width, height)
        if len(tg.collected_rate) == 1:
            return False, []
        graph = tg.get_graph()
        # for y, line in enumerate(graph):
        #     frame.write(y, x, Text().addf("g", line))
        return True, graph

    def get_daily_graph(self, width: int, height: int) -> tuple[bool, list[Text]]:
        graph = DailyGraph(self.rep.logger, width, height).get_graph()
        if len(graph) == 0:
            return False, []
        # for y, line in enumerate(graph):
        #     frame.write(y, x, Text().addf("g", line))
        return True, graph

    def show_graphs(self, frame: Frame):
        lines, cols = frame.get_inner()
        
        # now: datetime.datetime = datetime.datetime.now()
        # parrot = random_get(opening, str(now.hour))
        distance = 18
        made = False
        list_data: list[Text] = []
        try:
            selected = self.tree.get_selected_throw()
        except IndexError:
            selected = None
        width = cols - self.tree.max_title - distance - 7
        if width < 5:
            width = 5
        if Flags.graph.get_value() == "1":
            height = lines - 4
            if height < 3:
                height = 3
            if isinstance(selected, Task):
                made, list_data = self.get_task_graph(selected.key, width, height)
            elif isinstance(selected, Cluster) or isinstance(selected, Quest):
                made, list_data = self.get_daily_graph(width, height)
        if not made:
            list_data = [Text().add(x) for x in opening["estuda"].splitlines()]
        for y, line in enumerate(list_data):
            frame.write(y, self.tree.max_title + distance, line)

    def show_items(self):
        border_color = self.get_admin_color()
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
        left_size = 29
        skills_sx = 0
        flags_sx = 0
        if Flags.tracks.get_value() != "0":
            skills_sx = left_size #max(20, main_sx // 4)
        
        task_sx = main_sx - flags_sx - skills_sx

        frame_top = Frame(top_y, 0).set_size(top_dy + 2, cols)
        self.show_top_bar(frame_top)

        # frame_bottom = Frame(lines - bottom_dy - 1, -1).set_size(bottom_dy + 2, cols + 2)
        self.show_bottom_bar()
        # if task_sx > 5: 
        frame_main = Frame(mid_y, 0).set_size(mid_sy, task_sx).set_border_color(border_color)
        self.show_main_bar(frame_main)
        self.show_graphs(frame_main)

        if Flags.tracks.get_value() != "0":
            frame_skills = Frame(mid_y, cols - skills_sx).set_size(mid_sy, skills_sx).set_border_color(border_color)
            self.show_skills_bar(frame_skills)
