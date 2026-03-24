from tko.game.quest import Quest
from tko.game.task import Task
# from tko.game.graph import Graph

from icecream import ic # type: ignore
from tko.play.floating_grade import FloatingGrade
from tko.play.floating_input_text import FloatingInputText
from tko.settings.settings import Settings
from tko.play.tracker import Tracker
from tko.util.text import Text
from tko.cmds.cmd_down import CmdDown
from tko.cmds.cmd_run import Run
from tko.settings.rep_source import RepSource

from tko.util.param import Param

from tko.cmds.cmd_down import DownActions

from tko.play.fmt import Fmt
from tko.play.floating import Floating
from tko.play.gui import Gui
from tko.play.opener import Opener

from tko.play.tasktree import TaskAction
from typing import Callable

from tko.down.drafts import Drafts
import os

from tko.logger.log_item_self import LogItemSelf
from tko.logger.log_item_move import LogItemMove

import shutil
import tempfile
import subprocess
from pathlib import Path


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

        
    def open_link_without_stdout_stderr(self, link: str):
        if link.startswith("http://") or link.startswith("https://"):
            outfile = tempfile.NamedTemporaryFile(delete=False)
            subprocess.Popen("python3 -m webbrowser -t {}".format(link), stdout=outfile, stderr=outfile, shell=True)
        else:
            Opener(Settings()).open_files([link])

    @staticmethod
    def get_task_folder(task: Task) -> Path:
        folder = task.get_workspace_folder()
        if folder is None:
            return Path("")
        return folder

    def reload_game(self):
        self.rep.load_game(try_update=False, silent=True)

    def delete_folder_ask(self):
        def delete_folder(text: str):
            obj = self.tree.get_selected_throw()
            if not isinstance(obj, Task):
                return
            if obj.get_key() != text:
                self.fman.add_input(
                    Floating().bottom().right()
                    .put_text("\nTexto digitado não corresponde ao identificador da tarefa.\n")
                    .set_error()
                )
                return
            folder = self.get_task_folder(obj)
            try:
                shutil.rmtree(folder)
                self.fman.add_input(
                    Floating().bottom().right()
                    .put_text(f"\nPasta {folder} apagada com sucesso.\n")
                    .set_warning()
                )
            except OSError as e:
                self.fman.add_input(
                    Floating().bottom().right()
                    .put_text(f"\nErro ao apagar a pasta {folder}: {e}\n")
                    .set_error()
                )
            if obj.get_remote_name() == RepSource.STUDENT_SANDBOX_NAME:
                self.tree.move_down()
            self.rep.load_game(try_update=False, silent=True)

        obj = self.tree.get_selected_throw()
        if isinstance(obj, Task):
            folder = self.get_task_folder(obj)
            if folder == Path("") or not os.path.exists(folder):
                self.fman.add_input(
                    Floating().bottom().right()
                    .put_text("\nEssa tarefa não possui pasta de código local.\n")
                    .set_error()
                )
                return
            self.fman.add_input(FloatingInputText(Text().add(f"Para apagar essa pasta, digite ").addf("y", f"{obj.get_key()}"), action=delete_folder))
        else:
            self.fman.add_input(
                Floating().bottom().right()
                .put_text("\nVocê só pode apagar pastas de tarefas.\n")
                .set_error()
            )

    def open_code(self):
        obj = self.tree.get_selected_throw()
        if isinstance(obj, Task):
            task: Task = obj
            folder = self.rep.get_task_folder_for_label(task.get_full_key())
            if os.path.exists(folder):
                opener = Opener(self.settings).set_fman(self.fman)
                opener.set_target([folder]).set_language(self.rep.data.get_lang())
                opener.load_folders_and_open()
            else:
                self.fman.add_input(
                     Floating().bottom().right()
                    .put_text("\nO arquivo de código não foi encontrado.\n")
                    .set_error()
                )
        else:
            self.fman.add_input(
                 Floating().bottom().right()
                .put_text("\nVocê só pode abrir o código")
                .put_text("de tarefas baixadas.\n")
                .set_error()
            )

    def open_link(self):
        obj = self.tree.get_selected_throw()
        if isinstance(obj, Task):
            task: Task = obj
            if task.is_link():
                try:
                    self.open_link_without_stdout_stderr(task.target)
                except Exception as _:
                    pass
            self.fman.add_input(
                 Floating().bottom().right()
                .set_header(" Abrindo link ")
                .put_text("\n " + task.target + " \n")
                .set_warning()
            )
        elif isinstance(obj, Quest):
            self.fman.add_input(
                 Floating().bottom().right()
                .put_text("\nEssa é uma missão.")
                .put_text("\nVocê só pode abrir o link")
                .put_text("de tarefas.\n")
                .set_error()
            )
        else:
            self.fman.add_input(
                 Floating().bottom().right()
                .put_text("\nEsse é um grupo.")
                .put_text("\nVocê só pode abrir o link")
                .put_text("de tarefas.\n")
                .set_error()
            )

    def register_action(self, task: Task):
        self.rep.logger.store(LogItemSelf().set_task(task))

    def self_evaluate(self):
        obj = self.tree.get_selected_throw()
        
        if isinstance(obj, Task):
            task: Task = obj
            if ic.enabled:
                if not task.info.feedback:
                    task.info.rate = 100
                    task.info.feedback = True
                else:
                    task.info.rate = 0
                    task.info.feedback = False
            else:
                if task.is_link() or task.task_rate == Task.TaskRate.TICK:
                    if task.info.feedback:
                        task.info.feedback = False
                        task.info.rate = 0
                        self.rep.logger.store(LogItemSelf().set_task(task))
                    else:
                        task.info.feedback = True
                        task.info.rate = 100
                        self.rep.logger.store(LogItemSelf().set_task(task))
                else:
                    self.fman.add_input(
                        FloatingGrade(obj, lambda task: self.rep.logger.store(LogItemSelf().set_task(task)))
                    )
            return

    def create_draft(self):
        local_source = self.game.get_sandbox_source()
        workspace_folder: Path = local_source.get_source_workspace() / local_source.get_default_sandbox_draft_folder()
        if not os.path.exists(workspace_folder):
            os.makedirs(workspace_folder)
        current_folders_on_rep = os.listdir(workspace_folder)
        
        def __create(draft_name: str):
            folder:Path = workspace_folder / draft_name
            if not folder.exists():
                folder.mkdir()
            else:
                self.fman.add_input(
                    Floating().bottom().right()
                    .put_text(f"\nA pasta {folder} já existe.\n")
                    .set_error()
                )
                return

            draft = ""
            if self.rep.data.lang in Drafts.drafts:
                draft = Drafts.drafts[self.rep.data.lang]
            with open(folder / f"draft.{self.rep.data.lang}", "w", encoding="utf-8") as f:
                f.write(draft)

            task_keys_only: list[str] = []
            for quest in self.game.quests.values():
                for task in quest.get_tasks():
                    task_keys_only.append(task.get_key())
            draft_id = Drafts.find_max_numbered_key(task_keys_only=task_keys_only) + 1
            key = Drafts.create_draft_key(draft_id)
            Drafts.create_sandbox_draft(folder, key)
            
            self.tree.selected_item = f"{RepSource.STUDENT_SANDBOX_NAME}@{key}"
            self.tree.expanded.add(f"{RepSource.STUDENT_SANDBOX_NAME}@{RepSource.DEFAULT_DRAFT_FOLDER}")
            self.rep.data.selected = self.tree.selected_item
            self.rep.load_game(try_update=False, silent=True) # recarrega o jogo
            self.fman.add_input( Floating().bottom().right()
                                .put_text(f"Rascunho criado em {folder}")
                                .put_text("\nVocê pode renomear a pasta manualmente e apertar shift R para recarregar.")
                                .set_warning())

        self.fman.add_input(FloatingInputText(Text().add("Nome do rascunho"), __create, current_folders_on_rep))

    def down_remote_task(self):

        obj = self.tree.get_selected_throw()
        
        if isinstance(obj, Quest):
            self.fman.add_input(
                 Floating().bottom().right()
                .put_text("\nEssa é uma missão.")
                .put_text("\nVocê só pode baixar tarefas.\n")
                .set_error()
            )
            return
        if not isinstance(obj, Task):
            return
        self.__down_remote_task(obj)
    
    def __down_remote_task(self, task: Task) -> None:
        if not task.is_import_type():
            self.fman.add_input(
                 Floating().bottom().right().put_text("\nEssa não é uma tarefa de baixável.\n").set_error()
            )
            return
        down_frame = (
             Floating().bottom().right().set_warning().set_text_ljust().set_header(" Baixando tarefa ")
        )
        # down_frame.put_text(f"\ntko down {self.rep.alias} {task.key} -l {lang}\n")
        self.fman.add_input(down_frame)

        def fnprint(text: str):
            down_frame.put_text(" " + text)
            down_frame.draw()
            Fmt.refresh()

        cmd_down = CmdDown(repo=self.rep, task_key=task.get_full_key(), settings=self.settings)
        cmd_down.set_fnprint(fnprint)
        result = cmd_down.execute()
        if result:
            self.rep.logger.store(
                LogItemMove().set_key(task.get_full_key()).set_mode(LogItemMove.Mode.DOWN)
            )


    def select_task_action(self, task: Task) -> None:
        _, action = self.tree.get_task_action(task)
        if action == TaskAction.BAIXAR:
            self.__down_remote_task(task)
            return
        if action == TaskAction.VISITAR:
            self.open_link()
            return
        folder = task.get_workspace_folder()
        if not folder:
            raise Warning("Folder não encontrado")
        self.run_selected_task(task, folder)


    def open_versions(self):
        try:
            obj = self.tree.get_selected_throw()

            if isinstance(obj, Task):
                task: Task = obj
                track_folder = self.rep.paths.get_track_task_folder(task.get_full_key())
                tracker = Tracker()
                tracker.set_folder(track_folder)
                if task.get_full_key() in self.rep.logger.tasks.task_dict:
                    log_sort = self.rep.logger.tasks.task_dict[task.get_full_key()]

                    msg, folder = tracker.unfold_files(log_sort)
                    cmd = self.settings.app.get_editor()
                    fullcmd = "{} {}".format(cmd, folder)
                    outfile = tempfile.NamedTemporaryFile(delete=False)
                    subprocess.Popen(fullcmd, stdout=outfile, stderr=outfile, shell=True)
                    self.fman.add_input(
                        Floating().bottom().right()
                        .put_text("\nAs versões da tarefa foram descompactadas em uma pasta temporária")
                        .put_text(msg)
                        .put_text(f"Abrindo com o comando: {fullcmd}\n")
                    )
        except:
            pass

    def select_task(self) -> Callable[[], None]:
        try:
            obj = self.tree.get_selected_throw()

            if isinstance(obj, Quest):
                self.tree.toggle(obj)
                return lambda: None

            if isinstance(obj, Task):
                task: Task = obj
                return lambda: self.select_task_action(task)
        except IndexError as _:
            pass

        return lambda: None
        
    def run_selected_task(self, task: Task, task_dir: Path) -> None:
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
            draft_folder = folder / lang
            draft_path = DownActions(self.settings).create_default_draft(draft_folder, self.rep.data.get_lang())
            msg =  Floating().bottom().right().set_warning()
            msg.put_text("\nNenhum arquivo de código na linguagem {} encontrado.".format(self.rep.data.get_lang()))
            msg.put_text("\nUm arquivo de rascunho vazio foi criado em\n {} ".format(draft_path))
            self.fman.add_input(msg)
        run.execute()