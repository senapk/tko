from ..game.game import Game
from ..game.cluster import Cluster
from ..game.quest import Quest
from ..game.task import Task
from ..game.graph import Graph
from .opener import Opener
from ..run.basic import Success
from typing import List, Any, Dict, Callable, Tuple
from ..settings.settings import Settings

from ..settings.rep_settings import languages_avaliable, RepData
from ..down import Down
from ..util.sentence import Sentence, Token
from .fmt import Fmt


from .floating import Floating
from .floating_manager import FloatingManager
from .flags import Flag, Flags, FlagsMan
from .tasktree import TaskTree
from ..actions import Run
from ..run.param import Param
from .gui import Key

import webbrowser
import os

class PlayActions:

    def __init__(self, fman: FloatingManager, rep: RepData, rep_alias:str, tree: TaskTree, game: Game, opener: Opener):
        self.app = Settings().app
        self.settings = Settings()
        self.fman = fman
        self.rep = rep
        self.rep_alias = rep_alias
        self.tree = tree
        self.game = game
        self.opener = opener
        
    def set_rootdir(self, only_if_empty=True):
        if only_if_empty and self.app.get_rootdir() != "":
            return

        def chama(value):
            if value == "yes":
                self.app.set_rootdir(os.path.abspath(os.getcwd()))
                self.settings.save_settings()
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
                    .put_text("  tko config --root .")
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
                    .put_text("tko config --root .")
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
            .put_text("Selecione e tecle Enter")
            .put_text("")
            .set_options(["yes", "no"])
            .answer(chama)
        )

    def set_language(self, only_if_empty=True):
        if only_if_empty and self.rep.get_lang() != "":
            return

        def back(value):
            self.rep.set_lang(value)
            self.rep.save_data_to_json()
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
            .put_text("Escolha a extensão default para os rascunhos")
            .put_text("")
            .put_text("Selecione e tecle Enter.")
            .put_text("")
            .set_options(languages_avaliable)
            .answer(back)
        )

    def check_root_and_lang(self):
        if self.app.get_rootdir() == "":
            # self.set_rootdir()
            self.fman.add_input(
                Floating()
                .put_text("")
                .put_text("O diretório de download padrão")
                .put_text("do tko ainda não foi definido.")
                .put_text("")
                .put_sentence(Sentence() + "Utilize o comando " + Token("Shift + " + Key.set_root_dir, "g"))
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
                .put_sentence(Sentence() + "Utilize o comando " + Token("Shift + " + Key.set_lang, "g"))
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
                Floating("v>")
                .set_header(" Abrindo link ")
                .put_text("\n" + task.link + "\n")
                .warning()
            )
        elif isinstance(obj, Quest):
            self.fman.add_input(
                Floating("v>")
                .put_text("\nEssa é uma missão.")
                .put_text("\nVocê só pode abrir o link")
                .put_text("de tarefas.\n")
                .error()
            )
        else:
            self.fman.add_input(
                Floating("v>")
                .put_text("\nEsse é um grupo.")
                .put_text("\nVocê só pode abrir o link")
                .put_text("de tarefas.\n")
                .error()
            )

    def generate_graph(self, first_loop: bool, graph_ext: str):
        if not first_loop:
            return
        if graph_ext == "":
            return
        reachable: List[str] = self.game.available_quests
        counts = {}
        for q in self.game.quests.values():
            done = len([t for t in q.get_tasks() if t.is_complete()])
            init = len([t for t in q.get_tasks() if t.in_progress()])
            todo = len([t for t in q.get_tasks() if t.not_started()])
            counts[q.key] = f"{done} / {done + init + todo}\n{q.get_percent()}%"

        # mark_opt = Flags.dots.is_true()
        Graph(self.game).set_opt(False).set_reachable(reachable).set_counts(
            counts
        ).set_graph_ext(graph_ext).generate()
        lines, _ = Fmt.get_size()
        if first_loop:
            text = Sentence().add(f"Grafo gerado em graph{graph_ext}")
            Fmt.write(lines - 1, 0, text)

    def down_task(self):
        rootdir = self.app.get_rootdir()
        if rootdir == "":
            self.check_root_and_lang()
            return
        lang = self.rep.get_lang()
        if lang == "":
            self.check_root_and_lang()
            return

        obj = self.tree.items[self.tree.index_selected].obj
        if isinstance(obj, Task) and obj.key in obj.title:
            task: Task = obj
            down_frame = (
                Floating("v>").warning().set_ljust_text().set_header(" Baixando tarefa ")
            )
            down_frame.put_text(f"\ntko down {self.rep_alias} {task.key} -l {lang}\n")
            self.fman.add_input(down_frame)

            def fnprint(text):
                down_frame.put_text(text)
                down_frame.draw()
                Fmt.refresh()
            Down.download_problem(self.rep_alias, task.key, lang, fnprint, self.game)
        else:
            if isinstance(obj, Quest):
                self.fman.add_input(
                    Floating("v>")
                    .put_text("\nEssa é uma missão.")
                    .put_text("\nVocê só pode baixar tarefas.\n")
                    .error()
                )
            elif isinstance(obj, Cluster):
                self.fman.add_input(
                    Floating("v>")
                    .put_text("\nEsse é um grupo.")
                    .put_text("\nVocê só pode baixar tarefas.\n")
                    .error()
                )
            else:
                self.fman.add_input(
                    Floating("v>").put_text("\nEssa não é uma tarefa de código.\n").error()
                )
    
    def select_task(self):
        rootdir = self.app.get_rootdir()
        
        obj = self.tree.items[self.tree.index_selected].obj

        if isinstance(obj, Quest) or isinstance(obj, Cluster):
            self.tree.toggle(obj)
            return

        rep_dir = os.path.join(rootdir, self.rep_alias)
        task: Task = obj
        if not task.is_downloadable():
            self.open_link()
            return
        if not task.is_downloaded_for_lang(rep_dir, self.rep.get_lang()):
            self.down_task()
            return
        return self.run_selected_task(task, rep_dir)
        
    def run_selected_task(self, task: Task, rep_dir: str):
        path = os.path.join(rep_dir, task.key)
        run = Run([path], None, Param.Basic())
        run.set_lang(self.rep.get_lang())
        run.set_opener(self.opener)
        run.set_autorun(False)
        if Flags.images.is_true():
            run.set_curses(True, Success.RANDOM)
        else:
            run.set_curses(True, Success.FIXED)
        run.set_task(task)

        run.build_wdir()
        if not run.wdir.has_solver():
            msg = Floating("v>").error()
            msg.put_text("\nNenhum arquivo de código na linguagem {} encontrado.".format(self.rep.get_lang()))
            msg.put_text("Arquivos encontrados na pasta:\n")
            folder = run.wdir.get_autoload_folder()
            file_list = [file for file in os.listdir(folder) if os.path.isfile(os.path.join(folder, file))]
            for file in file_list:
                msg.put_text(file)
            msg.put_text("")
            self.fman.add_input(msg)
            return
        return run.execute