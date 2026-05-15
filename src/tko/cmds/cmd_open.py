from tko.play_tree.task_tree import TaskTree
from tko.config.settings import Settings
from tko.repository.repository import Repository
from tko.play.play import Play
from tko.util.rtext import RText
from pathlib import Path
from tko.repository.git_cache import UpdateMode
from tko.play_tree.formatter_util import FormatterUtil
from tko.game.task import Task
from tko.game.quest import Quest

class CmdOpen:
    def __init__(self, settings: Settings, repo: Repository, update_mode: UpdateMode):
        self.settings = settings
        self.need_update = False
        self.repo: Repository = repo
        self.repo_dir: Path = repo.paths.root_dir
        self.update_mode = update_mode

    def display_need_update(self):
        self.need_update = True

    def load_folder(self, repo_dir: Path):
        self.repo_dir = repo_dir
        self.repo = Repository(repo_dir, self.update_mode)
        if not self.repo.paths.config_file.exists():
            print(RText.parse("[r]Erro[.]: O comando [g]tko open[.] deve ser executado na pasta onde o repositório foi iniciado."))
            print(RText.parse("[g]Ação[.]: Navegue ou passe o caminho até a pasta do repositório e tente novamente."))
            raise Warning(RText.parse("[r]Erro:[.] [y][][.] não contém um repositório do tko", repo_dir))
        from tko.repository.repository_loader import RepositoryLoader
        from tko.repository.game_coordinator import GameCoordinator
        RepositoryLoader(self.repo).load_config()
        GameCoordinator(self.repo).load_game(verbose=True)
        return self

    def execute(self):
        play = Play(self.settings, self.repo)
        if self.need_update:
            play.display_need_update()
        play.play()

    def list(self, show_all: bool, only_down: bool, show_quests: bool):
        tree = TaskTree(self.settings, self.repo)
        if not show_quests:
            tree.layout.use_full_key = True
        tree.expand_all()
        tree.update(force_view_all=show_all)
        fmt_util = FormatterUtil(self.settings, self.repo)
        for item, tree_item in tree.get_rendered_items():
            istask = isinstance(tree_item, Task)
            if only_down:
                if not istask:
                    if show_quests:
                        print(item)
                elif fmt_util.is_downloaded_for_lang(tree_item):
                    print(item)
            else:
                if istask:
                    print(item)
                elif show_quests:
                    print(item)
                
