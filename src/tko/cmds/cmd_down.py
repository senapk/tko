from typing import Callable
import os
import shutil


from tko.settings.repository import Repository
from tko.settings.settings import Settings
from tko.game.game import Game
from tko.util.decoder import Decoder
from tko.down.drafts import Drafts
from tko.settings.languages import available_languages
from tko.feno.remote_md import Absolute
from tko.game.task import Task
from tko.feno.filter import CodeFilter

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
    test_case_filename = "tests.toml"
    def __init__(self, rep: Repository, task_key: str, settings: Settings):
        self.rep = rep
        self.task_key = task_key
        self.settings = settings
        self.task: Task = self.rep.game.get_task(self.task_key)
       
        origin_folder = self.task.get_origin_folder()
        if origin_folder is None:
            raise ValueError(f"Atividade {self.task_key} não possui pasta de origem para download")
        self.origin_folder: str = origin_folder
        
        destiny_folder = self.task.get_workspace_folder()
        if destiny_folder is None:
            raise ValueError(f"Atividade {self.task_key} não possui pasta de destino para download")
        self.destiny_folder: str = destiny_folder
       
        self.language: str = ""
        self.check_and_get_language()
        self.actions = DownActions()
        
    def execute(self) -> bool:
        if self.task.is_import_type():
            return self.download_from_external_source()
        if self.task.is_static_type():
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

    def find_folder_for_drafts(self) -> str:
        lang = self.language
        destiny_folder = self.destiny_folder
        drafts_folder = os.path.join(destiny_folder, lang)
        files_under_destiny = os.listdir(destiny_folder)
        on_root = False
        for file in files_under_destiny:
            if file.endswith(f".{lang}"):
                drafts_folder = os.path.join(destiny_folder)
                on_root = True
                break

        if not on_root and not os.path.exists(drafts_folder):
            os.makedirs(drafts_folder, exist_ok=True)
            return drafts_folder
        
        count = 1
        while True:
            drafts_backup_folder = os.path.join(destiny_folder, f"_{lang}.{count}")
            if not os.path.exists(drafts_backup_folder):
                drafts_folder = drafts_backup_folder
                os.makedirs(drafts_folder, exist_ok=True)
                break
            count += 1
        self.actions.send_to_print("")
        self.actions.send_to_print(f"Criando nova pasta de rascunhos: {os.path.basename(drafts_folder)} ")
        self.actions.send_to_print(f"")
        self.actions.send_to_print(f"Se quiser utilizar os novos rascunhos, copie manualmente ")
        self.actions.send_to_print(f"os novos rascunhos para a pasta {lang} ")
        return drafts_folder

    def remove_draft_folder_if_duplicated(self, drafts_folder: str) -> tuple[bool, str]:
        lang = self.language
        destiny_folder = os.path.dirname(drafts_folder)
        parts = drafts_folder.split(".")
        if len(parts) > 1:
            try:
                count = int(parts[-1])
                if count == 1:
                    last_path = os.path.join(destiny_folder, lang)
                else:
                    last = count - 1
                    last_path = ".".join(parts[:-1]) + f".{last}"
                if os.path.exists(last_path):
                    if self.folder_equals(drafts_folder, last_path):
                        shutil.rmtree(drafts_folder)
                        return True, last_path
            except ValueError:
                pass
        return False, ""

    def download_from_external_source(self) -> bool:
        os.makedirs(self.destiny_folder, exist_ok=True)

        self.copy_readme()
        self.copy_tests()


        self.actions.cached = True
        destiny_drafts_folder = self.find_folder_for_drafts()
        origin_source = os.path.join(CodeFilter.get_default_drafts_dir(self.origin_folder), self.language)
        if not self.copy_drafts_from(origin_source, destiny_drafts_folder):
            self.actions.create_default_draft(destiny_drafts_folder, self.language)

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
        origin_readme = os.path.join(self.origin_folder, "README.md")
        destiny_readme = os.path.join(self.destiny_folder, "README.md")

        source_folder_rel = os.path.relpath(self.origin_folder, self.destiny_folder)
        content = Decoder.load(origin_readme)
        content = Absolute.change_to_relative_folder(content, source_folder_rel)
        self.actions.compare_and_save_to(content, destiny_readme)
    
    def copy_drafts_from(self, origin_drafts_folder: str, destiny_draft_folder: str) -> bool:
        if not os.path.exists(origin_drafts_folder):
            return False
        os.makedirs(destiny_draft_folder, exist_ok=True)
        if self.copy_drafts_from_cache(origin_drafts_folder, destiny_draft_folder):
            return True
        return False
        

    def copy_drafts_from_cache(self, cache_draft_folder: str, destiny_draft_folder: str) -> bool:
        found: bool = False
        for file in os.listdir(cache_draft_folder):
            source_path = os.path.join(cache_draft_folder, file)
            destiny_path = os.path.join(destiny_draft_folder, file)
            if os.path.isfile(source_path):
                self.actions.compare_and_save_to(Decoder.load(source_path), destiny_path)
                found = True
        return found
        

    def copy_tests(self):
        source_folder = self.origin_folder
        destiny_folder = self.destiny_folder
        # copy any file with extension .toml or .tio from source_folder to destiny_folder, if they are different
        for file in os.listdir(source_folder):
            if file.endswith(".toml") or file.endswith(".tio"):
                source_path = os.path.join(source_folder, file)
                destiny_path = os.path.join(destiny_folder, file)
                if os.path.isfile(source_path):
                    self.actions.compare_and_save_to(Decoder.load(source_path), destiny_path)


    @staticmethod
    def folder_equals(folder1: str, folder2: str) -> bool:
        """ Compare two folders and return if they have the same files with the same content """
        if not os.path.exists(folder1) or not os.path.exists(folder2):
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
        language_def = self.rep.data.get_lang()

        if self.language == "":
            if language_def != "":
                self.language = language_def
            else:
                print("Escolha uma extensão para os rascunhos: [{}]: ".format(", ".join(available_languages)), end="")
                self.language = input()

class DownActions:
    def __init__(self):
        self.fnprint: Callable[[str], None] = print
        self.cache_msgs: list[str] = []
        self.cached: bool = False

    def send_to_print(self, text: str):
        if self.cached:
            self.cache_msgs.append(text)
        else:
            self.fnprint(text)

    @staticmethod
    def folder_and_file(path: str, parts: int = 2) -> str:
        """ Return the folder and file name of the path """
        pieces = path.split(os.sep)
        pieces = pieces[-parts:]  # Get the last 'parts' elements
        return os.path.join(*pieces)

    def compare_and_save_to(self, content: str, path: str):
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

    def create_default_draft(self, destiny: str, language: str) -> str:
        filename = "draft."
        draft_path = os.path.join(destiny, filename + language)
        os.makedirs(os.path.dirname(draft_path), exist_ok=True)
        if not os.path.exists(draft_path):
            with open(draft_path, "w", encoding="utf-8") as f:
                if language in Drafts.drafts:
                    f.write(Drafts.drafts[language])
                else:
                    f.write("")
            self.send_to_print(self.folder_and_file(draft_path, 3) + " (Vazio)")
        else:
            self.send_to_print(self.folder_and_file(draft_path, 3) + " (Não sobrescrito)")
        return draft_path
