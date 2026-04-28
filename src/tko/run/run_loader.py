import os
from pathlib import Path
from tko.util.text import Text
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
        filter_path = os.path.join(os.path.expanduser("~"), ".tko_filter")
        CodeFilter.cf_recursive(Path("."), Path(filter_path), force=True)
        os.chdir(filter_path)

class RunLoader:
    def __init__(self, ctx: RunContext):
        self.ctx = ctx

    def setup_initial_environment(self):
        if len(self.ctx.target_list) == 0:
            if self.ctx.rep is None:
                self._try_load_rep(Path())
            self._try_load_task(Path())

        elif len(self.ctx.target_list) == 1 and os.path.isdir(self.ctx.target_list[0]):
            if self.ctx.rep is None:
                self._try_load_rep(Path(self.ctx.target_list[0]))
            self._try_load_task(Path(self.ctx.target_list[0]))

    def build_wdir(self):
        self.ctx.wdir_builded = True
        self._remove_duplicates()
        self._change_targets_to_filter_mode()
        try:
            self.ctx.wdir = self.ctx.wdir.set_curses(self.ctx.curses_mode).set_lang(self.ctx.lang).set_target_list(self.ctx.target_list).build().filter(self.ctx.param)
        except FileNotFoundError as e:
            if self.ctx.wdir.has_solver():
                executable, _ = self.ctx.wdir.get_solver().get_executable()
                executable.set_compile_error(str(e))
        return self.ctx.wdir

    def prepare_rep_task_logger(self):
        if self.ctx.rep is None:
            solver_path = self.ctx.wdir.get_solver().args_list[0]
            dirname = Path(os.path.dirname(os.path.abspath(solver_path)))
            self._try_load_rep(dirname)
            self._try_load_task(dirname)

        if self.ctx.task is None:
            self._fill_task()

    def _try_load_rep(self, dirname: Path) -> bool:
        repo_path = RepPaths.rec_search_for_repo_parents(dirname)
        if repo_path is None:
            return False
        rep: Repository = Repository(repo_path)
        from tko.repository.repository_loader import RepositoryLoader
        from tko.repository.game_coordinator import GameCoordinator
        RepositoryLoader(rep).load_config()
        GameCoordinator(rep).load_game(verbose=True)
        self.ctx.rep = rep
        if rep.data.lang != "":
            self.ctx.lang = rep.data.lang
        return True

    def _try_load_task(self, dirname: Path) -> bool:
        if self.ctx.rep is None:
            return False
        rep: Repository = self.ctx.rep
        task_key = rep.get_key_from_task_folder(dirname)
        if task_key == "":
            return False
        task = rep.game.tasks.get(task_key)
        if task is None:
            return False
        self.ctx.task = task
        self.ctx.track_folder = rep.paths.get_track_task_folder(task_key)
        return True

    def _remove_duplicates(self):
        self.ctx.target_list = list(dict.fromkeys(self.ctx.target_list))

    def _change_targets_to_filter_mode(self) -> None:
        if not self.ctx.param.filter:
            return

        old_dir: Path = Path.cwd()
        print(Text.format(" Entrando no modo de filtragem ").center(RawTerminal.get_terminal_size(), Text.Token("═")))

        TkoFilterMode.deep_copy_and_change_dir()
        new_target_list: list[Path] = []

        for target in self.ctx.target_list:
            resolved: Path = target if target.is_absolute() else (old_dir / target)
            resolved = resolved.resolve()
            if resolved.exists():
                new_target_list.append(resolved)

        self.ctx.target_list = new_target_list

    def _fill_task(self):
        task = Task()
        sources = self.ctx.wdir.get_source_list()
        solver = self.ctx.wdir.get_solver()

        if len(sources) > 0:
            target_path = os.path.abspath(sources[0])
        elif solver.args_list:
            target_path = os.path.abspath(self.ctx.wdir.get_solver().args_list[0])
        else:
            target_path = os.path.abspath(os.getcwd())

        if os.path.isfile(target_path):
            target_path = os.path.dirname(target_path)

        pieces = target_path.split(os.sep)
        if len(pieces) >= 3:
            task.set_key(pieces[-1])
            task.set_remote_name(pieces[-2])
        elif len(pieces) == 2:
            task.set_key(pieces[-1])
            task.set_remote_name(pieces[-2])
        else:
            task.set_key(pieces[-1])
            task.set_remote_name("")

        self.ctx.task = task
        self.ctx.track_folder = None
        if self.ctx.rep:
            self.ctx.track_folder = self.ctx.rep.paths.get_track_task_folder(task.get_full_key())

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
