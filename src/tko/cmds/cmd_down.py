from typing import Callable, Any
import os
import urllib.request
import urllib.error
import json
import shutil
import tempfile


from tko.game.task import Task
from tko.settings.repository import Repository
from tko.settings.settings import Settings
from tko.game.game import Game
from tko.util.remote_url import RemoteUrl
from tko.cmds.cmd_build import CmdBuild
from tko.util.param import Param
from tko.util.decoder import Decoder
from tko.down.drafts import Drafts
from tko.settings.languages import available_languages
from tko.feno.remote_md import Absolute

class CmdLineDown:
    def __init__(self, settings: Settings, rep: Repository, task_key: str):
        self.settings = settings
        self.rep = rep
        self.task_key = task_key
        
    def execute(self):
        if not self.rep.paths.has_local_config_file():
            print("O parâmetro para o comando tko down deve a pasta onde você iniciou o repositório.")
            print("Navegue ou passe o caminho até a pasta do repositório e tente novamente.")
            return False
        self.rep.load_config().load_game()
        CmdDown(self.rep, self.task_key, self.settings).execute()
        return True


class CmdDown:
    test_case_filename = "cases.tio"
    def __init__(self, rep: Repository, task_key: str, settings: Settings):
        self.rep = rep
        self.task_key = task_key
        self.settings = settings
        self.game: Game | None = None
        self.destiny_folder = self.rep.get_task_folder_for_label(self.task_key)
        self.readme_path =  os.path.join(self.destiny_folder, "Readme.md")
        self.language: str = ""
        self.actions = DownActions()
        
    def set_fnprint(self, fnprint: Callable[[str], None]):
        self.actions.fnprint = fnprint
        return self

    def set_game(self, game: Game):
        self.game = game
        return self
    
    def set_language(self, language: str):
        self.language = language
        return self

    def remove_empty_destiny_folder(self):
        if len(os.listdir(self.destiny_folder)) == 0:
                os.rmdir(self.destiny_folder)

    def download_readme(self, readme_remote_url: RemoteUrl) -> bool:
        try:
            self.actions.down_readme(self.readme_path, readme_remote_url)
            return True
        except urllib.error.HTTPError:
            self.actions.send_to_print("falha: Arquivo de descrição não encontrado")
            return False
        except urllib.error.URLError:
            self.actions.send_to_print("falha: Não consegui baixar a atividade, verifique sua internet")
            return False

    def download_mapi(self, cache_url: str) -> tuple[bool, str]:
        try:
            mapi_url = cache_url + "mapi.json"
            mapi_path = os.path.join(self.destiny_folder, "mapi.json")
            urllib.request.urlretrieve(mapi_url, mapi_path)
            return True, mapi_path
        except urllib.error.HTTPError:
            return False, ""
        except urllib.error.URLError:
            self.actions.send_to_print("falha: não consegui baixar a atividade, verifique sua internet")
            return False, ""

    def build_cases_from_readme(self, destiny_folder: str):
        cases_tio_target = os.path.join(destiny_folder, CmdDown.test_case_filename)
        param = Param.Manip()
        cb = CmdBuild(cases_tio_target, [self.readme_path], param)
        cb.set_quiet(True)
        cb.execute()

    def find_folder_for_drafts(self, destiny_folder: str, lang: str) -> str:
        drafts_folder = os.path.join(destiny_folder, lang)
        files_under_destiny = os.listdir(destiny_folder)
        on_root = False
        for file in files_under_destiny:
            if file.endswith(f".{lang}"):
                drafts_folder = os.path.join(destiny_folder, file)
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
        self.actions.send_to_print(f"Criando nova pasta de rascunhos: {os.path.basename(drafts_folder)}")
        self.actions.send_to_print(f"Se quiser utilizar, copie manualmente")
        self.actions.send_to_print(f"os novos rascunhos para a pasta {lang}")
        return drafts_folder

    def remove_draft_folder_if_duplicated(self, drafts_folder: str, lang: str) -> tuple[bool, str]:
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


    def download_readme_cases_and_drafts(self, mapi_path: str) -> None:
        lang = self.check_and_select_language()

        loaded_json: dict[str, Any] | None = None
        if mapi_path != "" and os.path.isfile(mapi_path):
            encoding = Decoder.get_encoding(mapi_path)
            with open(mapi_path, encoding=encoding) as f:
                loaded_json = json.load(f)
            if loaded_json is not None:
                self.actions.unpack_problem_files(loaded_json, self.destiny_folder)

        test_case_path = os.path.join(self.destiny_folder, CmdDown.test_case_filename)
        if not os.path.isfile(test_case_path):
            self.build_cases_from_readme(self.destiny_folder)
        with open(test_case_path, "r", encoding="utf-8") as f:
            content = f.read()
        if content.strip() == "":
            os.remove(test_case_path)
        self.actions.cached = True
        drafts_folder = self.find_folder_for_drafts(self.destiny_folder, lang)
        if not self.actions.unpack_json_drafts(loaded_json, drafts_folder, lang):
            self.actions.create_default_draft(drafts_folder, lang)
        
        removed, last_path = self.remove_draft_folder_if_duplicated(drafts_folder, lang)
        self.actions.cached = False
        if not removed:
            for msg in self.actions.cache_msgs:
                self.actions.send_to_print(msg)
            self.actions.cache_msgs.clear()
        else:
            self.actions.send_to_print(f"Último rascunho em {os.path.basename(last_path)}")
        self.actions.send_to_print("")
        self.actions.send_to_print("Atividade baixada com sucesso")

    def download_from_url(self, task_source: str) -> bool:
        readme_remote_url = RemoteUrl(task_source)
        remote_url = readme_remote_url.get_raw_url()
        os.makedirs(self.destiny_folder, exist_ok=True)
        if not self.download_readme(readme_remote_url):
            self.remove_empty_destiny_folder()
            return False
        cache_url = os.path.dirname(remote_url) + "/.cache/"
        _, mapi_path = self.download_mapi(cache_url)
        self.download_readme_cases_and_drafts(mapi_path)
        if os.path.isfile(mapi_path):
            os.remove(mapi_path)
        return True

    def download_from_external_file(self, task_source: str) -> bool:
        if not os.path.exists(task_source):
            self.actions.send_to_print(f"Arquivo fonte não encontrado para carregar a atividade {self.task_key}")
            return False
        os.makedirs(self.destiny_folder, exist_ok=True)
        source_folder_abs = os.path.dirname(task_source)
        source_folder_rel = os.path.relpath(source_folder_abs, self.destiny_folder)
        content = Decoder.load(task_source)
        content = Absolute.change_to_relative_folder(content, source_folder_rel)
        self.actions.compare_and_save(content, self.readme_path)
        mapi_file = os.path.join(os.path.dirname(task_source), ".cache", "mapi.json")
        self.download_readme_cases_and_drafts(mapi_file)
        return True


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



    def execute(self) -> bool:
        task = self.rep.game.get_task(self.task_key)
        if task.link_type == Task.Types.REMOTE_FILE:
            return self.download_from_url(task.link)
        if task.link_type == Task.Types.IMPORT_FILE:
            return self.download_from_external_file(task.link)
        self.actions.send_to_print("falha: link para atividade não possui link para download")
        return False

    def check_and_select_language(self) -> str:
        language_def = self.rep.data.get_lang()

        if self.language == "":
            if language_def != "":
                self.language = language_def
            else:
                print("Escolha uma extensão para os rascunhos: [{}]: ".format(", ".join(available_languages)), end="")
                self.language = input()
        return self.language

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

    def __create_file(self, content: str, path: str, label: str="", parts: int = 2):
        Decoder.save(path, content)
        self.send_to_print(DownActions.folder_and_file(path, parts) + " " + label)

    def unpack_json_drafts(self, loaded: dict[str, Any] | None, destiny: str, lang: str) -> bool:
        if loaded is None:
            return False
        found = False
        if "draft" in loaded:
            if lang in loaded["draft"]:
                for file in loaded["draft"][lang]:
                    path = os.path.join(destiny, file["name"])
                    self.__create_file(file["contents"], path, "(Rascunho)", 3)
                    found = True

        return found

    def unpack_problem_files(self, loaded: dict[str, Any], destiny: str):
        if "upload" in loaded:
            for file in loaded["upload"]:
                name = file["name"]
                if name == "vpl_evaluate.cases":
                    name = CmdDown.test_case_filename
                path = os.path.join(destiny, name)
                self.compare_and_save(file["contents"], path)
        if "keep" in loaded:
            for file in loaded["keep"]:
                name = file["name"]
                if name == "vpl_evaluate.cases":
                    name = CmdDown.test_case_filename
                path = os.path.join(destiny, name)
                self.compare_and_save(file["contents"], path)

    @staticmethod
    def folder_and_file(path: str, parts: int = 2) -> str:
        """ Return the folder and file name of the path """
        pieces = path.split(os.sep)
        pieces = pieces[-parts:]  # Get the last 'parts' elements
        return os.path.join(*pieces)

    def compare_and_save(self, content: str, path: str):
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

    def down_readme(self, readme_path: str,  remote_url: RemoteUrl):
        _, temp_file= tempfile.mkstemp()
        remote_url.download_absolute_to(temp_file)
        content = Decoder.load(temp_file)
        self.compare_and_save(content, readme_path)

    def create_default_draft(self, destiny: str, language: str):
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
