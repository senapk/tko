from tko.game.cluster import Cluster
from tko.game.quest import Quest
from tko.game.task import Task
# from tko.game.graph import Graph

from icecream import ic # type: ignore
from tko.play.floating_grade import FloatingGrade
from tko.settings.settings import Settings

from tko.cmds.cmd_down import CmdDown
from tko.cmds.cmd_run import Run

from tko.util.param import Param

from tko.cmds.cmd_down import DownActions

from tko.play.fmt import Fmt
from tko.play.floating import Floating
from tko.play.gui import Gui
from tko.play.opener import Opener

from tko.play.tasktree import TaskAction
from typing import Callable

from tko.logger.log_item_self import LogItemSelf
from tko.logger.log_item_move import LogItemMove

import os
import shutil
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

        
    @staticmethod
    def open_link_without_stdout_stderr(link: str):
        outfile = tempfile.NamedTemporaryFile(delete=False)
        subprocess.Popen("python3 -m webbrowser -t {}".format(link), stdout=outfile, stderr=outfile, shell=True)

    @staticmethod
    def get_task_folder(task: Task) -> str:
        return task.get_folder_try()

    def delete_folder(self):
        obj = self.tree.get_selected_throw()
        if isinstance(obj, Task):
            task: Task = obj
            folder = self.get_task_folder(task)
            if os.path.exists(folder):
                try:
                    shutil.rmtree(folder)
                    self.fman.add_input(
                        Floating(self.settings, "v>")
                        .put_text(f"\nPasta {folder} apagada com sucesso.\n")
                        .set_warning()
                    )
                except OSError as e:
                    self.fman.add_input(
                        Floating(self.settings, "v>")
                        .put_text(f"\nErro ao apagar a pasta {folder}: {e}\n")
                        .set_error()
                    )
            else:
                self.fman.add_input(
                    Floating(self.settings, "v>")
                    .put_text("\nPasta não encontrada.\n")
                    .set_error()
                )
        else:
            self.fman.add_input(
                Floating(self.settings, "v>")
                .put_text("\nVocê só pode apagar pastas de tarefas.\n")
                .set_error()
            )

    def open_code(self):
        obj = self.tree.get_selected_throw()
        if isinstance(obj, Task):
            task: Task = obj
            folder = self.rep.get_task_folder_for_label(task.get_db_key())
            if os.path.exists(folder):
                opener = Opener(self.settings).set_fman(self.fman)
                opener.set_target([folder]).set_language(self.rep.data.get_lang())
                opener.load_folders_and_open()
            else:
                self.fman.add_input(
                    Floating(self.settings, "v>")
                    .put_text("\nO arquivo de código não foi encontrado.\n")
                    .set_error()
                )
        else:
            self.fman.add_input(
                Floating(self.settings, "v>")
                .put_text("\nVocê só pode abrir o código")
                .put_text("de tarefas baixadas.\n")
                .set_error()
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
                .set_warning()
            )
        elif isinstance(obj, Quest):
            self.fman.add_input(
                Floating(self.settings, "v>")
                .put_text("\nEssa é uma missão.")
                .put_text("\nVocê só pode abrir o link")
                .put_text("de tarefas.\n")
                .set_error()
            )
        else:
            self.fman.add_input(
                Floating(self.settings, "v>")
                .put_text("\nEsse é um grupo.")
                .put_text("\nVocê só pode abrir o link")
                .put_text("de tarefas.\n")
                .set_error()
            )

    def register_action(self, task: Task):
        self.rep.logger.store( LogItemSelf().set_key(task.get_db_key()).set_info(task.info) )

    def evaluate(self):
        obj = self.tree.get_selected_throw()
        
        if isinstance(obj, Task):
            task: Task = obj
            if ic.enabled:
                task.info.rate = 100
                task.info.flow = task.info.flow_max
                task.info.edge = task.info.edge_max
            else:
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
                .set_error()
            )
            return
        if isinstance(obj, Cluster):
            self.fman.add_input(
                Floating(self.settings, "v>")
                .put_text("\nEsse é um grupo.")
                .put_text("\nVocê só pode baixar tarefas.\n")
                .set_error()
            )
        if not isinstance(obj, Task):
            return
        self.__down_remote_task(obj)
    
    def __down_remote_task(self, task: Task) -> None:
        if task.link_type != Task.Types.REMOTE_FILE and task.link_type != Task.Types.IMPORT_FILE:
            self.fman.add_input(
                Floating(self.settings, "v>").put_text("\nEssa não é uma tarefa de baixável.\n").set_error()
            )
            return
        lang = self.rep.data.get_lang() 
        down_frame = (
            Floating(self.settings, "v>").set_warning().set_text_ljust().set_header(" Baixando tarefa ")
        )
        # down_frame.put_text(f"\ntko down {self.rep.alias} {task.key} -l {lang}\n")
        self.fman.add_input(down_frame)

        def fnprint(text: str):
            down_frame.put_text(" " + text)
            down_frame.draw()
            Fmt.refresh()

        cmd_down = CmdDown(rep=self.rep, task_key=task.get_db_key(), settings=self.settings)
        cmd_down.set_game(self.game)
        cmd_down.set_fnprint(fnprint)
        cmd_down.set_language(lang)
        result = cmd_down.execute()
        if result:
            self.rep.logger.store(
                LogItemMove().set_key(task.get_db_key()).set_mode(LogItemMove.Mode.DOWN)
            )


    def select_task_action(self, task: Task) -> None:
        _, action = self.tree.get_task_action(task)
        if action == TaskAction.BAIXAR:
            self.__down_remote_task(task)
            return
        if action == TaskAction.VISITAR:
            self.open_link()
            return
        folder = task.get_folder_try()
        if not folder:
            raise Warning("Folder não encontrado")
        self.run_selected_task(task, folder)

    def select_task(self) -> Callable[[], None]:
        try:
            obj = self.tree.get_selected_throw()

            if isinstance(obj, Quest) or isinstance(obj, Cluster):
                self.tree.toggle(obj)
                return lambda: None

            if isinstance(obj, Task):
                task: Task = obj
                return lambda: self.select_task_action(task)
        except IndexError as _:
            pass

        return lambda: None
        

        
    def run_selected_task(self, task: Task, task_dir: str) -> None:
        folder = task_dir
        run = Run(settings=self.settings, target_list=[folder], param=Param.Basic())
        run.set_lang(self.rep.data.lang)
        opener = Opener(self.settings).set_language(self.rep.data.get_lang()).set_target([folder])
        run.set_opener(opener)
        run.set_run_without_ask(False)
        run.set_curses(True)
        run.set_task(self.rep, task)
        run.build_wdir()
        
        if not run.wdir.has_solver():
            lang = self.rep.data.get_lang()
            draft_folder = os.path.join(folder, lang)
            DownActions().create_default_draft(draft_folder, self.rep.data.get_lang())
            msg = Floating(self.settings, "v>").set_warning()
            msg.put_text("\nNenhum arquivo de código na linguagem {} encontrado.".format(self.rep.data.get_lang()))
            msg.put_text("\nUm arquivo de rascunho vazio foi criado em {}.".format(draft_folder))
            self.fman.add_input(msg)
        run.execute()