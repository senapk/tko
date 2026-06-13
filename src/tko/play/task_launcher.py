from typing import Callable

from tko.game.task import Task
from tko.game.quest import Quest
from tko.floating import Floating
from tko.floating.floating_manager import FloatingManager
from tko.play_tree.task_tree import TaskTree
from tko.play_gui.gui import Gui
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.play.task_action import TaskAction
from tko.play.opener import Opener
from tko.play.task_download_service import TaskDownloadService
from tko.play.task_editor_service import TaskEditorService
from tko.cmds.cmd_run import Run
from tko.cmds.cmd_down import CmdDown
from tko.i18n import Msg
from tko.util.param import Param


class _TaskLauncherMsg:
    FOLDER_NOT_FOUND = Msg(pt="Pasta não encontrada", en="Folder not found")
    NO_SOURCE_FOR_LANG = Msg(pt="Nenhum arquivo de código na linguagem {lang} encontrado.", en="No source file found for language {lang}.")
    DRAFT_CREATED = Msg(pt="Um arquivo de rascunho foi criado", en="A draft file was created")


class TaskLauncher:

    def __init__(self, repo: Repository, settings: Settings, fman: FloatingManager, tree: TaskTree,
                 gui: Gui, downloader: TaskDownloadService, editor: TaskEditorService):
        self.repo = repo
        self.settings = settings
        self.fman = fman
        self.tree = tree
        self.gui = gui
        self.downloader = downloader
        self.editor = editor

    def select_task(self) -> Callable[[], None]:
        try:
            obj = self.tree.get_selected_throw()

            if isinstance(obj, Quest):
                self.tree.toggle()
                return lambda: None

            if isinstance(obj, Task):
                task: Task = obj
                return lambda: self.select_task_action(task)
        except IndexError:
            pass

        return lambda: None

    def select_task_action(self, task: Task) -> None:
        _, action = self.gui.get_task_action(task)
        if action == TaskAction.BAIXAR:
            self.downloader.down_task(task)
            return
        if action == TaskAction.VISITAR:
            self.editor.open_link()
            return
        self.run_selected_task(task)

    def run_selected_task(self, task: Task) -> None:
        task_folder = task.path.work_dir
        if not task_folder:
            raise Warning(str(_TaskLauncherMsg.FOLDER_NOT_FOUND))
        run = Run(settings=self.settings, target_list=[task_folder], param=Param.Basic())
        run.set_lang(self.repo.data.lang)
        opener = Opener(self.settings).set_language(self.repo.data.lang).add_task_folder_to_open(task_folder)
        run.set_opener(opener)
        run.set_run_without_ask(False)
        run.set_curses(True)
        run.set_task(self.repo, task)
        run.load()

        if not run.context.wdir.solver:
            cmd = CmdDown(self.repo, task.basic.full_key, self.settings)
            cmd.execute()
            msg = Floating().bottom().right().set_warning().set_countdown(Floating.Time.MEDIUM)
            msg.put_text("\n" + str(_TaskLauncherMsg.NO_SOURCE_FOR_LANG).format(lang=self.repo.data.lang))
            msg.put_text("\n" + str(_TaskLauncherMsg.DRAFT_CREATED) + "\n")
            self.fman.add_input(msg)
        else:
            run.execute()
