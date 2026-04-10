from typing import Callable
import os
import shutil

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

    @staticmethod
    def get_default_dir_for_drafts(task_folder: Path):
        return task_folder / 'src'

    def source_on_root(self, path: Path) -> bool:
        for file in path.iterdir():
            if file.suffix == self.language:
                return True
        return False
    
    def source_on_lang_folder(self, path: Path) -> bool:
        lang_folder = path / self.language
        if not lang_folder.exists():
            return False
        for file in lang_folder.iterdir():
            if file.suffix == self.language:
                return True
        return False

    def find_and_create_folder_for_drafts(self) -> Path:
        lang = self.language
        default_drafts_folder: Path = self.get_default_dir_for_drafts(self.destiny_folder) / lang
        on_root = self.source_on_root(self.destiny_folder)
        if on_root:
            return self.destiny_folder
        on_lang = self.source_on_lang_folder(self.destiny_folder)
        if on_lang:
            return self.destiny_folder / lang
        if not default_drafts_folder.exists():
            default_drafts_folder.mkdir(parents=True, exist_ok=True)
            return default_drafts_folder
        
        count = 1
        while True:
            drafts_backup_folder = self.get_default_dir_for_drafts(self.destiny_folder)/ f"_{lang}.{count}"
            if not os.path.exists(drafts_backup_folder):
                default_drafts_folder = drafts_backup_folder
                os.makedirs(default_drafts_folder, exist_ok=True)
                break
            count += 1
        self.actions.send_to_print("")
        self.actions.send_to_print(f"Criando nova pasta de rascunhos: {os.path.basename(default_drafts_folder)} ")
        self.actions.send_to_print(f"")
        self.actions.send_to_print(f"Se quiser utilizar os novos rascunhos, copie manualmente ")
        self.actions.send_to_print(f"os novos rascunhos para a pasta {lang} ")
        return Path(default_drafts_folder)

    def remove_draft_folder_if_duplicated(self, drafts_folder: Path) -> tuple[bool, Path]:
        lang = self.language
        destiny_folder = drafts_folder.parent
        parts = drafts_folder.name.split(".")
        if len(parts) > 1:
            try:
                count = int(parts[-1])
                if count == 1:
                    last_path = os.path.join(destiny_folder, lang)
                else:
                    last = count - 1
                    last_path = ".".join(parts[:-1]) + f".{last}"
                if os.path.exists(last_path):
                    if self.folder_equals(drafts_folder, Path(last_path)):
                        shutil.rmtree(drafts_folder)
                        return True, Path(last_path)
            except ValueError:
                pass
        return False, Path("")

    def download_from_external_source(self) -> bool:
        os.makedirs(self.destiny_folder, exist_ok=True)

        self.copy_readme()
        self.copy_tests()
        return self.copy_drafts()

    def copy_drafts(self):
        self.actions.cached = True
        if self.task.is_import_type():
            destiny_drafts_folder: Path = self.find_and_create_folder_for_drafts()
        else:
            destiny_drafts_folder: Path = self.get_default_dir_for_drafts(self.destiny_folder) / self.language
            os.makedirs(destiny_drafts_folder, exist_ok=True)

        origin_drafts_source: Path = CodeFilter.get_default_drafts_dir(self.origin_folder) / self.language
        
        if not self.copy_drafts_from(origin_drafts_source, destiny_drafts_folder):
            self.actions.create_default_draft(destiny_drafts_folder, self.language)
        if self.task.task_test == self.task.TaskTest.SELF:
            self.actions.create_default_draft(destiny_drafts_folder, "md")

        if self.task.is_import_type():
            removed, last_path = self.remove_draft_folder_if_duplicated(destiny_drafts_folder)
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


    @staticmethod
    def folder_equals(folder1: Path, folder2: Path) -> bool:
        """ Compare two folders and return if they have the same files with the same content """
        if not folder1.exists() or not folder2.exists():
            return False
        if len(os.listdir(folder1)) != len(os.listdir(folder2)):
            return False
        for file in os.listdir(folder1):
            path1 = os.path.join(folder1, file)
            path2 = os.path.join(folder2, file)
            if not os.path.isfile(path1) or not os.path.isfile(path2):
                return False
            with open(path1, "rb") as f1, open(path2, "rb") as f2:
                if f1.read() != f2.read():
                    return False
        return True

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
        pieces = path.parts
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
