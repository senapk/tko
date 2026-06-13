from loguru import logger
import os
import subprocess
import tempfile

from tko.game.task import Task
from tko.game.quest import Quest
from tko.floating import Floating
from tko.floating.floating_manager import FloatingManager
from tko.play_tree.task_tree import TaskTree
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.play.opener import Opener
from tko.logger.tracker import Tracker
from tko.i18n import Msg


class _TaskEditorMsg:
    CODE_NOT_FOUND = Msg(pt="O arquivo de código não foi encontrado.", en="Code file not found.")
    CODE_ONLY_DOWNLOADED = Msg(pt="Você só pode abrir o código de tarefas baixadas.", en="You can only open code from downloaded tasks.")
    OPENING_LINK_LOG = Msg(pt="Opening link for task: {task_key}, URL: {url}", en="Opening link for task: {task_key}, URL: {url}")
    TARGET_LOG = Msg(pt="Target: {target}", en="Target: {target}")
    OPENING_LINK = Msg(pt="Abrindo link", en="Opening link")
    IS_MISSION = Msg(pt="Essa é uma missão.", en="This is a mission.")
    LINK_ONLY_TASKS = Msg(pt="Você só pode abrir o link de tarefas.", en="You can only open the link for tasks.")
    VERSIONS_DECOMPRESSED = Msg(
        pt="As versões da tarefa foram descompactadas em uma pasta temporária",
        en="Task versions have been decompressed to a temporary folder",
    )
    VERSIONS_OPENING = Msg(pt="Abrindo com o comando: {cmd}", en="Opening with command: {cmd}")


class TaskEditorService:
    

    def __init__(self, repo: Repository, settings: Settings, fman: FloatingManager, tree: TaskTree):
        self.repo = repo
        self.settings = settings
        self.fman = fman
        self.tree = tree

    def _open_link_without_stdout_stderr(self, url: str | None):
        if url is not None:
            outfile = tempfile.NamedTemporaryFile(delete=False)
            subprocess.Popen("python3 -m webbrowser -t {}".format(url), stdout=outfile, stderr=outfile, shell=True)

    def open_code(self):
        try:
            obj = self.tree.get_selected_throw()
        except IndexError:
            return
        if isinstance(obj, Task):
            task: Task = obj
            folder = self.repo.get_task_folder_for_label(task.basic.full_key)
            if os.path.exists(folder):
                opener = Opener(self.settings).set_fman(self.fman).set_language(self.repo.data.lang)
                opener.add_task_folder_to_open(folder)
                opener.open_files()
            else:
                self.fman.add_input(
                    Floating().bottom().right()
                    .put_text(f"\n{str(_TaskEditorMsg.CODE_NOT_FOUND)}\n")
                    .set_error().set_countdown(Floating.Time.FAST)
                )
        else:
            self.fman.add_input(
                Floating().bottom().right()
                .put_text(f"\n{str(_TaskEditorMsg.CODE_ONLY_DOWNLOADED)}\n")
                .set_error().set_countdown(Floating.Time.FAST)
            )

    def open_link(self):
        try:
            obj = self.tree.get_selected_throw()
        except IndexError:
            return
        if isinstance(obj, Task):
            task: Task = obj
            url = task.resource.external_url
            target = task.path.origin_target
            logger.info(str(_TaskEditorMsg.OPENING_LINK_LOG).format(task_key=task.basic.key, url=url))
            logger.info(str(_TaskEditorMsg.TARGET_LOG).format(target=target))
            if url is not None:
                try:
                    self._open_link_without_stdout_stderr(url)
                    self.fman.add_input(
                        Floating().bottom().right()
                        .set_header(f" {str(_TaskEditorMsg.OPENING_LINK)} ")
                        .put_text(f"\n {str(url)} \n")
                        .set_warning().set_countdown(Floating.Time.FAST)
                    )
                except Exception as _:
                    pass
            if target is not None:
                opener = Opener(self.settings)
                opener.set_fman(self.fman).set_language(self.repo.data.lang)
                opener.add_files_to_open([target])
                opener.open_files()
        elif isinstance(obj, Quest):
            self.fman.add_input(
                Floating().bottom().right()
                .put_text(f"\n{str(_TaskEditorMsg.IS_MISSION)}")
                .put_text(f"\n{str(_TaskEditorMsg.LINK_ONLY_TASKS)}\n")
                .set_error().set_countdown(Floating.Time.FAST)
            )

    def open_versions(self):
        try:
            obj = self.tree.get_selected_throw()
            if isinstance(obj, Task):
                task: Task = obj
                track_folder = self.repo.paths.get_track_task_folder(task.basic.full_key)
                tracker = Tracker()
                tracker.set_folder(track_folder)
                if task.basic.full_key in self.repo.logger.tasks.task_dict:
                    log_sort = self.repo.logger.tasks.task_dict[task.basic.full_key]
                    msg, folder = tracker.unfold_files(log_sort)
                    cmd = self.settings.app.editor
                    fullcmd = "{} {}".format(cmd, folder)
                    outfile = tempfile.NamedTemporaryFile(delete=False)
                    subprocess.Popen(fullcmd, stdout=outfile, stderr=outfile, shell=True)
                    self.fman.add_input(
                        Floating().bottom().right()
                        .put_text(f"\n{str(_TaskEditorMsg.VERSIONS_DECOMPRESSED)}")
                        .put_text(msg)
                        .put_text(f"{str(_TaskEditorMsg.VERSIONS_OPENING).format(cmd=fullcmd)}\n")
                    )
        except IndexError:
            pass
        except Exception:
            pass
