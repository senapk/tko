from tko.game.task import Task
from tko.game.quest import Quest
from tko.util.rt import RT
from tko.widget.fmt import Fmt
from tko.floating import Floating
from tko.floating.floating_manager import FloatingManager
from tko.play_tree.task_tree import TaskTree
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.cmds.cmd_down import CmdDown
from tko.logger.log_item_move import LogItemMove, LogItemMoveMode
from tko.i18n import Msg


class _TaskDownloadMsg:
    IS_MISSION = Msg.text(pt="Essa é uma missão.", en="This is a mission.")
    ONLY_TASKS = Msg.text(pt="Você só pode baixar tarefas.", en="You can only download tasks.")
    NOT_IMPORTABLE = Msg.text(pt="Essa não é uma tarefa de bai xável.", en="This is not a downloadable task.")
    HEADER = Msg.text(pt="Baixando tarefa", en="Downloading task")


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
            self.fman.add_floating(
                Floating().bottom().right()
                .put_text(f"\n{_TaskDownloadMsg.IS_MISSION.t()}")
                .put_text(f"\n{_TaskDownloadMsg.ONLY_TASKS.t()}\n")
                .set_error().set_countdown(Floating.Time.FAST)
            )
            return
        if not isinstance(obj, Task):
            return
        self.down_task(obj)

    def down_task(self, task: Task) -> None:
        if task.resource.is_static_type:
            self.fman.add_floating(
                Floating().bottom().right().put_text(f"\n{_TaskDownloadMsg.NOT_IMPORTABLE.t()}\n").set_error()
            )
            return
        down_frame = (
            Floating().bottom().right().set_warning().set_countdown(Floating.Time.MEDIUM)
            .set_text_ljust().set_header(f" {_TaskDownloadMsg.HEADER.t()} ")
        )
        self.fman.add_floating(down_frame)

        def fnprint(text : str | RT):
            down_frame.put_text(text)
            down_frame.draw()
            Fmt.refresh()

        cmd_down = CmdDown(repo=self.repo, task_key=task.basic.full_key, settings=self.settings)
        cmd_down.set_fnprint(fnprint)
        result = cmd_down.execute()
        if result:
            self.repo.logger.store(
                LogItemMove().set_key(task.basic.full_key).set_mode(LogItemMoveMode.DOWN)
            )
