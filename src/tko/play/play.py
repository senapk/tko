from ..game.game import Game
from ..game.cluster import Cluster
from ..game.quest import Quest
from ..game.task import Task
from ..game.xp import XP
from ..game.graph import Graph

from typing import List, Any, Dict
from ..settings.settings import RepSettings, GeralSettings
from ..down import Down
from ..util.ftext import Sentence, Token,  RToken
from .fmt import Fmt
from .frame import Frame

from .floating import Floating
from .floating_manager import FloatingManager
from .flags import Flag, Flags, FlagsMan
from .tasktree import TaskTree
from ..actions import Run
from ..run.param import Param
from ..util.symbols import symbols

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

        if self.rep.get_lang() == "":
            self.rep.set_lang(self.local.get_lang_def())
        self.flagsman = FlagsMan(self.rep.get_flags())
        self.game: Game = game
        self.fman = FloatingManager()
        self.tree = TaskTree(local, game, rep, rep_alias)

        if len(self.rep.get_tasks()) == 0:
            self.show_help()

        self.first_loop = True
        self.graph_ext = ""

        self.help_extra: List[Token] = [
            RToken("G", f"Sair[{self.Key.quit}]"),
            RToken("G", f"Ajuda[{self.Key.ajuda}]"),
            RToken("Y", "Navegar[wasd]"),
            RToken("Y", f"Contrair[{self.Key.collapse}{self.Key.expand}]"),
            RToken("C", f"Github[{self.Key.open_link}]"),
            RToken("C", f"Baixar[{self.Key.down_task}]"),
            RToken("C", f"Executar[{self.Key.run_task}]"),
            RToken("M", "Marcar[enter]"),
            RToken("M", "Graduar[0-9]"),
        ]

    def save_to_json(self):
        self.tree.save_on_rep()
        self.rep.set_flags(self.flagsman.get_data())

        self.fn_save()

    def set_rootdir(self, only_if_empty=True):
        if only_if_empty and self.local.get_rootdir() != "":
            return

        def chama(value):
            if value == "yes":
                self.local.set_rootdir(os.path.abspath(os.getcwd()))
                self.fn_save()
                self.fman.add_input(
                    Floating()
                    .put_text("")
                    .put_text("Diretório raiz definido como ")
                    .put_text("")
                    .put_text("  " + os.getcwd())
                    .put_text("")
                    .put_text("Você pode também pode alterar")
                    .put_text("o diretório raiz navegando para o")
                    .put_text("diretório desejado e executando o comando")
                    .put_text("")
                    .put_text("  tko config --root")
                    .put_text("")
                    .warning()
                )
            else:
                self.fman.add_input(
                    Floating()
                    .put_text("")
                    .put_text("Navegue para o diretório desejado e tente novamente.")
                    .put_text("")
                    .put_text("Você pode também pode alterar")
                    .put_text("o diretório raiz navegando para o")
                    .put_text("diretório desejado e executando o comando")
                    .put_text("")
                    .put_text("tko config --root")
                    .put_text("")
                    .warning()
                )

        self.fman.add_input(
            Floating()
            .put_text("")
            .put_text("Você deseja utilizar o diretório")
            .put_text("atual como diretório raiz do tko?")
            .put_text("")
            .put_text(os.getcwd())
            .put_text("")
            .put_text("como raiz para o repositório de " + self.rep_alias + "?")
            .put_text("")
            .put_text("Selecione e tecle enter")
            .put_text("")
            .set_options(["yes", "no"])
            .answer(chama)
        )

    def set_language(self, only_if_empty=True):
        if only_if_empty and self.rep.get_lang() != "":
            return

        def back(value):
            self.rep.set_lang(value)
            self.fn_save()
            self.fman.add_input(
                Floating()
                .put_text("")
                .put_text("Linguagem alterada para " + value)
                .put_text("")
                .warning()
            )

        self.fman.add_input(
            Floating()
            .put_text("")
            .put_text("Escolha a extensão")
            .put_text("default para os rascunhos")
            .put_text("")
            .put_text("Selecione e tecle enter.")
            .put_text("")
            .set_options(["c", "cpp", "py", "ts", "js", "java", "hs"])
            .answer(back)
        )

    def check_root_and_lang(self):
        if self.local.get_rootdir() == "":
            # self.set_rootdir()
            self.fman.add_input(
                Floating()
                .put_text("")
                .put_text("O diretório de download padrão")
                .put_text("do tko ainda não foi definido.")
                .put_text("")
                .put_sentence(Sentence() + "Utilize o comando " + Token("Shift + " + self.Key.set_root, "g"))
                .put_text("para configurá-lo.")
                .put_text("")
            )

        if self.rep.get_lang() == "":
            self.fman.add_input(
                Floating()
                .put_text("")
                .put_text("A linguagem de download padrão")
                .put_text("para os rascunhos ainda não foi definda.")
                .put_text("")
                .put_sentence(Sentence() + "Utilize o comando " + Token("Shift + " + self.Key.set_lang, "g"))
                .put_text("para configurá-la.")
                .put_text("")
            )
            return


    def open_link(self):
        obj = self.tree.get_selected()
        if isinstance(obj, Task):
            task: Task = obj
            if task.link.startswith("http"):
                try:
                    webbrowser.open_new_tab(task.link)
                except Exception as _:
                    pass
            self.fman.add_input(
                Floating()
                .set_header(" Abrindo link ")
                .put_text("\n" + task.link + "\n")
                .warning()
            )
        elif isinstance(obj, Quest):
            self.fman.add_input(
                Floating()
                .put_text("\nEssa é uma missão.")
                .put_text("\nVocê só pode abrir o link")
                .put_text("de tarefas.\n")
                .error()
            )
        else:
            self.fman.add_input(
                Floating()
                .put_text("\nEsse é um grupo.")
                .put_text("\nVocê só pode abrir o link")
                .put_text("de tarefas\n.")
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

        # mark_opt = Flags.dots.is_true()
        Graph(self.game).set_opt(False).set_reachable(reachable).set_counts(
            counts
        ).set_graph_ext(self.graph_ext).generate()
        lines, _cols = Fmt.get_size()
        if self.first_loop:
            text = Sentence().add(f"Grafo gerado em graph{self.graph_ext}")
            Fmt.write(lines - 1, 0, text)

    def down_task(self):
        rootdir = self.local.get_rootdir()
        if rootdir == "":
            self.check_root_and_lang()
            return
        lang = self.rep.get_lang()
        if lang == "":
            self.check_root_and_lang()
            return

        repdir = os.path.join(rootdir, self.rep_alias)

        obj = self.tree.items[self.tree.index_selected].obj
        if isinstance(obj, Task) and obj.key in obj.title:
            task: Task = obj
            down_frame = (
                Floating("").warning().set_ljust_text().set_header(" Baixando tarefa ")
            )
            down_frame.put_text(f"\ntko down {self.rep_alias} {task.key} -l {lang}\n")
            self.fman.add_input(down_frame)

            def fnprint(text):
                down_frame.put_text(text)
                down_frame.draw()
                Fmt.refresh()

            Down.download_problem(self.rep_alias, task.key, lang, fnprint)
        else:
            if isinstance(obj, Quest):
                self.fman.add_input(
                    Floating()
                    .put_text("\nEssa é uma missão.")
                    .put_text("\nVocê só pode baixar tarefas.\n")
                    .error()
                )
            elif isinstance(obj, Cluster):
                self.fman.add_input(
                    Floating()
                    .put_text("\nEsse é um grupo.")
                    .put_text("\nVocê só pode baixar tarefas.\n")
                    .error()
                )
            else:
                self.fman.add_input(
                    Floating().put_text("\nEssa não é uma tarefa de código.\n").error()
                )

    def run_task(self):
        rootdir = self.local.get_rootdir()
        obj = self.tree.items[self.tree.index_selected].obj

        if isinstance(obj, Quest):
            self.fman.add_input(
                Floating()
                .put_text("\nEssa é uma missão.")
                .put_text("\nVocê só pode executar tarefas baixadas.\n")
                .error()
            )
            return
        if isinstance(obj, Cluster):
            self.fman.add_input(
                Floating()
                .put_text("\nEsse é um grupo.")
                .put_text("\nVocê só pode executar tarefas baixadas.\n")
                .error()
            )
            return


        if not obj.key in obj.title:
            self.fman.add_input(
                Floating().put_text("\nEssa não é uma tarefa de código.\n").error()
            )
            return
        path = os.path.join(rootdir, self.rep_alias, obj.key)
        if not os.path.isdir(path):
            self.fman.add_input(
                Floating().put_text("\nVocê precisa baixar a tarefa primeiro\n").error()
            )
            return
        run = Run([path], None, Param.Basic())
        run.set_curses()
        return run.execute



    @staticmethod
    def build_list_sentence(items: List[Token]) -> Sentence:
        _help = Sentence()
        try:
            for x in items:
                label, key = x.text.split("[")
                key = "[" + key
                _help.addf("/" + x.fmt, label).addf(x.fmt, key).add(" ")
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
        dy, dx = frame.get_inner()
        frame.set_header(
            Sentence().add("{").addf("/", f"Tarefas lang:{self.rep.get_lang()}").add("}")
        )
        link = Sentence().add(self.build_bar_links())
        if link.len() > dx - 2:
            link.trim_end(dx - 5)
            link.addf("r", "...")
        frame.set_footer(link, ">", "{", "}")
        frame.draw()

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

        done = Flags.main_done.get_value() + "/k"  # adicionando depois para ter menor prioridade
        todo = Flags.main_todo.get_value() + "/k"
        total_bar = Sentence.build_bar(text, total_perc / 100, dx - 2, done, todo)
        frame_xp.set_header(Sentence().add("{").addf("/", "Skills").add("}"), "^")
        # frame_xp.set_footer(Sentence().add(total_bar), "^")
        frame_xp.draw()

        total, obt = self.game.get_skills_resume(self.tree.available_quests)
        index = 0
        for skill, value in total.items():
            if Flags.percent.is_true():
                text = f"{skill}:{int(100 * obt[skill] / value)}%"
            else:
                text = f"{skill}:{obt[skill]}/{value}"

            perc = obt[skill] / value
            done = Flags.skill_done.get_value() + "/k"  # adicionando depois para ter menor prioridade
            todo = Flags.skill_todo.get_value() + "/k"
            skill_bar = Sentence.build_bar(text, perc, dx - 2, done, todo)
            frame_xp.write(index, 1, skill_bar)
            index += 2

        frame_xp.write(index, 1, total_bar)

    def show_flags_bar(self, frame: Frame):
        frame.set_header(Sentence().add("{").addf("/", "Config").add("}"), "^")
        frame.draw()
        frame.print(0, Sentence())

        pad = 11
        for flag in self.flagsman.left:
            if flag.is_bool():
                frame.print(0, flag.get_toggle_sentence(pad))
                frame.print(0, Sentence())

        frame.print(0, Sentence().addf("C", "Pasta Raiz [P]"))
        frame.print(0, Sentence())
        frame.print(0, Sentence().addf("C", "Linguagem  [L]"))
        frame.print(0, Sentence())

    def show_color_bar(self, frame: Frame):
        frame.set_header(Sentence().add("{").addf("/", "Cores").add("}"), "^")
        frame.draw()

        for flag in self.flagsman.left:
            if not flag.is_bool():
                frame.print(0, flag.get_toggle_sentence())

    def show_help_config(self):
        _help: Floating = Floating().warning().set_ljust_text().set_header(" Configurações ")
        dx = 80
        self.fman.add_input(_help)
        _help.put_sentence(Sentence() + f"      Mínimo " + RToken("r", f"[{Flags.minimum.get_char()}]") + " - Mostrar os requisitos mínimos para completar a missão")
        _help.put_sentence(Sentence() + f"  Recompensa " + RToken("r", f"[{Flags.reward.get_char()}]") + " - Mostrar quanto de experiência cada atividade fornece")
        _help.put_sentence(Sentence() + f"  Percentual " + RToken("r", f"[{Flags.percent.get_char()}]") + " - Mostrar os valores em percentual")
        _help.put_sentence(Sentence() + f"  ModoAdmin " + RToken("r", f"Shift + [A]") + " - Liberar acesso a todas as missões" )
        _help.put_sentence(Sentence() + f"  PastaRaiz " + RToken("r", f"Shift + [{self.Key.set_root}]") + " - Mudar a pasta padrão de download do tko" )
        _help.put_sentence(Sentence() + f"  Linguagem " + RToken("r", f"Shift + [{self.Key.set_lang}]") + " - Mudar a linguagem de download dos rascunhos" )


    def show_help(self):
        _help: Floating = Floating().warning().set_ljust_text()
        dx = 80
        self.fman.add_input(_help)

        _help.set_header_sentence(Sentence().add(" Ajuda "))
        _help.put_sentence(Sentence().add("  Barras Alternáveis  - ").add("Config").addf("r", f"[c]").add(", ").add("Técnicas").addf("r", "[t]"))
        # _help.put_text("")
        # _help.put_text(" Movimentação ".center(dx, symbols.hbar.text))
        _help.put_sentence(Sentence() + "  " + RToken("g", "[setas]") + " ou " + RToken("g", "[wasd]") + "   - Para navegar entre os elementos")
        _help.put_sentence(Sentence() + "  " + RToken("g", "[enter]") + " ou " + RToken("g", "[espaço]") + " - Expandir ou contrair")
        _help.put_sentence(Sentence() + "    " + RToken("g", "[>]") + "   ou   " + RToken("g", "[<]") + "    - Expandir ou contrair todas")
        # _help.put_text("")
        # _help.put_text(" Tarefas ".center(dx, symbols.hbar.text))
        _help.put_sentence(Sentence() + "  " + RToken("g", "[enter]") + " ou " + RToken("g", "[espaço]")
                            + " - Marcar (" + Token(symbols.success.text, "g") + "10)"
                            + " ou Desmarcar (" + Token(symbols.failure.text, "r") + "0)")
        _help.put_sentence(Sentence() + "          ou " + RToken("g", "[1-9]") + "    - Definir uma nota parcial")
        _help.put_sentence(Sentence() + "  Github " + RToken("r", f"[{self.Key.open_link}]") + " - Abrir tarefa em uma aba do browser")
        _help.put_sentence(Sentence() + "  Baixar " + RToken("r", f"[{self.Key.down_task}]") + " - Baixar tarefa de código para seu dispositivo")
        _help.put_sentence(Sentence() + "Executar " + RToken("r", f"[{self.Key.run_task}]") + " - Rodar tarefa de código que você baixou")

    @staticmethod
    def disable_on_resize():
        _, cols = Fmt.get_size()
        if cols < 50 and Flags.skills.is_true() and Flags.config.is_true():
            Flags.skills.toggle()
        elif cols < 30 and Flags.skills.is_true():
            Flags.skills.toggle()
        elif cols < 35 and Flags.config.is_true():
            Flags.config.toggle()

    def get_task_path(self) -> str:
        obj = self.tree.get_selected()
        if isinstance(obj, Task):
            rootdir = self.local.get_rootdir()
            if rootdir != "":
                path = os.path.join(self.local.get_rootdir(), self.rep_alias, obj.key, "Readme.md")
                if os.path.isfile(path):
                    return path
        return ""

    def show_bottom_bar(self, frame: Frame):
        content = Sentence().add("  ")

        _help = Play.build_list_sentence(self.help_extra).add(" ")
        content.add(_help)
        content.trim_alfa(frame.get_dx())
        frame.set_header(content, "^")
        frame.set_border_none()
        frame.draw()
        frame.draw()

    def show_top_bar(self, frame: Frame) -> int:
        dx = frame.get_dx()
        content = Sentence().add(" ")
        content.addf("G", f"({self.rep_alias.upper()})").add(" ")

        flags = Sentence()
        for f in self.flagsman.top:
            flags.add(f.get_toggle_sentence()).add(" ")
        content.add(flags)


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
        done = Flags.main_done.get_value() + "/k"
        todo = Flags.main_todo.get_value() + "/k"
        xp_bar = Sentence().add(Sentence.build_bar(text, percent, size, done, todo).add(" "))

        # limit = dx - xp_bar.len()
        # # content.trim_spaces(limit)
        # # content.trim_alfa(limit)
        # # content.trim_end(limit)
        content.add(xp_bar)

        frame.write(0, 0, content)

        pasta_raiz = "Não definida"
        root = self.local.get_rootdir()
        if root != "":
            pasta_raiz = os.path.join(root, self.rep_alias)
        frame.set_footer(Sentence().addf("/", "Pasta Raiz: ").addf("/", pasta_raiz), ">", "{", "}")

        frame.draw()
        return content.len()
        # frame.write(0, 0, content)


    def show_items(self):
        Fmt.erase()
        self.tree.reload_sentences()
        lines, cols = Fmt.get_size()
        main_sx = cols  # tamanho em x livre
        main_sy = lines  # size em y avaliable

        top_y = -1
        top_dy = 3
        frame_top = Frame(top_y, 0).set_size(3, main_sx)

        size_top = self.show_top_bar(frame_top)

        bottom_sy = 2
        frame_bottom = Frame(lines - 2, 0).set_size(3, size_top + 2)
        self.show_bottom_bar(frame_bottom)


        mid_y = top_y + top_dy
        mid_sy = main_sy - (top_y + top_dy + bottom_sy)

        skills_sx = 0
        if Flags.skills.is_true():
            skills_sx = max(20, main_sx // 4)
            frame_skills = Frame(mid_y, cols - skills_sx).set_size(mid_sy, skills_sx)
            self.show_skills_bar(frame_skills)


        flags_sx = 0
        if Flags.config.is_true():
            flags_sx = 16
            # flags_sy = len([1 for flag in self.flagsman.left if flag.is_bool()])

            frame_flags = Frame(mid_y, 0).set_size(mid_sy, flags_sx)
            self.show_flags_bar(frame_flags)

            # frame_colors = Frame(mid_y + flags_sy + 2, 0).set_size(
            #     mid_sy - flags_sy - 2, flags_sx
            # )
            # self.show_color_bar(frame_colors)

        task_sx = main_sx - flags_sx - skills_sx
        frame_main = Frame(mid_y, flags_sx).set_size(mid_sy, task_sx)


        self.show_main_bar(frame_main)

    class Key:
        left = "a"
        right = "d"
        down = "s"
        up = "w"
        down_task = "b"
        run_task = "e"
        ajuda = "h"
        expand = ">"
        collapse = "<"
        set_root = "P"
        set_lang = "L"
        open_link = "g"
        quit = "q"
        reset = "U"
        mass_toggle = "B"
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
                    f.put_sentence(Sentence().addf("G", "ligado"))
                else:
                    f.put_sentence(Sentence().addf("R", "desligado"))
                f.put_text("")
                self.fman.add_input(f)

    class GradeFunctor:
        def __init__(self, grade: int, fn):
            self.grade = grade
            self.fn = fn

        def __call__(self):
            self.fn(self.grade)

    def toggle_config(self):
        if Flags.config.is_true():
            Flags.config.toggle()
        else:
            Flags.config.toggle()
            self.show_help_config()

    def make_callback(self) -> Dict[int, Any]:
        def set_exit():
            self.exit = True

        def reset_colors():
            for flag in self.flagsman.left:
                if not flag.is_bool():
                    flag.index(0)
            self.fman.add_input(Floating().put_text("\nCores alteradas para seus valores padrão.\n").warning())

        calls = {}

        def add_int(_key: int, fn):
            if _key in calls.keys():
                raise ValueError(f"Chave duplicada {chr(_key)}")
            calls[_key] = fn

        def add_str(str_key: str, fn):
            if str_key != "":
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

        add_str(self.Key.ajuda, self.show_help)
        add_str(self.Key.expand, self.tree.process_expand)
        add_str(self.Key.collapse, self.tree.process_collapse)

        add_str(self.Key.toggle_enter, self.tree.toggle)
        add_str(self.Key.toggle_space, self.tree.toggle)
        add_str(self.Key.open_link, self.open_link)
        add_str(self.Key.set_lang, lambda: self.set_language(False))
        add_str(self.Key.set_root, lambda: self.set_rootdir(False))
        add_str(self.Key.down_task, self.down_task)
        add_str(self.Key.run_task, self.run_task)
        add_str(self.Key.mass_toggle, self.tree.mass_mark)
        add_str(self.Key.reset, reset_colors)

        for value in range(10):
            add_str(str(value), self.GradeFunctor(int(value), self.tree.set_grade))

        if Flags.config.is_true():
            for flag in self.flagsman.left:
                add_str(flag.get_char(), self.FlagFunctor(self.fman, flag))

        # for flag in self.flagsman.top:
        #     add_str(flag.get_char(), self.FlagFunctor(self.fman, flag))

        add_str(Flags.config.get_char(), self.toggle_config)
        add_str(Flags.skills.get_char(), self.FlagFunctor(self.fman, Flags.skills))

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
                value = scr.getch()

            if value in calls.keys():
                callback = calls[value]()
                if callback is not None:
                    return callback
            elif value != -1:
                self.fman.add_input(Floating("v").error()
                                    .put_text("Tecla")
                                    .put_text(chr(value))
                                    .put_text("não reconhecida")
                                    .put_text("")
                                    )

            self.tree.reload_sentences()
            self.save_to_json()

            if self.first_loop:
                self.first_loop = False

    def check_lang_in_text_mode(self):
        lang = self.rep.get_lang()
        if lang == "":
            options = ["c", "cpp", "py", "ts", "js", "java", "hs"]
            print("\nLinguagem padrão ainda não foi definida.\n")
            while True:
                print("Escolha entre as opções a seguir ", end="")
                print("[" + ", ".join(options) + "]", ":", end=" ")
                lang = input()
                if lang in options:
                    break
            self.rep.set_lang(lang)

    def play(self, graph_ext: str):
        self.graph_ext = graph_ext
        self.check_lang_in_text_mode()

        while True:
            output = curses.wrapper(self.main)
            if output is None:
                return
            else:
                output()
