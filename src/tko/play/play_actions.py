from tko.game.cluster import Cluster
from tko.game.quest import Quest
from tko.game.task import Task
from tko.game.graph import Graph

from tko.util.logger import Logger, LogAction
from tko.settings.settings import Settings

from tko.cmds.cmd_down import CmdDown
from tko.cmds.cmd_run import Run

from tko.util.consts import Success
from tko.util.param import Param

from tko.util.text import Text

from tko.play.fmt import Fmt
from tko.play.floating import Floating
from tko.play.flags import Flags
from tko.play.gui import Gui
from tko.play.opener import Opener

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
        return os.path.join(self.app._rootdir, self.rep.alias, "graph.png")
        

    def open_link_without_stdout_stderr(self, link: str):
        outfile = tempfile.NamedTemporaryFile(delete=False)
        subprocess.Popen("python3 -m webbrowser -t {}".format(link), stdout=outfile, stderr=outfile, shell=True)

    def open_code(self):
        obj = self.tree.get_selected()
        if isinstance(obj, Task):
            task: Task = obj
            folder = os.path.join(self.app._rootdir, self.rep.alias, task.key)
            if os.path.exists(folder):
                opener = Opener(self.settings).set_fman(self.fman)
                opener.set_target([folder]).set_language(self.rep.get_lang())
                opener.load_folders_and_open()
            else:
                self.fman.add_input(
                    Floating("v>")
                    .put_text("\nO arquivo de código não foi encontrado.\n")
                    .error()
                )
        else:
            self.fman.add_input(
                Floating("v>")
                .put_text("\nVocê só pode abrir o código")
                .put_text("de tarefas baixadas.\n")
                .error()
            )

    def open_link(self):
        obj = self.tree.get_selected()
        if isinstance(obj, Task):
            task: Task = obj
            if task.link.startswith("http"):
                try:
                    self.open_link_without_stdout_stderr(task.link)
                except Exception as _:
                    pass
            self.fman.add_input(
                Floating("v>")
                .set_header(" Abrindo link ")
                .put_text("\n " + task.link + " \n")
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

    def generate_graph(self):
        Graph(self.game).set_path(self.gen_graph_path()).set_opt(False).generate()
        path = self.gen_graph_path()
        if not self.graph_opened:
            opener = Opener(self.settings)
            opener.open_files([path])
            self.graph_opened = True


    def down_task(self):

        lang = self.rep.get_lang() 
        obj = self.tree.get_selected()
        if isinstance(obj, Task) and obj.key in obj.title:
            task: Task = obj
            down_frame = (
                Floating("v>").warning().set_text_ljust().set_header(" Baixando tarefa ")
            )
            down_frame.put_text(f"\ntko down {self.rep.alias} {task.key} -l {lang}\n")
            self.fman.add_input(down_frame)

            def fnprint(text):
                down_frame.put_text(text)
                down_frame.draw()
                Fmt.refresh()
            result = CmdDown.execute(self.rep.alias, task.key, lang, self.settings, fnprint, self.game)
            if result:
                Logger.get_instance().record_event(LogAction.DOWN, task.key)

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
        rootdir = self.app._rootdir
        
        obj = self.tree.get_selected()

        if isinstance(obj, Quest) or isinstance(obj, Cluster):
            self.tree.toggle(obj)
            return

        rep_dir = os.path.join(rootdir, self.rep.alias)
        if isinstance(obj, Task):
            task: Task = obj
            if not task.is_downloadable():
                self.open_link()
                return
            if not task.is_downloaded_for_lang(rep_dir, self.rep.get_lang()):
                self.down_task()
                return
            return self.run_selected_task(task, rep_dir)
        raise Exception("Objeto não reconhecido")
        
    def run_selected_task(self, task: Task, rep_dir: str):
        folder = os.path.join(rep_dir, task.key)
        run = Run(self.settings, [folder], None, Param.Basic())
        run.set_lang(self.rep.get_lang())
        opener = Opener(self.settings).set_language(self.rep.get_lang()).set_target([folder])
        run.set_opener(opener)
        run.set_autorun(False)
        if self.app.has_images():
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