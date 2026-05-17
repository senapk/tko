import logging
import os
import shutil
from pathlib import Path

from icecream import ic  # type: ignore
from tko.cmds.drafts_finder_cached import DraftsFinderCached
from tko.floating import Floating
from tko.floating.floating_input_text import FloatingInputText
from tko.game.task import Task
from tko.play_gui.gui import Gui
from tko.util.rtext import RText
from tko.i18n import MsgKey, t

from tko.play.draft_creator import DraftCreator
from tko.play.task_download_service import TaskDownloadService
from tko.play.task_editor_service import TaskEditorService
from tko.play.task_evaluator import TaskEvaluator
from tko.play.task_launcher import TaskLauncher


class PlayActions:

    logger = logging.getLogger(__name__)

    def __init__(self, gui: Gui):
        self.app = gui.app
        self.settings = gui.settings
        self.fman = gui.fman
        self.repo = gui.repo
        self.tree = gui.tree
        self.game = gui.game
        self.gui = gui

        self.downloader = TaskDownloadService(self.repo, self.settings, self.fman, self.tree)
        self.editor = TaskEditorService(self.repo, self.settings, self.fman, self.tree)
        self.evaluator = TaskEvaluator(self.repo, self.fman, self.tree)
        self.draft_creator = DraftCreator(self.repo, self.settings, self.fman, self.tree, self.game, self.reload)
        self.launcher = TaskLauncher(self.repo, self.settings, self.fman, self.tree, gui, self.downloader, self.editor)

    # --- UI / config ---

    def resize_panels(self, amount: int):
        value = self.settings.app.panel_size_percent
        new_value = max(30, min(70, value + amount))
        if new_value != value:
            self.settings.app.panel_size_percent = new_value
            self.settings.save_settings()

    def reload(self):
        DraftsFinderCached.reset_cache()
        from tko.repository.game_coordinator import GameCoordinator
        GameCoordinator(self.repo).load_game(verbose=False)
        self.tree.recalculate_layout()

    def get_task_folder(self, task: Task) -> Path:
        folder = task.path.work_dir
        if folder is None:
            return Path("")
        return folder.resolve()

    def delete_folder_ask(self):
        def delete_folder(text: str):
            obj = self.tree.get_selected_throw()
            if not isinstance(obj, Task):
                return
            if obj.basic.key != text:
                self.fman.add_input(
                    Floating().bottom().right()
                    .put_text(f"\n{t(MsgKey.TASK_DELETE_NOT_MATCH)}\n")
                    .set_error()
                )
                return
            folder = self.get_task_folder(obj)
            try:
                shutil.rmtree(folder)
                self.fman.add_input(
                    Floating().bottom().right()
                    .put_text(f"\n{t(MsgKey.TASK_DELETE_SUCCESS, folder=folder)}\n")
                    .set_warning()
                )
            except OSError:
                self.fman.add_input(
                    Floating().bottom().right()
                    .put_text(f"\n{t(MsgKey.PLAY_ACTION_DELETE_ERROR)}\n")
                    .set_error()
                )
            self.reload()

        obj = self.tree.get_selected_throw()
        if isinstance(obj, Task):
            folder = self.get_task_folder(obj)
            if folder == Path("") or not os.path.exists(folder):
                self.fman.add_input(
                    Floating().bottom().right()
                    .put_text("\n" + t(MsgKey.PLAY_ACTION_TASK_NO_LOCAL_FOLDER) + "\n")
                    .set_error()
                )
                return
            if ic.enabled:
                delete_folder(text=folder.name)
            else:
                self.fman.add_input(
                    FloatingInputText(
                        RText(t(MsgKey.PLAY_ACTION_DELETE_CONFIRM_PREFIX)) + RText(f"{obj.basic.key}", "y"),
                        action=delete_folder,
                    )
                )
        else:
            self.fman.add_input(
                Floating().bottom().right()
                .put_text("\n" + t(MsgKey.PLAY_ACTION_ONLY_TASK_FOLDERS) + "\n")
                .set_error()
            )
