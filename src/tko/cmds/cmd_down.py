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
    def __init__(self, rep: Repository, task_key: str, settings: Settings):
        self.rep = rep
        self.task_key = task_key
        self.settings = settings
        self.game: Game | None = None
        self.language: str | None = None
        self.destiny_folder: str = ""
        self.readme_path: str = ""
        self.cache_url: str = ""
        self.mapi_file: str = ""

    def set_fnprint(self, fnprint: Callable[[str], None]):
        DownProblem.fnprint = fnprint
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
            DownProblem.down_readme(self.readme_path, readme_remote_url)
            return True
        except urllib.error.HTTPError:
            DownProblem.fnprint("falha: Arquivo de descrição não encontrado")
            return False
        except urllib.error.URLError:
            DownProblem.fnprint("falha: Não consegui baixar a atividade, verifique sua internet")
            return False

    def download_mapi(self) -> bool:
        try:
            mapi_url = self.cache_url + "mapi.json"
            urllib.request.urlretrieve(mapi_url, self.mapi_file)
            return True
        except urllib.error.HTTPError:
            return False
        except urllib.error.URLError:
            DownProblem.fnprint("falha: não consegui baixar a atividade, verifique sua internet")
            return False

    def build_cases_from_readme(self, destiny_folder: str):
        cases_tio_target = os.path.join(destiny_folder, "cases.tio")
        param = Param.Manip()
        cb = CmdBuild(cases_tio_target, [self.readme_path], param)
        cb.set_quiet(True)
        cb.execute()

    def download_from_url(self, task_source: str) -> bool:
        readme_remote_url = RemoteUrl(task_source)
        remote_url = readme_remote_url.get_raw_url()
        self.cache_url = os.path.dirname(remote_url) + "/.cache/"
        self.destiny_folder = self.rep.get_task_folder_for_label(self.task_key)
        self.readme_path =  os.path.join(self.destiny_folder, "Readme.md")
        self.mapi_file = os.path.join(self.destiny_folder, "mapi.json")

        backup_folder = DownProblem.backup_and_create_problem_folder(self.destiny_folder)
        if not self.download_readme(readme_remote_url):
            self.remove_empty_destiny_folder()
            return False
        
        lang = self.check_and_select_language()
        
        if self.download_mapi():
            encoding = Decoder.get_encoding(self.mapi_file)
            with open(self.mapi_file, encoding=encoding) as f:
                loaded_json = json.load(f)
            os.remove(self.mapi_file)
            DownProblem.unpack_problem_files(loaded_json, self.destiny_folder)
            if not DownProblem.unpack_json_drafts(loaded_json, self.destiny_folder, lang):
                DownProblem.create_default_draft(self.destiny_folder, lang)
        else:
            self.build_cases_from_readme(self.destiny_folder)
            DownProblem.create_default_draft(self.destiny_folder, lang)
        DownProblem.fnprint("")
        DownProblem.fnprint("Atividade baixada com sucesso")
        if backup_folder != "":
            if CmdDown.folder_equals(self.destiny_folder, backup_folder):
                DownProblem.fnprint("Pastas {} e {} são iguais".format(os.path.basename(self.destiny_folder), os.path.basename(backup_folder)))
                DownProblem.fnprint("Removendo pasta de backup {}".format(os.path.basename(backup_folder)))
                shutil.rmtree(backup_folder, ignore_errors=True)

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


    def download_from_external_file(self, task_source: str) -> bool:
        if not os.path.exists(task_source):
            DownProblem.fnprint("Arquivo fonte não encontrado")
        self.cache_url = os.path.join(os.path.dirname(task_source), ".cache")
        self.destiny_folder = self.rep.get_task_folder_for_label(self.task_key)
        self.readme_path =  os.path.join(self.destiny_folder, "Readme.md")
        self.mapi_file = os.path.join(self.cache_url, "mapi.json")
        backup_folder = DownProblem.backup_and_create_problem_folder(self.destiny_folder)
        # Decoder.save(self.readme_path, Decoder.load(task_source))
        DownProblem.compare_and_save(Decoder.load(task_source), self.readme_path)

        lang = self.check_and_select_language()
        
        if os.path.isfile(self.mapi_file):
            encoding = Decoder.get_encoding(self.mapi_file)
            with open(self.mapi_file, encoding=encoding) as f:
                loaded_json = json.load(f)
            DownProblem.unpack_problem_files(loaded_json, self.destiny_folder)
            if not DownProblem.unpack_json_drafts(loaded_json, self.destiny_folder, lang):
                if not backup_folder:
                    DownProblem.create_default_draft(self.destiny_folder, lang)
        else:
            self.build_cases_from_readme(self.destiny_folder)
            DownProblem.create_default_draft(self.destiny_folder, lang)
        DownProblem.fnprint("")
        DownProblem.fnprint("Atividade carregada com sucesso")
        return True

    def execute(self) -> bool:
        task = self.rep.game.get_task(self.task_key)
        if task.link_type == Task.Types.REMOTE_FILE:
            return self.download_from_url(task.link)
        if task.link_type == Task.Types.IMPORT_FILE:
            return self.download_from_external_file(task.link)
        DownProblem.fnprint("falha: link para atividade não possui link para download")
        return False

    def check_and_select_language(self) -> str:
        language_def = self.rep.get_lang()

        if self.language is None:
            if language_def != "":
                self.language = language_def
            else:
                print("Escolha uma extensão para os rascunhos: [{}]: ".format(", ".join(available_languages)), end="")
                self.language = input()
        return self.language

