from tko.play.keys import GuiActions
from tko.settings.settings import Settings
from tko.util.text import Text
from tko.util.symbols import Symbols
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
from tko.util.visual import Visual
from tko.settings.settings import Settings
from tko.settings.app_settings import AppSettings

class Gui:

    def __init__(self, settings: Settings, tree: TaskTree, flagsman: FlagsMan, fman: FloatingManager):
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

        self.app: AppSettings = self.settings.app

    def set_need_update(self):
        self.need_update = True


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
    def get_frame_color() -> str:
        if Flags.inbox.get_value() == Flags.inbox_only:
            return "g"
        if Flags.inbox.get_value() == Flags.inbox_all:
            return "y"
        return ""

    @staticmethod
    def center_header_footer(value: Text, frame: Frame) -> Text:
        half = value.len() // 2
        x = frame.get_x()
        _, dx = Fmt.get_size()
        color = Gui.get_frame_color()
        full = Text().addf(color, "─" * ((dx//2) - x - 2 - half)).add(value)
        return full

    def show_left_panel(self, frame: Frame):
        dy, dx = frame.get_inner()
        top = Text()

        if self.search.search_mode:
            top = self.make_search_text(dx - 20)
        else:
            top = Text.format(" {} ", self.rep.data.lang.upper())
        frame.set_header(top, "<", prefix="{", suffix="}")
        
        dirname: Path = self.rep.paths.get_workspace_dir()
        dirname_str = dirname.name.upper()
        
        text = Text.format(" {} ", dirname_str)
        if self.need_update:
            text = Text().addf("r", " TKO DESATUALIZADO!").addf("y"," Atualize com: ").addf("g", "pipx upgrade tko ")
        frame.set_footer(text, "<", prefix="{", suffix="}")
        frame.draw()

        values = self.tree.get_senteces(dy)
        for y, sentence in enumerate(values):
            if sentence.len() > dx:
                sentence.trim_end(dx - 1)
                sentence.addf("r", "…")
            frame.write(y, 0, sentence)

    def show_skills_bar(self, frame_xp: Frame):
        dy, dx = frame_xp.get_inner()
        #_ = [q for q in self.game.quests.values() if q.is_reachable()]
        obtained, priority, complete = self.game.get_skills_resume()
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

    def show_bottom_bar(self):
        lines, cols = Fmt.get_size()
        self_color = "X"
        try:
            selected = self.tree.get_selected_throw()
            if isinstance(selected, Task):
                self_color = "G"
        except IndexError:
            pass
        act_color, act_text = self.get_activate_label()
        help_fixed: list[Text] = [
            Text().addf('R', f" Sair [esc] "),
            Text().addf("C", f" Criar Rascunho [{GuiKeys.create_draft}] "),
            Text().addf("C", f" {GuiActions.pallete} [{GuiKeys.palette}] "),
            Text().addf("G", f" {GuiActions.search} [{GuiKeys.search}] "),
            Text().addf(act_color, f" {act_text} [↲] "),
            Text().addf(self_color, f" {GuiActions.grade} [{GuiKeys.self_evaluate}] "),
        ]
        line_main = Text().add(" ").join(help_fixed) # alignment adjust
        Fmt.write(lines - 1, 0, line_main.center(cols))

    def make_search_text(self, size: int):
        text = " Busca: " + self.tree.search_text + Symbols.cursor
        text = text.ljust(size)
        return Text().add(text)
    
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
        vi = Visual(self.settings.app.use_borders)
        pre = [
            vi.render_button(f"Inbox[{GuiKeys.inbox}]", Flags.inbox.get_value() == Flags.inbox_only),
            vi.render_button(f"Todas[{GuiKeys.all_tasks}]", Flags.inbox.get_value() == Flags.inbox_all),
            Text().add(" ")
        ]
        pos = [
            vi.render_button(f"Gráficos[{GuiKeys.panel_graph}]", panel_on and Flags.panel.get_value() == Flags.panel_graph),
            vi.render_button(f"Logs[{GuiKeys.panel_logs}]", panel_on and Flags.panel.get_value() == Flags.panel_logs),
            vi.render_button(f"Trilhas[{GuiKeys.panel_skills}]", panel_on and Flags.panel.get_value() == Flags.panel_skills),
            vi.render_button(f"Ajuda[{GuiKeys.panel_help}]", panel_on and Flags.panel.get_value() == Flags.panel_help),
        ]
        last = [
            vi.render_button("Exec[PageUp]", Flags.task_graph_mode.get_value() == Flags.task_exec_view),
            vi.render_button("Time[PgDown]", Flags.task_graph_mode.get_value() == Flags.task_time_view),
        ]
        
        limit = frame.get_dx()
        extra = Text()
        if Flags.panel.get_value() == Flags.panel_graph:
            extra = Text().add("").join(last)

        info = Text().add("").join(pre + pos)
        info = Text().add(" " * ((limit - len(info)) // 2)).add(info)
        info += Text().add(" " * (limit - len(info) - len(extra))).add(extra)
        # info = info.ljust((limit - len(info))//2).add(" " * (limit - len(extra))).add(extra)
        frame.write(0, 1, info)

    def show_help(self, frame: Frame):
        frame.draw()
        dx = frame.get_dx() - 2
        help_lines: list[Text] = []
        help_lines.append(Text.format("{g}", " Configuração ").center(dx, Text.Token("-")))
        help_lines.append(Text.format("   Bordas {r} Habilita {r}{R}{r}", "B", "", "bordas redondas", ""))
        help_lines.append(Text.format(" Calibrar {r} Para calibrar os direcionais do teclado", GuiKeys.calibrate))

        help_lines.append(Text().addf("g", " Símbolos ").center(dx, Text.Token("-")))
        help_lines.append(Text.format("{y}   Tarefa sugeridas        , {} Tarefa opcional", Symbols.star_filled, Symbols.star_void))
        help_lines.append(Text.format("{g}   Pode consultar e refazer, {r} Fazer sozinho sem consulta", Symbols.task_reload, Symbols.task_zero))
        help_lines.append(Text.format("{g}{g}{g} Fez Autoavaliação       , {}{}{} Sem Autoavaliação", 
                                      Symbols.right_triangle_filled, Symbols.down_triangle_filled, Symbols.task_view,
                                      Symbols.right_triangle_void, Symbols.square_void, Symbols.task_view))
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
        help_lines.append(Text().add(" Para mudar o editor padrão para abrir arquivos use o comando"))
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

    def get_daily_graph(self, width: int, height: int) -> tuple[bool, list[Text], list[Text]]:
        header, graph = DailyGraph(self.rep.logger, width, height).get_graph()
        if len(graph) == 0:
            return False, [], []
        # for y, line in enumerate(graph):
        #     frame.write(y, x, Text().addf("g", line))
        return True, header, graph

    def show_graphs(self, frame: Frame):
        try:
            selected = self.tree.get_selected_throw()
        except IndexError:
            selected = None

        lines, cols = frame.get_inner()
        made = False
        list_data: list[Text] = []
        width = cols - 2
        if width < 5:
            width = 5
        header: list[Text] = []
        if Flags.panel.get_value() in (Flags.panel_graph, Flags.panel_logs):
            height = lines - 2
            if height < 3:
                height = 3
            if isinstance(selected, Task):
                made, header, list_data = self.get_task_graph(selected.get_full_key(), width, height)
            elif isinstance(selected, Quest) and Flags.panel.get_value() == Flags.panel_graph:
                made, header, list_data = self.get_daily_graph(width, height)
        if not made:
            list_data = [Text().add(x).rjust(width) for x in opening["parrot"].splitlines()]
            # keep_borders = True
        if self.xray_offset < 0:
            self.xray_offset = 0
        if self.xray_offset >= len(list_data):
            self.xray_offset = len(list_data) - 1
        
        offset = 0
        
        if Flags.panel.get_value() == Flags.panel_logs and isinstance(selected, Task):
            offset = self.xray_offset
            # keep_borders = True
        line_count = 0
        
        dy, _ = frame.get_inner()
        if Flags.panel.get_value() == Flags.panel_logs:
            if header:
                frame.set_header(Text().add(" Scroll Up[PageUp]  ScrollDown[PgDown] "), "^")
                frame.set_footer(Text().add(" ").add(header[0]), "^")

            count = -1
            line_count = 0
            for line in list_data:
                count += 1
                if count < offset:
                    continue
                if line_count > dy - 1:
                    break
                frame.write(line_count, 0, line)
                line_count += 1

        else:
            if header:
                frame.set_footer(Text().add(" ").add(header[0]), "^")
            count = -1
            line_count = 0
            for line in list_data:
                count += 1
                if count < offset:
                    continue
                frame.write(line_count, 0, line)
                line_count += 1
 
        frame.draw()

    def show_items(self):
        border_color = self.get_frame_color()
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
            right_sx = round(cols * (100 - self.settings.app.panel_size_percent) / 100.0)
        
        task_sx = main_sx - right_sx

        frame_top = Frame(top_y, 0).set_size(top_dy + 2, cols)
        self.show_top_bar(frame_top)

        if Flags.show_panel.is_true():
            frame_right =  Frame(mid_y, cols - right_sx).set_size(mid_sy, right_sx).set_border_color(self.get_frame_color())
            if Flags.panel.get_value() == Flags.panel_skills:
                self.show_skills_bar(frame_right)
            elif Flags.panel.get_value() == Flags.panel_graph:
                self.show_graphs(frame_right)
            elif Flags.panel.get_value() == Flags.panel_logs:
                self.show_graphs(frame_right)
            elif Flags.panel.get_value() == Flags.panel_help:
                self.show_help(frame_right)
        # precisam ser desenhados após o panel do graphs
        frame_main = Frame(mid_y, 0).set_size(mid_sy, task_sx).set_border_color(border_color).set_border_color(self.get_frame_color())
        self.show_left_panel(frame_main)
        self.show_bottom_bar()
