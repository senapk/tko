from tko.play.tasktree import TaskTree
from tko.settings.settings import Settings
from tko.settings.repository import Repository
from tko.play.play import Play
from tko.util.text import Text
from pathlib import Path

class CmdOpen:
    def __init__(self, settings: Settings, repo: Repository, force_update: bool):
        self.settings = settings
        self.need_update = False
        self.repo: Repository = repo
        self.repo_dir: Path = repo.paths.get_root_dir()
        self.force_update = force_update

    def display_need_update(self):
        self.need_update = True

    def load_folder(self, repo_dir: Path):
        self.repo_dir = repo_dir
        self.repo = Repository(repo_dir, self.force_update)
        if not self.repo.paths.has_local_config_file():
            print(Text.format("{r}: O comando {g} deve ser executado na pasta onde o repositório foi iniciado.", "Erro", "tko open"))
            print(Text.format("{g}: Navegue ou passe o caminho até a pasta do repositório e tente novamente.", "Ação"))
            raise Warning(Text.format("{r}: {y} {}", "Erro:", repo_dir, "não contém um repositório do tko"))
        self.repo.load_config().load_game()
        return self

    def execute(self):
        play = Play(self.settings, self.repo)
        if self.need_update:
            play.display_need_update()
        play.play()

    def list(self, show_all: bool):
        tree = TaskTree(self.settings, self.repo)
        tree.expand_all()
        tree.update(force_view_all=True, ligatures=True)
        for item in tree.get_rendered_items():
            print(item)
