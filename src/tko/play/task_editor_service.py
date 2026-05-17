import logging
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
from tko.i18n import MsgKey, t


class TaskEditorService:
    logger = logging.getLogger(__name__)

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
        obj = self.tree.get_selected_throw()
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
                    .put_text(f"\n{t(MsgKey.TASK_CODE_NOT_FOUND)}\n")
                    .set_error()
                )
        else:
            self.fman.add_input(
                Floating().bottom().right()
                .put_text(f"\n{t(MsgKey.TASK_CODE_ONLY_DOWNLOADED)}\n")
                .set_error()
            )

    def open_link(self):
        obj = self.tree.get_selected_throw()
        if isinstance(obj, Task):
            task: Task = obj
            url = task.resource.external_url
            target = task.path.origin_target
            self.logger.info(t(MsgKey.TASK_EDITOR_OPENING_LINK_LOG, task_key=task.basic.key, url=url))
            self.logger.info(t(MsgKey.TASK_EDITOR_TARGET_LOG, target=target))
            if url is not None:
                try:
                    self._open_link_without_stdout_stderr(url)
                    self.fman.add_input(
                        Floating().bottom().right()
                        .set_header(f" {t(MsgKey.TASK_OPENING_LINK)} ")
                        .put_text(f"\n {str(url)} \n")
                        .set_warning()
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
                .put_text(f"\n{t(MsgKey.TASK_IS_MISSION)}")
                .put_text(f"\n{t(MsgKey.TASK_LINK_ONLY_TASKS)}\n")
                .set_error()
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
                        .put_text(f"\n{t(MsgKey.TASK_VERSIONS_DECOMPRESSED)}")
                        .put_text(msg)
                        .put_text(f"{t(MsgKey.TASK_VERSIONS_OPENING, cmd=fullcmd)}\n")
                    )
        except Exception:
            pass
