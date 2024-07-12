from ..game.game import Game
from ..game.cluster import Cluster
from ..game.quest import Quest
from ..game.task import Task
from ..game.xp import XP
from ..game.graph import Graph

from typing import List, Any, Dict
from ..settings.settings import RepSettings, GeralSettings
from ..down import Down
from ..util.ftext import FF, TK, TR
from .style import Style
from .fmt import Fmt
from .frame import Frame

from .floating import Floating
from .floating_manager import FloatingManager
from .flags import Flag, Flags, FlagsMan
from .tasktree import TaskTree, Entry

import webbrowser
import os
import curses


class Play:

    def __init__(
        self,
        local: GeralSettings,
        game: Game,
        rep: RepSettings,
        rep_alias: str,
        fn_save,
    ):
        self.fn_save = fn_save
        self.local = local
        self.rep_alias = rep_alias
        self.rep = rep
        self.exit = False

        self.flagsman = FlagsMan(self.rep.get(RepSettings.flags))
        self.rep.lang = self.rep.get(RepSettings.lang)
        self.game: Game = game
        self.fman = FloatingManager()
        self.tree = TaskTree(local, game, rep, rep_alias)

        self.first_loop = True
        self.graph_ext = ""

        self.help_base = [
            f"Quit[{self.Key.quit}]",
            f"Help[{self.Key.help}]",
            "Move[wasd]",
            "Mark[enter]",
        ]
        self.help_extra = [
            f"Open[{self.Key.open_link}]",
            f"Get[{self.Key.down_task}]",
            "Grade[0-9]",
            f"Lang[{self.Key.set_lang}]",
            f"Fold[{self.Key.collapse}{self.Key.expand}]",
            f"MassMark[{self.Key.mass_toggle}]",
            f"ResetColors[{self.Key.reset}]",
        ]

    def save_to_json(self):
        self.tree.save_on_rep()
        self.rep.set(RepSettings.flags, self.flagsman.get_data())
        self.rep.set(RepSettings.lang, self.rep.lang)

        self.fn_save()

    def set_rootdir(self):
        def chama(value):
            if value == "yes":
                self.local.rootdir = os.getcwd()
                self.fn_save()
                self.fman.add_input(
                    Floating()
                    .put_text("Diretório raiz definido como ")
                    .put_text("  " + self.local.rootdir)
                    .put_text("Você pode alterar o diretório raiz navegando para o")
                    .put_text("diretório desejado e executando o comando")
                    .put_text("  tko config --root")
                    .put_text("")
                    .set_exit_fn(self.set_language)
                    .warning()
                )
            else:
                self.fman.add_input(
                    Floating()
                    .put_text("Navague para o diretório desejado e execute o comando")
                    .put_text("  tko config --root")
                    .put_text("ou rode o tko play novamente na pasta desejada")
                    .warning()
                )

        self.fman.add_input(
            Floating()
            .put_text("Diretório raiz para o tko ainda não foi definido")
            .put_text("Você deseja utilizar o diretório atual")
            .put_text(os.getcwd())
            .put_text("como raiz para o repositório de " + self.rep_alias + "?")
            .set_options(["yes", "no"])
            .answer(chama)
        )

    def set_language(self):

        def back(value):
            self.rep.lang = value
            self.fn_save()
            self.fman.add_input(
                Floating()
                .put_text("Linguagem alterada para " + value)
                .put_text("Você pode mudar a linguagem")
                .put_text("de programação apertando")
                .put_sentence(FF() + TR("G", "l"))
                .warning()
            )

        self.fman.add_input(
            Floating()
            .put_text("   Escolha a extensão")
            .put_text(" default para os rascunhos")
            .put_text("")
            .put_text(" Selecione e tecle enter")
            .set_options(["c", "cpp", "py", "ts", "js", "java", "hs"])
            .answer(back)
        )

    def process_down(self):
        if self.local.rootdir == "":
            self.set_rootdir()
            return

        if self.rep.lang == "":
            self.set_language()
            return

        rootdir = os.path.relpath(os.path.join(self.local.rootdir, self.rep_alias))
        obj = self.tree.get_selected()
        self.down_task(rootdir, obj, self.rep.lang)

    def open_link(self):
        obj = self.tree.get_selected()
        if isinstance(obj, Task):
            task: Task = obj
            if task.link.startswith("http"):
                webbrowser.open_new_tab(task.link)
            self.fman.add_input(
                Floating()
                .set_header(" Abrindo link ")
                .put_text(task.link)
                .warning()
            )
        elif isinstance(obj, Quest):
            self.fman.add_input(
                Floating()
                .put_text("Essa é uma missão")
                .put_text("você só pode abrir o link")
                .put_text("de tarefas")
                .error()
            )
        else:
            self.fman.add_input(
                Floating()
                .put_text("Esse é um grupo")
                .put_text("você só pode abrir o link")
                .put_text("de tarefas")
                .error()
            )

    def generate_graph(self):
        if not self.first_loop:
            return
        if self.graph_ext == "":
            return
        reachable: List[str] = [q.key for q in self.tree.available_quests]
        counts = {}
        for q in self.game.quests.values():
            done = len([t for t in q.get_tasks() if t.is_complete()])
            init = len([t for t in q.get_tasks() if t.in_progress()])
            todo = len([t for t in q.get_tasks() if t.not_started()])
            counts[q.key] = f"{done} / {done + init + todo}\n{q.get_percent()}%"

        mark_opt = Flags.dots.is_true()
        Graph(self.game).set_opt(mark_opt).set_reachable(reachable).set_counts(
            counts
        ).set_graph_ext(self.graph_ext).generate()
        lines, _cols = Fmt.get_size()
        if self.first_loop:
            text = FF().add(f"Grafo gerado em graph{self.graph_ext}")
            Fmt.write(lines - 1, 0, text)

    def down_task(self, rootdir, obj: Any, ext: str):
        if isinstance(obj, Task) and obj.key in obj.title:
            task: Task = obj
            down_frame = (
                Floating().warning().set_header(FF().add(" Baixando tarefa "))
            )
            down_frame.put_text(f"tko down {self.rep_alias} {task.key} -l {ext}")
            self.fman.add_input(down_frame)

            def fnprint(text):
                down_frame.put_text(text)
                down_frame.draw()
                Fmt.refresh()

            Down.download_problem(rootdir, self.rep_alias, task.key, ext, fnprint)
        else:
            if isinstance(obj, Quest):
                self.fman.add_input(
                    Floating()
                    .put_text("Essa é uma missão")
                    .put_text("você só pode baixar tarefas")
                    .error()
                )
            elif isinstance(obj, Cluster):
                self.fman.add_input(
                    Floating()
                    .put_text("Esse é um grupo")
                    .put_text("você só pode baixar tarefas")
                    .error()
                )
            else:
                self.fman.add_input(
                    Floating().put_text("Essa não é uma tarefa de código").error()
                )

    @staticmethod
    def build_list_sentence(items: List[str]) -> FF:
        _help = FF()
        try:
            for x in items:
                label, key = x.split("[")
                key = "[" + key
                _help.addf("/", label).add(key).add(" ")
        except ValueError:
            raise ValueError("Desempacotando mensagens")
        _help.data.pop()

        return _help

    def build_bar_links(self) -> str:
        obj = self.tree.items[self.tree.index_selected].obj
        if isinstance(obj, Task):
            link = obj.link
            if link:
                return link
        return ""

    def show_main_bar(self, frame: Frame):
        frame.set_header(
            FF().add("{").addf("/", f"Tarefas lang:{self.rep.lang}").add("}")
        )
        frame.set_footer(FF().add(self.build_bar_links()), ">", "{", "}")
        frame.draw()

        dy, dx = frame.get_inner()
        for y, sentence in enumerate(self.tree.get_senteces(dy)):
            frame.write(y, 0, sentence)

    def show_skills_bar(self, frame_xp):
        dy, dx = frame_xp.get_inner()
        xp = XP(self.game)
        total_perc = int(
            100 * (xp.get_xp_total_obtained() / xp.get_xp_total_available())
        )
        if Flags.percent.is_true():
            text = f" Total:{total_perc}%"
        else:
            text = f" Total:{xp.get_xp_total_obtained()}"

        done = "/k" + Flags.main_done.get_value()
        todo = "/k" + Flags.main_todo.get_value()
        total_bar = FF.build_bar(text, total_perc / 100, dx - 2, done, todo)
        frame_xp.set_header(FF().add("{").addf("/", "Skills").add("}"), "^")
        frame_xp.set_footer(FF().add(total_bar), "^")
        frame_xp.draw()

        total, obt = self.game.get_skills_resume()
        index = 0
        for skill, value in total.items():
            if Flags.percent.is_true():
                text = f"{skill}:{int(100 * obt[skill] / value)}%"
            else:
                text = f"{skill}:{obt[skill]}/{value}"

            perc = obt[skill] / value
            skill_bar = FF.build_bar(
                text,
                perc,
                dx - 2,
                "/k" + Flags.skill_done.get_value(),
                "/k" + Flags.skill_todo.get_value(),
            )
            frame_xp.write(index, 1, skill_bar)
            index += 2

    def show_flags_bar(self, frame: Frame):
        frame.set_header(FF().add("{").addf("/", "Flags").add("}"), "^")
        frame.draw()

        for flag in self.flagsman.left:
            if flag.is_bool():
                frame.print(0, flag.get_toggle_sentence(7))

    def show_color_bar(self, frame: Frame):
        frame.set_header(FF().add("{").addf("/", "Cores").add("}"), "^")
        frame.draw()

        for flag in self.flagsman.left:
            if not flag.is_bool():
                frame.print(0, flag.get_toggle_sentence())

    def show_help(self):
        _help: Floating = Floating().warning().set_ljust_text()
        self.fman.add_input(_help)
        _help.set_header(FF().addf("/", " Help "))
        _help.put_text("Controles")
        _help.put_text("  setas ou wasd   - Para navegar entre os elementos")
        _help.put_text("  enter ou espaço - Marcar ou desmarcar, expandir ou contrair")
        _help.put_text("  0 a 9 - Definir a nota parcial para uma tarefa")
        _help.put_text(f"      {self.Key.open_link} - Abrir tarefa em uma aba do browser")
        _help.put_text(
            f"      {self.Key.down_task} - Baixar um tarefa de código para seu dispositivo"
        )
        _help.put_text("")
        _help.put_text("Flags")
        _help.put_text("  Muda a forma de exibição dos elementos")
        _help.put_text("")
        _help.put_text("Extra")
        _help.put_text(
            f"  {self.Key.set_lang} - Mudar a linguagem de download dos rascunhos"
        )

    @staticmethod
    def disable_on_resize():
        lines, cols = Fmt.get_size()
        if cols < 50 and Flags.skills_bar.is_true() and Flags.flags_bar.is_true():
            Flags.skills_bar.toggle()
        elif cols < 30 and Flags.skills_bar.is_true():
            Flags.skills_bar.toggle()
        elif cols < 35 and Flags.flags_bar.is_true():
            Flags.flags_bar.toggle()

    def show_bottom_bar(self, frame: Frame):
        _help = Play.build_list_sentence(self.help_base + self.help_extra)
        for tk in _help.data:
            if tk.text != " ":
                tk.fmt = "B"
        dx = frame.get_dx()
        _help.trim_alfa(dx)
        _help.trim_end(dx)
        frame.set_header(_help, "^")
        frame.set_border_none()
        frame.draw()

    def show_top_bar(self, frame: Frame) -> None:
        dx = frame.get_dx()
        # _help = Play.build_list_sentence(self.help_base)
        # _help.trim_alfa(dx)
        # _help.trim_end(dx)
        # frame.set_footer(_help, "^")
        frame.draw()

        content = FF().add(" ")
        content.addf(Flags.cmds.get_value(), f"({self.rep_alias.upper()})").add(" ")

        for f in self.flagsman.top:
            content.add(f.get_toggle_sentence()).add(" ")

        for s in content.get_data():
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
        xp_bar = FF.build_bar(text, percent, size, done, todo).add(" ")

        limit = dx - xp_bar.len()
        content.trim_spaces(limit)
        content.trim_alfa(limit)
        content.trim_end(limit)

        frame.write(0, 0, content.add(xp_bar))


    def show_items(self):
        Fmt.erase()
        self.tree.reload_sentences()
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
            flags_sy = len([1 for flag in self.flagsman.left if flag.is_bool()])

            frame_flags = Frame(mid_y, 0).set_size(flags_sy + 2, flags_sx)
            self.show_flags_bar(frame_flags)

            frame_colors = Frame(mid_y + flags_sy + 2, 0).set_size(
                mid_sy - flags_sy - 2, flags_sx
            )
            self.show_color_bar(frame_colors)

        task_sx = main_sx - flags_sx - skills_sx
        frame_main = Frame(mid_y, flags_sx).set_size(mid_sy, task_sx)


        self.show_main_bar(frame_main)

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
        def __init__(self, fman: FloatingManager, flag: Flag):
            self.fman = fman
            self.flag = flag

        def __call__(self):
            self.flag.toggle()
            if self.flag.get_location() == "left" and self.flag.is_bool():
                f = Floating("v").warning()
                f.put_text("")
                f.put_text(self.flag.get_description())
                if self.flag.is_true():
                    f.put_sentence(FF().addf("G", "ligado"))
                else:
                    f.put_sentence(FF().addf("R", "desligado"))
                f.put_text("")
                self.fman.add_input(f)

    class GradeFunctor:
        def __init__(self, grade: int, fn):
            self.grade = grade
            self.fn = fn

        def __call__(self):
            self.fn(self.grade)

    def make_callback(self) -> Dict[int, Any]:
        def set_exit():
            self.exit = True

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
        add_str(
            self.Key.quit,
            lambda: self.fman.add_input(
                Floating().put_text("\nBye Bye\n").set_exit_fn(set_exit).warning()
            ),
        )

        add_str(self.Key.up, self.tree.move_up)
        add_int(curses.KEY_UP, self.tree.move_up)

        add_str(self.Key.down, self.tree.move_down)
        add_int(curses.KEY_DOWN, self.tree.move_down)

        add_str(self.Key.left, self.tree.arrow_left)
        add_int(curses.KEY_LEFT, self.tree.arrow_left)

        add_str(self.Key.right, self.tree.arrow_right)
        add_int(curses.KEY_RIGHT, self.tree.arrow_right)

        add_str(self.Key.help, self.show_help)
        add_str(self.Key.expand, self.tree.process_expand)
        add_str(self.Key.collapse, self.tree.process_collapse)

        add_str(self.Key.toggle_enter, self.tree.toggle)
        add_str(self.Key.toggle_space, self.tree.toggle)
        add_str(self.Key.open_link, self.open_link)
        add_str(self.Key.set_lang, self.set_language)
        add_str(self.Key.down_task, self.process_down)
        add_str(self.Key.mass_toggle, self.tree.mass_mark)
        add_str(self.Key.reset, reset_colors)

        for value in range(10):
            add_str(str(value), self.GradeFunctor(int(value), self.tree.set_grade))

        for flag in self.flagsman.left:
            add_str(flag.get_char(), self.FlagFunctor(self.fman, flag))

        for flag in self.flagsman.top:
            add_str(flag.get_char(), self.FlagFunctor(self.fman, flag))

        return calls

    def main(self, scr):
        curses.curs_set(0)  # Esconde o cursor
        Fmt.init_colors()  # Inicializa as cores
        Fmt.set_scr(scr)  # Define o scr como global

        while not self.exit:
            self.tree.update_available()
            self.fman.draw_warnings()
            self.generate_graph()
            calls = self.make_callback()
            self.show_items()



            if self.fman.has_floating():
                value: int = self.fman.get_input()
            else:
                value: int = scr.getch()

            if value in calls.keys():
                calls[value]()

            self.tree.reload_sentences()
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
