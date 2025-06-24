from tko.game.cluster import Cluster
from tko.game.quest import Quest
from tko.game.task import Task
# from tko.game.graph import Graph

from tko.play.floating_grade import FloatingGrade
from tko.settings.settings import Settings

from tko.cmds.cmd_down import CmdDown
from tko.cmds.cmd_run import Run

from tko.util.param import Param

from tko.cmds.cmd_down import DownProblem

from tko.play.fmt import Fmt
from tko.play.floating import Floating
from tko.play.gui import Gui
from tko.play.opener import Opener

from tko.play.tasktree import TaskAction
from typing import Callable

from tko.logger.log_item_self import LogItemSelf
from tko.logger.log_item_move import LogItemMove

import os
import tempfile
import subprocess


class PlayActions:

    def __init__(self, gui: Gui):
        self.app = Settings().app
        self.settings = Settings()
        self.fman = gui.fman
        self.rep = gui.rep
        self.tree = gui.tree
        self.game = gui.game
        self.graph_opened: bool = False
        self.gui = gui

    def gen_graph_path(self) -> str:
        return os.path.join(self.rep.paths.get_rep_dir(), "graph.png")
        
    @staticmethod
    def open_link_without_stdout_stderr(link: str):
        outfile = tempfile.NamedTemporaryFile(delete=False)
        subprocess.Popen("python3 -m webbrowser -t {}".format(link), stdout=outfile, stderr=outfile, shell=True)

    @staticmethod
    def get_task_folder(task: Task) -> str:
        if task.folder is None:
            raise Exception("Folder não encontrado")
        return task.folder

    def open_code(self):
        obj = self.tree.get_selected_throw()
        if isinstance(obj, Task):
            task: Task = obj
            folder = self.rep.get_task_folder_for_label(task.key)
            if os.path.exists(folder):
                opener = Opener(self.settings).set_fman(self.fman)
                opener.set_target([folder]).set_language(self.rep.get_lang())
                opener.load_folders_and_open()
            else:
                self.fman.add_input(
                    Floating(self.settings, "v>")
                    .put_text("\nO arquivo de código não foi encontrado.\n")
                    .error()
                )
        else:
            self.fman.add_input(
                Floating(self.settings, "v>")
                .put_text("\nVocê só pode abrir o código")
                .put_text("de tarefas baixadas.\n")
                .error()
            )

    def open_link(self):
        obj = self.tree.get_selected_throw()
        if isinstance(obj, Task):
            task: Task = obj
            if task.link_type == Task.Types.VISITABLE_URL or task.link_type == Task.Types.REMOTE_FILE:
                try:
                    PlayActions.open_link_without_stdout_stderr(task.link)
                except Exception as _:
                    pass
            self.fman.add_input(
                Floating(self.settings, "v>")
                .set_header(" Abrindo link ")
                .put_text("\n " + task.link + " \n")
                .warning()
            )
        elif isinstance(obj, Quest):
            self.fman.add_input(
                Floating(self.settings, "v>")
                .put_text("\nEssa é uma missão.")
                .put_text("\nVocê só pode abrir o link")
                .put_text("de tarefas.\n")
                .error()
            )
        else:
            self.fman.add_input(
                Floating(self.settings, "v>")
                .put_text("\nEsse é um grupo.")
                .put_text("\nVocê só pode abrir o link")
                .put_text("de tarefas.\n")
                .error()
            )

    # def generate_graph(self):
    #     Graph(self.game).set_path(self.gen_graph_path()).set_opt(False).generate()
    #     path = self.gen_graph_path()
    #     if not self.graph_opened:
    #         opener = Opener(self.settings)
    #         opener.open_files([path])
    #         self.graph_opened = True

    def register_action(self, task: Task):
        self.rep.logger.store( LogItemSelf().set_key(task.key).set_info(task.info) )

    def evaluate(self):
        obj = self.tree.get_selected_throw()
        
        if isinstance(obj, Task):
            task: Task = obj
            self.fman.add_input(
                FloatingGrade(obj, self.settings, "").set_exit_fn(
                    lambda: self.register_action(task)
                )
            )
            return

    def down_remote_task(self):

        obj = self.tree.get_selected_throw()
        
        if isinstance(obj, Quest):
            self.fman.add_input(
                Floating(self.settings, "v>")
                .put_text("\nEssa é uma missão.")
                .put_text("\nVocê só pode baixar tarefas.\n")
                .error()
            )
            return
        if isinstance(obj, Cluster):
            self.fman.add_input(
                Floating(self.settings, "v>")
                .put_text("\nEsse é um grupo.")
                .put_text("\nVocê só pode baixar tarefas.\n")
                .error()
            )
        if not isinstance(obj, Task):
            return
        self.__down_remote_task(obj)
    
    def __down_remote_task(self, task: Task) -> None:
        if task.link_type != Task.Types.REMOTE_FILE and task.link_type != Task.Types.IMPORT_FILE:
            self.fman.add_input(
                Floating(self.settings, "v>").put_text("\nEssa não é uma tarefa de baixável.\n").error()
            )
            return
        lang = self.rep.get_lang() 
        down_frame = (
            Floating(self.settings, "v>").warning().set_text_ljust().set_header(" Baixando tarefa ")
        )
        # down_frame.put_text(f"\ntko down {self.rep.alias} {task.key} -l {lang}\n")
        self.fman.add_input(down_frame)

        def fnprint(text: str):
            down_frame.put_text(" " + text)
            down_frame.draw()
            Fmt.refresh()

        cmd_down = CmdDown(rep=self.rep, task_key=task.key, settings=self.settings)
        cmd_down.set_game(self.game)
        cmd_down.set_fnprint(fnprint)
        cmd_down.set_language(lang)
        result = cmd_down.execute()
        if result:
            self.rep.logger.store(
                LogItemMove().set_key(task.key).set_mode(LogItemMove.Mode.DOWN)
            )


    def select_task_action(self, task: Task) -> None:
        _, action = self.tree.get_task_action(task)
        if action == TaskAction.BAIXAR:
            self.__down_remote_task(task)
            return
        if action == TaskAction.VISITAR:
            self.open_link()
            return
        folder = task.get_folder()
        if not folder:
            raise Warning("Folder não encontrado")
        self.run_selected_task(task, folder)

    def select_task(self) -> Callable[[], None]:
        obj = self.tree.get_selected_throw()

        if isinstance(obj, Quest) or isinstance(obj, Cluster):
            self.tree.toggle(obj)
            return lambda: None

        if isinstance(obj, Task):
            task: Task = obj
            return lambda: self.select_task_action(task)
        return lambda: None

        
    def run_selected_task(self, task: Task, task_dir: str) -> None:
        folder = task_dir
        run = Run(settings=self.settings, target_list=[folder], param=Param.Basic())
        run.set_lang(self.rep.get_lang())
        opener = Opener(self.settings).set_language(self.rep.get_lang()).set_target([folder])
        run.set_opener(opener)
        run.set_run_without_ask(False)
        run.set_curses(True)
        run.set_task(self.rep, task)

        run.build_wdir()
        
        if not run.wdir.has_solver():
            DownProblem.create_default_draft(task_dir, self.rep.get_lang())
            msg = Floating(self.settings, "v>").warning()
            msg.put_text("\nNenhum arquivo de código na linguagem {} encontrado.".format(self.rep.get_lang()))
            msg.put_text("\nUm arquivo de rascunho foi criado em {}.".format(task_dir))
            self.fman.add_input(msg)
        run.execute()