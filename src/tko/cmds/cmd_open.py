from tko.play_tree.task_tree import TaskTree
from tko.config.settings import Settings
from tko.repository.repository import Repository
from tko.play.play import Play
from pathlib import Path
from tko.play_tree.task_formatter import TaskFormatter
from tko.game.task import Task
from tko.i18n import Msg 
from tko.repository.repository_watcher import RepositoryWatcher
from tko.util.console import Console
# from tko.i18n import t
# from tko.util.rt import RT
# from tko.util.console import Console


_OPEN_INVALID_REPO = Msg(
    pt="[r]Erro[]: O comando [g]tko open[] deve ser executado na pasta onde o repositório foi iniciado.",
    en="[r]Error[]: The [g]tko open[] command must run in the folder where the repository was initialized.",
)
_OPEN_ACTION_HINT = Msg(
    pt="[g]Ação[]: Navegue ou passe o caminho até a pasta do repositório e tente novamente.",
    en="[g]Action[]: Navigate to that folder or pass its path and try again.",
)
_NOT_FOUND_HINT = Msg(
    pt="[r]Erro:[] [y]{repo_dir}[] não contém um repositório do tko",
    en="[r]Error:[] [y]{repo_dir}[] does not contain a tko repository",
)

class CmdOpen:
    def __init__(self, settings: Settings, repo: Repository, watcher: RepositoryWatcher | None = None):
        self.settings = settings
        self.need_update = False
        self.repo: Repository = repo
        self.repo_dir: Path = repo.paths.root_dir
        self.update_mode = settings.rs.update_mode
        self.watcher = watcher

    def display_need_update(self):
        self.need_update = True

    def execute(self):
        play = Play(self.settings, self.repo, self.watcher)
        if self.need_update:
            play.display_need_update()
        play.play()

    def build_tree(self, show_all: bool, full_key: bool, quests_keys: bool = False) -> TaskTree:
        tree = TaskTree(self.settings, self.repo)
        if full_key:
            tree.layout.use_full_key = True
        if quests_keys:
            tree.layout.insert_quest_keys = True
        tree.expand_all()
        tree.update(force_view_all=show_all)
        return tree

    def list(self, show_all: bool, only_down: bool, show_quests: bool):
        tree = self.build_tree(show_all, full_key = not show_quests, quests_keys= not show_quests)
        task_formatter = TaskFormatter(self.settings, self.repo)
        for item, tree_item in tree.get_rendered_items(show_selected=False):
            istask = isinstance(tree_item, Task)
            if only_down:
                if not istask:
                    if show_quests:
                        Console.print(item)
                elif task_formatter.is_downloaded_for_lang(tree_item):
                    Console.print(item)
            else:
                if istask:
                    Console.print(item)
                elif show_quests:
                    Console.print(item)
                
