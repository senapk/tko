from typing import Callable
import os
import shutil

from tko.cmds.drafts_finder_cached import DraftsFinderCached
from tko.settings.repository import Repository
from tko.settings.settings import Settings
from tko.game.game import Game
from tko.util.decoder import Decoder
from tko.feno.remote_md import Absolute
from tko.game.task import Task
from tko.feno.filter import CodeFilter
from pathlib import Path
from tko.loader.toml_parser import TomlParser

class CmdLineDown:
    def __init__(self, settings: Settings, rep: Repository, task_key: str, game: Game | None = None):
        self.settings = settings
        self.rep = rep
        self.task_key = task_key
        if game is None:
            self.rep.load_config().load_game()
            self.game = self.rep.game
        else:
            self.game = game
        
    def execute(self):
        if not self.rep.paths.has_local_config_file():
            print("O parâmetro para o comando tko down deve a pasta onde você iniciou o repositório.")
            print("Navegue ou passe o caminho até a pasta do repositório e tente novamente.")
            return False
    
        CmdDown(self.rep, self.task_key, self.settings).execute()
        return True


class CmdDown:
    def __init__(self, repo: Repository, task_key: str, settings: Settings):
        self.repo = repo
        self.task_key = task_key
        self.settings = settings
        self.task: Task = self.repo.game.get_task(self.task_key)
       
        origin_folder = self.task.get_origin_folder()
        if origin_folder is None:
            raise ValueError(f"Atividade {self.task_key} não possui pasta de origem para download")
        self.origin_folder: Path = origin_folder # root task folder
        
        destiny_folder = self.task.get_workspace_folder()
        if destiny_folder is None:
            raise ValueError(f"Atividade {self.task_key} não possui pasta de destino para download")
        self.destiny_folder: Path = destiny_folder # root task workspace folder
       
        self.language: str = ""
        self.check_and_get_language()
        self.actions = DownActions(self.settings)
        
    def execute(self) -> bool:
        if self.task.is_import_type():
            return self.download_from_external_source()
        if self.task.is_static_type():
            if not self.copy_drafts():
                self.actions.send_to_print("Atividade já está no repositório, precisa baixar nenhum arquivo")
            return False
        self.actions.send_to_print("falha: link para atividade não possui link para download")
        return False

    def set_fnprint(self, fnprint: Callable[[str], None]):
        self.actions.fnprint = fnprint
        return self

    def remove_empty_destiny_folder(self):
        if os.path.exists(self.destiny_folder):
            if len(os.listdir(self.destiny_folder)) == 0:
                os.rmdir(self.destiny_folder)

    def find_and_create_folder_for_drafts(self, force: bool = False) -> Path:
        lang = self.language
        finder = DraftsFinderCached(self.destiny_folder, lang)
        drafts_folder = finder.find_dir_for_drafts()
        if not drafts_folder.exists():
            drafts_folder.mkdir(parents=True, exist_ok=True)
            return drafts_folder
        elif force:
            shutil.rmtree(drafts_folder)
            drafts_folder.mkdir(parents=True, exist_ok=True)
            return drafts_folder
        
        drafts_folder = finder.find_dir_for_drafts_secondary()
        self.actions.send_to_print("")
        self.actions.send_to_print(f"Criando nova pasta de rascunhos: {drafts_folder.name} ")
        self.actions.send_to_print(f"")
        self.actions.send_to_print(f"Se quiser utilizar os novos rascunhos, copie manualmente ")
        self.actions.send_to_print(f"os novos rascunhos para a pasta {lang} ")
        return Path(drafts_folder)

    def download_from_external_source(self) -> bool:
        self.destiny_folder.mkdir(exist_ok=True, parents=True)
        self.copy_readme()
        self.copy_tests()
        return self.copy_drafts()

    def copy_drafts(self):
        self.actions.cached = True
        finder = DraftsFinderCached(self.destiny_folder, self.language)
        if not self.task.is_import_type():
            destiny_drafts_folder: Path = finder.find_dir_for_drafts()
            destiny_drafts_folder.mkdir(exist_ok=True, parents=True)
            self.actions.create_default_draft(destiny_drafts_folder, self.language)
            return True

        destiny_drafts_folder: Path = self.find_and_create_folder_for_drafts()
        origin_drafts_source: Path = CodeFilter.get_source_drafts_dir(self.origin_folder, self.language)
        if not self.copy_drafts_from(origin_drafts_source, destiny_drafts_folder):
            self.actions.create_default_draft(destiny_drafts_folder, self.language)
        if self.task.task_test == self.task.TaskTest.SELF:
            self.actions.create_default_draft(destiny_drafts_folder, "md")
        removed, last_path = finder.remove_secondary_dir_if_duplicated()
        self.actions.cached = False
        if not removed:
            for msg in self.actions.cache_msgs:
                self.actions.send_to_print(msg)
            self.actions.cache_msgs.clear()
        else:
            self.actions.send_to_print(f"Último rascunho em {os.path.basename(last_path)}")
        self.actions.send_to_print("")
        self.actions.send_to_print("Atividade baixada com sucesso")
        return True
    
    def copy_readme(self):
        origin_readme  = self.origin_folder /"README.md"
        destiny_readme = self.destiny_folder/ "README.md"

        source_folder_rel = self.origin_folder.relative_to(self.destiny_folder, walk_up=True)
        content = Decoder.load(origin_readme)
        content = Absolute.change_to_relative_folder(content, source_folder_rel)
        self.actions.compare_and_save_to(content, destiny_readme)
    
    def copy_drafts_from(self, origin_drafts_folder: Path, destiny_draft_folder: Path) -> bool:
        if not os.path.exists(origin_drafts_folder):
            return False
        destiny_draft_folder.mkdir(exist_ok=True)
        if self.copy_drafts_from_cache(origin_drafts_folder, destiny_draft_folder):
            return True
        return False
        

    def copy_drafts_from_cache(self, cache_draft_folder: Path, destiny_draft_folder: Path) -> bool:
        found: bool = False
        for file in cache_draft_folder.iterdir():
            destiny_path = destiny_draft_folder / file.name
            self.actions.compare_and_save_to(Decoder.load(file), destiny_path)
            found = True
        return found
        

    def copy_tests(self):
        source_folder = self.origin_folder
        destiny_folder = self.destiny_folder
        # copy any file with extension .toml or .tio from source_folder to destiny_folder, if they are different
        for file in source_folder.iterdir():
            if file.suffix == ".tio": 
                destiny_path = destiny_folder / file.name
                self.actions.compare_and_save_to(Decoder.load(file), destiny_path)
            if file.suffix == ".toml":
                destiny_path = destiny_folder / file.name
                content = TomlParser.load_and_expand(file)
                self.actions.compare_and_save_to(content, destiny_path)


    def check_and_get_language(self) -> None:
        language_def = self.repo.data.get_lang()

        if self.language == "":
            if language_def != "":
                self.language = language_def
            else:
                langs = self.settings.get_languages_settings().get_languages_with_drafts()
                print("Escolha uma extensão para os rascunhos: [{}]: ".format(", ".join(langs.keys())), end="")
                self.language = input()