class DownProblem:
    fnprint: Callable[[str], None] = print

    @staticmethod
    def __create_file(content: str, path: str, label: str=""):
        Decoder.save(path, content)
        DownProblem.fnprint(DownProblem.folder_and_file(path) + " " + label)

    @staticmethod
    def unpack_json_drafts(loaded: dict[str, Any], destiny: str, lang: str) -> bool:
        found = False
        if "draft" in loaded:
            if lang in loaded["draft"]:
                for file in loaded["draft"][lang]:
                    path = os.path.join(destiny, file["name"])
                    DownProblem.__create_file(file["contents"], path, "(Rascunho)")
                    found = True

        return found

    @staticmethod
    def unpack_problem_files(loaded: dict[str, Any], destiny: str):
        if "upload" in loaded:
            for file in loaded["upload"]:
                name = file["name"]
                if name == "vpl_evaluate.cases":
                    name = "cases.tio"
                path = os.path.join(destiny, name)
                DownProblem.compare_and_save(file["contents"], path)
        if "keep" in loaded:
            for file in loaded["keep"]:
                name = file["name"]
                if name == "vpl_evaluate.cases":
                    name = "cases.tio"
                path = os.path.join(destiny, name)
                DownProblem.compare_and_save(file["contents"], path)

    @staticmethod
    def folder_and_file(path: str) -> str:
        """ Return the folder and file name of the path """
        folder = os.path.basename(os.path.dirname(path))
        file = os.path.basename(path)
        return os.path.join(folder, file)

    @staticmethod
    def  compare_and_save(content: str, path: str):
        if not os.path.exists(path):
            Decoder.save(path, content)
            DownProblem.fnprint(DownProblem.folder_and_file(path) + " (Novo)")
        else:
            path_content = Decoder.load(path)
            if path_content != content:
                DownProblem.fnprint(DownProblem.folder_and_file(path) + " (Atualizado)")
                Decoder.save(path, content)
            else:
                DownProblem.fnprint(DownProblem.folder_and_file(path) + " (Inalterado)")

    @staticmethod
    def down_readme(readme_path: str,  remote_url: RemoteUrl):
        temp_file = tempfile.mktemp()
        remote_url.download_absolute_to(temp_file)
        content = Decoder.load(temp_file)
        DownProblem.compare_and_save(content, readme_path)
    
    @staticmethod
    def backup_and_create_problem_folder(destiny: str) -> str:
        """ If destiny exists, rename it to destiny+1, destiny+2, etc.
        If backup was created, return the new name.
        If not, return empty string.
        """
        new_destiny = ""
        if os.path.exists(destiny): # move folder to 
            count = 1
            while True:
                new_destiny = "{}+{}".format(destiny, count)
                if not os.path.exists(new_destiny):
                    shutil.move(destiny, new_destiny)
                    DownProblem.fnprint("Pasta {} já existe".format(os.path.basename(destiny)))
                    DownProblem.fnprint("Renomeando para {}".format(os.path.basename(new_destiny)))
                    break
                else:
                    count += 1
        nova = "" if new_destiny == "" else " nova"
        DownProblem.fnprint("Criando{} pasta {}".format(nova, os.path.basename(destiny)))
        os.makedirs(destiny, exist_ok=True)
        DownProblem.fnprint("")
        return new_destiny

    @staticmethod
    def create_default_draft(destiny: str, language: str):
        filename = "draft."
        draft_path = os.path.join(destiny, filename + language)

        if not os.path.exists(draft_path):
            with open(draft_path, "w", encoding="utf-8") as f:
                if language in Drafts.drafts:
                    f.write(Drafts.drafts[language])
                else:
                    f.write("")
            DownProblem.fnprint(DownProblem.folder_and_file(draft_path) + " (Vazio)")
        else:
            DownProblem.fnprint(DownProblem.folder_and_file(draft_path) + " (Não sobrescrito)")
