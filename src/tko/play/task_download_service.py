from tko.game.task import Task
from tko.game.quest import Quest
from tko.widget.fmt import Fmt
from tko.floating import Floating
from tko.floating.floating_manager import FloatingManager
from tko.play_tree.task_tree import TaskTree
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.cmds.cmd_down import CmdDown
from tko.logger.log_item_move import LogItemMove
from tko.i18n import MsgKey, t


class TaskDownloadService:

    def __init__(self, repo: Repository, settings: Settings, fman: FloatingManager, tree: TaskTree):
        self.repo = repo
        self.settings = settings
        self.fman = fman
        self.tree = tree

    def down_remote_task(self):
        try:
            obj = self.tree.get_selected_throw()
        except IndexError:
            return
        
        if isinstance(obj, Quest):
            self.fman.add_input(
                Floating().bottom().right()
                .put_text(f"\n{t(MsgKey.TASK_DOWNLOAD_IS_MISSION)}")
                .put_text(f"\n{t(MsgKey.TASK_DOWNLOAD_ONLY_TASKS)}\n")
                .set_error()
            )
            return
        if not isinstance(obj, Task):
            return
        self.down_task(obj)

    def down_task(self, task: Task) -> None:
        if not task.resource.is_import_type:
            self.fman.add_input(
                Floating().bottom().right().put_text(f"\n{t(MsgKey.TASK_DOWNLOAD_NOT_IMPORTABLE)}\n").set_error()
            )
            return
        down_frame = (
            Floating().bottom().right().set_warning().set_text_ljust().set_header(f" {t(MsgKey.TASK_DOWNLOAD_HEADER)} ")
        )
        self.fman.add_input(down_frame)

        def fnprint(text: str):
            down_frame.put_text(" " + text)
            down_frame.draw()
            Fmt.refresh()

        cmd_down = CmdDown(repo=self.repo, task_key=task.basic.full_key, settings=self.settings)
        cmd_down.set_fnprint(fnprint)
        result = cmd_down.execute()
        if result:
            self.repo.logger.store(
                LogItemMove().set_key(task.basic.full_key).set_mode(LogItemMove.Mode.DOWN)
            )
