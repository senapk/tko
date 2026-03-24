from tko.play.keys import GuiActions
from tko.settings.settings import Settings
from tko.util.text import Text
from tko.util.symbols import symbols
from pathlib import Path

from tko.play.fmt import Fmt
from tko.play.frame import Frame
from tko.play.border import Border
from tko.play.search import Search
from tko.play.language_setter import LanguageSetter
from tko.play.images import opening
from tko.play.floating_manager import FloatingManager
from tko.play.flags import Flags, FlagsMan
from tko.play.tasktree import TaskTree, TaskAction

from tko.play.keys import GuiKeys
from tko.game.quest import Quest
from tko.game.task import Task
from tko.play.task_graph import TaskGraph
from tko.play.daily_graph import DailyGraph

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
        self.xray_offset = 0

        self.app = Settings().app

    def set_need_update(self):
        self.need_update = True

    def get_help_fixed(self):
        color = "W"
        try:
            selected = self.tree.get_selected_throw()
            if isinstance(selected, Task):
                color = "G"
        except IndexError:
            pass
        act_color, act_text = self.get_activate_label()
        help_fixed: list[Text] = [
            Text().addf('R', f"Sair [esc] "),
            Text().addf("C", f"Criar Rascunho [{GuiKeys.create_draft}]"),
            Text().addf("C", f"{GuiActions.pallete} [{GuiKeys.palette}]"),
            Text().addf("C", f"{GuiActions.calibrate} [{GuiKeys.calibrate}]"),
            Text().addf("G", f"{GuiActions.search} [{GuiKeys.search}]"),
            Text().addf(act_color, f"{act_text} [↲]"),
            Text().addf(color, f"{GuiActions.grade} [{GuiKeys.self_evaluate}]"),
        ]
        return help_fixed

    def get_activate_label(self) -> tuple[str, str]:
        try:
            obj = self.tree.get_selected_throw()
        except IndexError:
            return "R", " Retornar"
        if isinstance(obj, Quest):
            quest: Quest = obj
            if Flags.inbox.get_value() != Flags.inbox_all and not quest.is_reachable():
                output = TaskAction.BLOQUEIO
            elif quest.get_full_key() in self.tree.expanded:
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
        if Flags.inbox.get_value() == Flags.inbox_only:
            return "g"
        if Flags.inbox.get_value() == Flags.inbox_all:
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

    def get_lr(self, test: bool) -> tuple[str, str]:
        if test:
            return symbols.right_arrow_filled.text, symbols.left_arrow_filled.text
        else:
            return " ", " "

    def render_button(self, info: str, test: bool):
        left, right = self.get_lr(test)
        bg = "X" if test else ""
        return Text().addf(bg, left).addf(bg, info).addf(bg, right)

    def gen_right_header(self) -> Text:
        top = Text()
        if Flags.panel.get_value() == Flags.panel_graph:
            top.add(Text().add(" Gráficos "))
        elif Flags.panel.get_value() == Flags.panel_help:
            top.add(Text().add(" Help "))
        elif Flags.panel.get_value() == Flags.panel_skills:
            top.add(Text().add(" Trilhas "))
        elif Flags.panel.get_value() == Flags.panel_logs:
            top.add(Text().add(" Logs "))
        return top

    def show_main_bar(self, frame: Frame):
        dy, dx = frame.get_inner()
        top = Text()

        if self.search.search_mode:
            top = self.make_search_text(dx - 20)
        else:
            if Flags.inbox.get_value() == Flags.inbox_only:
                top.add(" Inbox ")
            else:
                top.add(" Todas as Tarefas ")
        
        # full = self.center_header_footer(top, frame)
        frame.set_header(top, "^", prefix="{", suffix= "}")
        # footer            
        text = Text()
        alias_color = "R"
        dirname: Path = self.rep.paths.get_workspace_dir()
        dirname_str = dirname.name.upper()
        text.add(self.style.border(alias_color, dirname_str))
        text.add(self.style.border("G", self.rep.data.lang.upper()))
        if self.need_update:
            text = Text().addf("r", " TKO DESATUALIZADO!").addf("y"," Atualize com: ").addf("g", "pipx upgrade tko ")
        # text = self.center_header_footer(text, frame)
        frame.set_footer(text, "^")
        
        # if Flags.flags:
        #     value = self.make_flags_bar()
        #     full = self.center_header_footer(value, frame)
        #     frame.set_footer(full, "<")
        frame.draw()

        values = self.tree.get_senteces(dy)
        for y, sentence in enumerate(values):
            if sentence.len() > dx:
                sentence.trim_end(dx - 3)
                sentence.addf("r", "...")
            frame.write(y, 0, sentence)

    def show_skills_bar(self, frame_xp: Frame):
        dy, dx = frame_xp.get_inner()
        #_ = [q for q in self.game.quests.values() if q.is_reachable()]
        obtained, priority, complete = self.game.get_skills_resume()

        frame_xp.set_header(Text().add(self.gen_right_header()), "^", prefix="{", suffix= "}")
        frame_xp.draw()

        elements: list[Text] = []
        for skill, value in complete.items():
            if Flags.show_panel.get_value() == "1":
                obtained_value = round(100 * obtained.get(skill, 0) / priority.get(skill, 1))
                possible_value = round(100 * value / priority.get(skill, 1))
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
            #text = text.rjust(dx - 4)
            skill_bar = self.style.build_bar(text=text, percent=perc, length=dx - 2, fmt_true=done_color, fmt_false=todo_color, rounded=False)
            elements.append(skill_bar)
        
        # Total bar
        total_obtained, total_priority, total_complete = self.game.sum_xp(obtained, priority, complete)
        if total_priority == 0:
            grade = 0
        else:
            grade = total_obtained / total_priority * 10.0

        if Flags.show_panel.get_value() == "1":
            text = f" Nota: {grade:.1f}       "
        else:
            text = f"Nota: {grade:.1f} :{round(total_obtained):03d}/{round(total_priority):03d}/{round(total_complete):03d}"
        # text = text.rjust(dx - 4)
        done_color = self.colors.main_bar_done
        todo_color = self.colors.main_bar_todo
        percent = total_obtained / total_priority if total_priority > 0 else 0.0
        total_bar = self.style.build_bar(text, percent , dx - 2, done_color, todo_color, rounded=False)
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

    def make_search_text(self, size: int):
        text = " Busca: " + self.tree.search_text + symbols.cursor.text
        text = text.ljust(size)
        return Text().addf("X", text)
    
    def make_xp_button(self, size: int):
        # if self.search.search_mode:
        #     return self.make_search_text(size)

        #reachable_quests = [q for q in self.game.quests.values() if q.is_reachable()]
        obtained, priority, complete = self.game.get_skills_resume()

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
            return self.style.build_bar(text, percent, size, "W", "W", rounded = False)
        
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
        panel_on = Flags.show_panel.is_true()
        pre = [
            self.render_button(f"Inbox[{GuiKeys.inbox}]", Flags.inbox.get_value() == Flags.inbox_only),
            self.render_button(f"Todas[{GuiKeys.all_tasks}]", Flags.inbox.get_value() == Flags.inbox_all)
        ]
        pos = [
            self.render_button(f"Gráficos[{GuiKeys.panel_graph}]", panel_on and Flags.panel.get_value() == Flags.panel_graph),
            self.render_button(f"Trilhas[{GuiKeys.panel_skills}]", panel_on and Flags.panel.get_value() == Flags.panel_skills),
            self.render_button(f"Logs[{GuiKeys.panel_logs}]", panel_on and Flags.panel.get_value() == Flags.panel_logs),
            self.render_button(f"Ajuda[{GuiKeys.panel_help}]", panel_on and Flags.panel.get_value() == Flags.panel_help),
        ]
        
        limit = frame.get_dx()
        # size = limit - Text().add("").join(pre + pos).len() - 2
        # main_label = self.make_xp_button(size).ljust(size, Text.Token(""))
        # info = Text().add("").join(pre + [main_label] + pos)
        info = Text().add("").join(pre + pos).center(limit)
        frame.write(0, 1, info)

    def show_help(self, frame: Frame):
        # def empty(value):
        #     pass

        frame.set_header(self.gen_right_header(), align="^", prefix="{", suffix= "}")
        frame.draw()
        dx = frame.get_dx() - 2
        help_lines: list[Text] = []
        help_lines.append(Text.format("{g}", " Configuração ").center(dx, Text.Token("-")))
        help_lines.append(Text.format("   Bordas {r} Habilita {r}{R}{r}", "B", "", "bordas redondas", ""))
        help_lines.append(Text.format(" Calibrar {r} Para calibrar os direcionais do teclado", GuiKeys.calibrate))

        help_lines.append(Text().addf("g", " Símbolos ").center(dx, Text.Token("-")))
        help_lines.append(Text.format("{g} Tarefa sugeridas, {w} Tarefa opcional", symbols.star_filled, symbols.star_open))
        help_lines.append(Text.format("{y} Tarefa de estudo com consulta permitida", symbols.task_repeat))
        help_lines.append(Text.format("{r} Tarefa de avaliação que precisa ser feita sem consulta", symbols.task_denied))
        help_lines.append(Text.format("{g} {g} {g} Autoavaliação feita, {w} {w} {w} Sem Autoavaliação", 
                                      symbols.circle_filled, symbols.square_filled, symbols.task_human_filled,
                                      symbols.circle_open, symbols.square_filled, symbols.task_human_open))
        help_lines.append(Text.format("{g} Nota por testes, {w} Nota manual por critério, {w} Checkbox apenas", 
                                      symbols.circle_open, symbols.task_human_open, symbols.square_open))
        
        help_lines.append(Text.format("{g}", " Navegação ").center(dx, Text.Token("-")))
        help_lines.append(Text.format("  setas {r} Para navegar entre os elementos", "↑↓→"))
        help_lines.append(Text.format("    Enter {r} Interage com o elemento de acordo com o contexto", "↲"))
        help_lines.append(Text().addf("g", " Interface ").center(dx, Text.Token("-")))
        help_lines.append(Text.format("    Inbox {r} Mostra as tarefas sugeridas e iniciadas", GuiKeys.inbox))
        help_lines.append(Text.format("    Todas {r} Mostra as todas tarefas cadastradas", GuiKeys.all_tasks))
        help_lines.append(Text.format("   Paleta {r} Abre o menu de ações e configurações", GuiKeys.palette))
        help_lines.append(Text.format("    Tempo {r} Mostrar/Oculta o tempo gasto nas tarefas", GuiKeys.show_duration))
        help_lines.append(Text.format("    Busca {r} Abre a barra de pesquisa", GuiKeys.search))

        help_lines.append(Text().addf("g", " Tarefas ").center(dx, Text.Token("-")))
        help_lines.append(Text.format(" Download {r} Baixa novamente a tarefa selecionada", GuiKeys.down_task))
        help_lines.append(Text.format("   Apagar {r} Apaga a pasta da tarefa selecionada", GuiKeys.delete_folder))
        help_lines.append(Text.format(" Rascunho {r} Cria um rascunho para escrever código ou anotações", GuiKeys.create_draft))
        help_lines.append(Text.format("Avaliação {r} Abre tela para auto avaliação", GuiKeys.self_evaluate))

        help_lines.append(Text.format("{g}", " Editor padrão ").center(dx, Text.Token("-")))
        help_lines.append(Text().add(" O comando de edição padrão abre pastas e arquivos no vscode"))
        help_lines.append(Text().add(" Se quiser mudar o editor, basta definir o novo comando padrão"))
        help_lines.append(Text().addf("y", "tko config set --editor <comando>").center(dx))

        for i, line in enumerate(help_lines):
            frame.write(i, 0, line)

    def get_task_graph(self, task_key: str, width: int, height: int) -> tuple[bool, list[Text], list[Text]]:
        tg = TaskGraph(self.settings, self.rep, task_key, width, height)
        header, graph = tg.get_output()
        if len(graph) == 0:
            return False, [], []
        # for y, line in enumerate(graph):
        #     frame.write(y, x, Text().addf("g", line))
        return True, header, graph

    def get_daily_graph(self, width: int, height: int) -> tuple[bool, list[Text]]:
        graph = DailyGraph(self.rep.logger, width, height).get_graph()
        if len(graph) == 0:
            return False, []
        # for y, line in enumerate(graph):
        #     frame.write(y, x, Text().addf("g", line))
        return True, graph


    def show_graphs(self, frame: Frame):
        
        try:
            selected = self.tree.get_selected_throw()
        except IndexError:
            selected = None

        lines, cols = frame.get_inner()
        
        # now: datetime.datetime = datetime.datetime.now()
        # parrot = random_get(opening, str(now.hour))
        keep_borders = False
        made = False
        list_data: list[Text] = []
        width = cols - 2
        if width < 5:
            width = 5
        header: list[Text] = []
        if Flags.panel.get_value() in (Flags.panel_graph, Flags.panel_logs):
            height = lines - 4
            if height < 3:
                height = 3
            if isinstance(selected, Task):
                made, header, list_data = self.get_task_graph(selected.get_full_key(), width, height)
            elif isinstance(selected, Quest):
                made, list_data = self.get_daily_graph(width, height)
        if not made:
            list_data = [Text().add(x).rjust(width) for x in opening["parrot"].splitlines()]
            keep_borders = True
        if self.xray_offset < 0:
            self.xray_offset = 0
        if self.xray_offset >= len(list_data):
            self.xray_offset = len(list_data) - 1
        
        offset = 0
        
        if Flags.panel.get_value() == Flags.panel_logs and isinstance(selected, Task):
            offset = self.xray_offset
            keep_borders = True
        count = -1
        line_count = 0
        
        if not keep_borders:
            frame.set_border_none()

        frame.set_header(self.gen_right_header(), "^", prefix="{", suffix= "}")
        frame.draw()
        if header:
            for y, line in enumerate(header):
                frame.write(y, 0, line)
            line_count = len(header)
        for line in list_data:
            count += 1
            if count < offset:
                continue
            frame.write(line_count, 0, line)
            line_count += 1

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
        # left_size = 29

        right_sx = 0
        if Flags.show_panel.is_true():
            right_sx = cols - self.tree.get_total_width() - 1
            if right_sx > cols // 2:
                right_sx = cols // 2
        
        task_sx = main_sx - right_sx

        frame_top = Frame(top_y, 0).set_size(top_dy + 2, cols)
        self.show_top_bar(frame_top)

        # frame_bottom = Frame(lines - bottom_dy - 1, -1).set_size(bottom_dy + 2, cols + 2)
        self.show_bottom_bar()
        # if task_sx > 5: 
        frame_main = Frame(mid_y, 0).set_size(mid_sy, task_sx).set_border_color(border_color)
        self.show_main_bar(frame_main)
        # self.show_graphs(frame_main)

        if Flags.show_panel.is_true():
            frame_right = Frame(mid_y, cols - right_sx).set_size(mid_sy, right_sx).set_border_color(border_color)
            if Flags.panel.get_value() == Flags.panel_skills:
                self.show_skills_bar(frame_right)
            elif Flags.panel.get_value() in [Flags.panel_logs, Flags.panel_graph]:
                self.show_graphs(frame_right)
            elif Flags.panel.get_value() == Flags.panel_help:
                self.show_help(frame_right)
