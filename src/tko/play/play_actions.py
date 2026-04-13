from tko.cmds.drafts_finder_cached import DraftsFinderCached
from tko.game.quest import Quest
from tko.game.task import Task
# from tko.game.graph import Graph

from icecream import ic # type: ignore
from tko.play.FormatterUtil import FormatterUtil
from tko.play.floating_grade import FloatingGrade
from tko.play.floating_input_text import FloatingInputText
from tko.play.tracker import Tracker
from tko.util.text import Text
from tko.cmds.cmd_down import CmdDown
from tko.cmds.cmd_run import Run
from tko.settings.rep_source import STUDENT_SANDBOX_NAME

from tko.util.param import Param

from tko.play.fmt import Fmt
from tko.play.floating import Floating
from tko.play.gui import Gui, TaskAction
from tko.play.opener import Opener

from typing import Callable
from tko.down.sandbox_drafts import SandboxDrafts
import os

from tko.logger.log_item_self import LogItemSelf
from tko.logger.log_item_move import LogItemMove
from tko.cmds.drafts_finder_cached import DraftsFinderCached

import shutil
import tempfile
import subprocess
from pathlib import Path

class PlayActions:

    def __init__(self, gui: Gui):
        self.app = gui.app
        self.settings = gui.settings
        self.fman = gui.fman
        self.repo = gui.repo
        self.tree = gui.tree
        self.game = gui.game
        self.graph_opened: bool = False
        self.gui = gui
        self.fmt_util = FormatterUtil(self.settings, self.repo)

    def resize_panels(self, amount: int):
        value = self.settings.app.panel_size_percent
        new_value = max(30, min(70, value + amount))
        if new_value != value:
            self.settings.app.panel_size_percent = new_value
            self.settings.save_settings()
        
    def open_link_without_stdout_stderr(self, link: str):
        if link.startswith("http://") or link.startswith("https://"):
            outfile = tempfile.NamedTemporaryFile(delete=False)
            subprocess.Popen("python3 -m webbrowser -t {}".format(link), stdout=outfile, stderr=outfile, shell=True)
        else:
            opener = Opener(self.settings)
            opener.add_files_to_open([Path(link)])
            opener.open_files()

    @staticmethod
    def get_task_folder(task: Task) -> Path:
        folder = task.get_workspace_folder()
        if folder is None:
            return Path("")
        return folder.resolve()

    def reload_game(self):
        DraftsFinderCached.reset_cache()
        self.repo.load_game(silent=True)
        self.tree.recalculate_layout()

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
            if obj.get_remote_name() == STUDENT_SANDBOX_NAME:
                self.tree.move_down()
            if not obj.visible:
                self.tree.move_down()
            self.repo.load_game(silent=True)

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
            if ic.enabled:
                delete_folder(text=folder.name)
            else:
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
            folder = self.repo.get_task_folder_for_label(task.get_full_key())
            if os.path.exists(folder):
                opener = Opener(self.settings).set_fman(self.fman).set_language(self.repo.data.get_lang())
                opener.add_task_folder_to_open(folder)
                opener.open_files()
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
        self.repo.logger.store(LogItemSelf().set_task(task))

    def self_evaluate_full(self):
        obj = self.tree.get_selected_throw()
        if isinstance(obj, Task):
            task: Task = obj
            if not task.info.feedback:
                task.info.rate = 100
                task.info.feedback = True
            else:
                task.info.rate = 0
                task.info.feedback = False

    def self_evaluate(self):
        obj = self.tree.get_selected_throw()
        
        if isinstance(obj, Task):
            self.fman.add_input(
                FloatingGrade(obj, lambda task: self.repo.logger.store(LogItemSelf().set_task(task)))
            )

    def create_draft(self):
        sandbox_source = self.game.get_sandbox_source()
        sandbox_folder: Path = sandbox_source.get_workspace()
        sandbox_folder.mkdir(parents=True, exist_ok=True)
        
        def find_numbered_draft_id(sandbox_folder: Path) -> int:
            task_keys_only: list[str] = []
            for quest in self.game.quests.values():
                for task in quest.get_tasks():
                    task_keys_only.append(task.get_key())
            for element in sandbox_folder.iterdir():
                task_keys_only.append(element.name)
            draft_id = SandboxDrafts.find_max_numbered_key(task_keys_only=task_keys_only) + 1
            return draft_id
        
        def search_for_key(text: str) -> tuple[str, str]:
            key = ""
            title_words: list[str] = []

            words = text.split(" ")
            for word in words:
                if word.startswith("@"):
                    key = word[1:]
                else:
                    title_words.append(word)
            return key, " ".join(title_words)

        def __create(draft_title: str):
            key, title = search_for_key(draft_title)
            if key == "":
                key = SandboxDrafts.format_draft_key(find_numbered_draft_id(sandbox_folder))
            if title == "":
                title = "Digite o título da tarefa aqui"
            
            folder:Path = sandbox_folder / key
            if not folder.exists():
                folder.mkdir()
            else:
                self.fman.add_input(
                    Floating().bottom().right()
                    .put_text(f"\nA pasta {folder} já existe.\n")
                    .set_error()
                )
                return

            lang_drafts: dict[str, str] = self.settings.get_languages_settings().get_languages_with_drafts()
            draft = ""
            if self.repo.data.lang in lang_drafts:
                draft = lang_drafts[self.repo.data.lang]
            draft_path = folder / "src" / self.repo.data.lang / f"draft.{self.repo.data.lang}"
            draft_path.parent.mkdir(parents=True, exist_ok=True)
            with open(draft_path, "w", encoding="utf-8") as f:
                f.write(draft)

            SandboxDrafts.create_sandbox_draft(folder, title)
            self.tree.state.selected = f"{sandbox_source.name}@{key}"
            self.tree.state.expanded.add(f"{sandbox_source.name}@{sandbox_source.name}")
            self.repo.data.selected = self.tree.state.selected
            self.reload_game()
            self.fman.add_input( Floating().bottom().right()
                                .put_text(f"Rascunho criado em {folder}")
                                .set_warning())

        current_folders_on_rep: list[str] = [f"@{folder.name}" for folder in sandbox_folder.iterdir() if folder.is_dir()]
        self.fman.add_input(FloatingInputText(Text().add("Digite o Título (use @label para definir a chave manualmente)" ), __create, current_folders_on_rep))

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
    
    def select_task_action(self, task: Task) -> None:
        _, action = self.gui.get_task_action(task)
        if action == TaskAction.BAIXAR:
            self.__down_remote_task(task)
            return
        if action == TaskAction.VISITAR:
            self.open_link()
            return
        self.run_selected_task(task)

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

        cmd_down = CmdDown(repo=self.repo, task_key=task.get_full_key(), settings=self.settings)
        cmd_down.set_fnprint(fnprint)
        result = cmd_down.execute()
        if result:
            self.repo.logger.store(
                LogItemMove().set_key(task.get_full_key()).set_mode(LogItemMove.Mode.DOWN)
            )

    def open_versions(self):
        try:
            obj = self.tree.get_selected_throw()

            if isinstance(obj, Task):
                task: Task = obj
                track_folder = self.repo.paths.get_track_task_folder(task.get_full_key())
                tracker = Tracker()
                tracker.set_folder(track_folder)
                if task.get_full_key() in self.repo.logger.tasks.task_dict:
                    log_sort = self.repo.logger.tasks.task_dict[task.get_full_key()]

                    msg, folder = tracker.unfold_files(log_sort)
                    cmd = self.settings.app.editor
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
                self.tree.toggle()
                return lambda: None

            if isinstance(obj, Task):
                task: Task = obj
                return lambda: self.select_task_action(task)
        except IndexError as _:
            pass

        return lambda: None
        
    def run_selected_task(self, task: Task) -> None:
        task_folder = task.get_workspace_folder()
        if not task_folder:
            raise Warning("Folder não encontrado")
        run = Run(settings=self.settings, target_list=[task_folder], param=Param.Basic())
        run.set_lang(self.repo.data.lang)
        opener = Opener(self.settings).set_language(self.repo.data.get_lang()).add_task_folder_to_open(task_folder)
        run.set_opener(opener)
        run.set_run_without_ask(False)
        run.set_curses(True)
        run.set_task(self.repo, task)
        run.build_wdir()
        
        if not run.wdir.has_solver():
            cmd = CmdDown(self.repo, task.get_full_key(), self.settings)
            cmd.execute()
            msg =  Floating().bottom().right().set_warning()
            msg.put_text("\nNenhum arquivo de código na linguagem {} encontrado.".format(self.repo.data.get_lang()))
            msg.put_text("\nUm arquivo de rascunho foi criado\n")
            self.fman.add_input(msg)
        else:
            run.execute()