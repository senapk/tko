import os
from pathlib import Path
from tko.util.rtext import RText
from tko.util.raw_terminal import RawTerminal
from tko.feno.filter import CodeFilter
from tko.repository.repository import Repository
from tko.repository.rep_paths import RepPaths
from tko.game.task import Task
from tko.play.opener import Opener
from tko.run.run_context import RunContext

class TkoFilterMode:
    @staticmethod
    def deep_copy_and_change_dir():
        filter_path = (Path.home()/ ".tko_filter").resolve()
        CodeFilter.cf_recursive(Path(".").resolve(), filter_path, force=True)
        # chdir to filter_path
        os.chdir(filter_path)

class RunLoader:
    def __init__(self, ctx: RunContext):
        self.ctx = ctx

    def setup_task(self):
        self.try_setup_task_from_rep()
        if self.ctx.task is None:
            self.setup_task_from_wdir()

    def build_wdir(self):
        self.ctx.wdir_builded = True
        self._remove_duplicates()
        if self.ctx.param.filter:
            self._change_targets_to_filter_mode()
        try:
            lang: str = ""
            if self.ctx.lang:
                lang = self.ctx.lang
            elif self.ctx.repo is not None and self.ctx.repo.data.lang:
                lang = self.ctx.repo.data.lang
            self.ctx.wdir = (self.ctx.wdir.set_curses(self.ctx.curses_mode)
                                    .set_lang(lang)
                                    .set_target_list(self.ctx.target_list)
                                    .build()
                                    .filter(self.ctx.param)
                            )
        except FileNotFoundError as e:
            if self.ctx.wdir.has_solver():
                executable, _ = self.ctx.wdir.get_solver().get_executable()
                executable.set_compile_error(str(e))
        return self.ctx.wdir

    def try_setup_task_from_rep(self) -> bool:
        if self.ctx.repo is None:
            return False
        task = self.ctx.repo.get_task_from_task_folder(self.ctx.pwd)
        if task is not None:
            self.ctx.task = task
        return True

    def _remove_duplicates(self):
        self.ctx.target_list = list(dict.fromkeys(self.ctx.target_list))

    def _change_targets_to_filter_mode(self) -> None:
        print(RText(" Entrando no modo de filtragem ").center(RawTerminal.get_terminal_size(), "═"))

        TkoFilterMode.deep_copy_and_change_dir()
        new_target_list: list[Path] = []

        for target in self.ctx.target_list:
            resolved = target.resolve()
            if resolved.exists():
                new_target_list.append(resolved)

        self.ctx.target_list = new_target_list

    def setup_task_from_wdir(self) -> bool:
        if self.ctx.task is not None:
            return False
        if not self.ctx.wdir_builded:
            return False
        task = Task()
        task.set_key("STANDALONE")
        task.set_remote_name("NONE")
        self.ctx.task = task
        self.ctx.track_folder = None
        return True
            

    def create_opener_for_wdir(self) -> Opener:
        opener = Opener(self.ctx.settings)
        folders: list[Path] = []
        targets: list[Path] = [Path(".")]
        if self.ctx.target_list:
            targets = self.ctx.target_list

        if self.ctx.wdir.get_solver().args_list:
            solver_zero = self.ctx.wdir.get_solver().args_list[0]
            lang = solver_zero.name.split(".")[-1]
            opener.set_language(lang)

        for f in targets:
            if f.is_dir() and f not in folders:
                opener.add_task_folder_to_open(f)
            else:
                opener.add_files_to_open([f])
        return opener