class DownActions:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.fnprint: Callable[[str], None] = print
        self.cache_msgs: list[str] = []
        self.cached: bool = False

    def send_to_print(self, text: str):
        if self.cached:
            self.cache_msgs.append(text)
        else:
            self.fnprint(text)

    @staticmethod
    def folder_and_file(path: Path, parts: int = 2) -> str:
        """ Return the folder and file name of the path """
        pieces = path.resolve().parts
        pieces = pieces[-parts:]  # Get the last 'parts' elements
        return os.path.join(*pieces)

    def compare_and_save_to(self, content: str, path: Path):
        if not os.path.exists(path):
            Decoder.save(path, content)
            self.send_to_print(self.folder_and_file(path) + " (Novo)")
        else:
            path_content = Decoder.load(path)
            if path_content != content:
                self.send_to_print(self.folder_and_file(path) + " (Atualizado)")
                Decoder.save(path, content)
            else:
                self.send_to_print(self.folder_and_file(path) + " (Inalterado)")

    def create_default_draft(self, destiny: Path, language: str):
        filename = "draft."
        draft_path = destiny / (filename + language)
        os.makedirs(os.path.dirname(draft_path), exist_ok=True)
        lang_drafts: dict[str, str] = self.settings.get_languages_settings().get_languages_with_drafts()
        if not os.path.exists(draft_path):
            with open(draft_path, "w", encoding="utf-8") as f:
                if language in lang_drafts.keys():
                    f.write(lang_drafts[language])
                else:
                    f.write("")
            self.send_to_print(self.folder_and_file(draft_path, 3) + " (Vazio)")
        else:
            self.send_to_print(self.folder_and_file(draft_path, 3) + " (Não sobrescrito)")
        return draft_path
