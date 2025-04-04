from typing import Callable
import os
import urllib.request
import urllib.error
import json
import tempfile
import shutil

from tko.game.task import Task
from tko.settings.repository import Repository
from tko.settings.settings import Settings
from tko.game.game import Game
from tko.util.remote_url import RemoteUrl
from tko.cmds.cmd_build import CmdBuild
from tko.util.param import Param
from tko.util.decoder import Decoder
from tko.down.drafts import Drafts
from tko.settings.repository import available_languages
from icecream import ic # type: ignore

class CmdLineDown:
    def __init__(self, settings: Settings, folder: str, task_key: str):
        self.settings = settings
        self.folder = folder
        self.task_key = task_key
        ic("entrei no cmdlinedown")
        self.rep = Repository(folder)
        
    def execute(self):
        ic(self.rep.get_config_file())
        if not self.rep.has_local_config_file():
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

    def download_readme(self, readme_remote_url) -> bool:
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
            ic(mapi_url)
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
        ic("baixando da url")
        readme_remote_url = RemoteUrl(task_source)
        remote_url = readme_remote_url.get_raw_url()
        self.cache_url = os.path.dirname(remote_url) + "/.cache/"
        self.destiny_folder = self.rep.get_task_folder_for_label(self.task_key)
        self.readme_path =  os.path.join(self.destiny_folder, "Readme.md")
        self.mapi_file = os.path.join(self.destiny_folder, "mapi.json")
        ic(self.mapi_file)

        folder_created = DownProblem.create_problem_folder(self.destiny_folder)
        if not self.download_readme(readme_remote_url):
            if folder_created:
                self.remove_empty_destiny_folder()
            return False
        
        lang = self.check_and_select_language()
        
        if self.download_mapi():
            encoding = Decoder.get_encoding(self.mapi_file)
            with open(self.mapi_file, encoding=encoding) as f:
                loaded_json = json.load(f)
            # os.remove(self.mapi_file)
            DownProblem.unpack_problem_files(loaded_json, self.destiny_folder)
            if not DownProblem.unpack_json_drafts(loaded_json, self.destiny_folder, lang):
                DownProblem.create_default_draft(self.destiny_folder, lang)
        else:
            self.build_cases_from_readme(self.destiny_folder)
            DownProblem.create_default_draft(self.destiny_folder, lang)
        DownProblem.fnprint("")
        DownProblem.fnprint("Atividade baixada com sucesso")
        return True

    def download_from_external_file(self, task_source: str) -> bool:
        if not os.path.exists(task_source):
            DownProblem.fnprint("Arquivo fonte não encontrado")
        self.cache_url = os.path.join(os.path.dirname(task_source), ".cache")
        self.destiny_folder = self.rep.get_task_folder_for_label(self.task_key)
        self.readme_path =  os.path.join(self.destiny_folder, "Readme.md")
        self.mapi_file = os.path.join(self.cache_url, "mapi.json")
        folder_created = DownProblem.create_problem_folder(self.destiny_folder)
        # Decoder.save(self.readme_path, Decoder.load(task_source))
        DownProblem.compare_and_save(Decoder.load(task_source), self.readme_path)

        lang = self.check_and_select_language()
        
        if os.path.isfile(self.mapi_file):
            encoding = Decoder.get_encoding(self.mapi_file)
            with open(self.mapi_file, encoding=encoding) as f:
                loaded_json = json.load(f)
            DownProblem.unpack_problem_files(loaded_json, self.destiny_folder)
            if not DownProblem.unpack_json_drafts(loaded_json, self.destiny_folder, lang):
                if not folder_created:
                    DownProblem.create_default_draft(self.destiny_folder, lang)
        else:
            self.build_cases_from_readme(self.destiny_folder)
            DownProblem.create_default_draft(self.destiny_folder, lang)
        DownProblem.fnprint("")
        DownProblem.fnprint("Atividade carregada com sucesso")
        return True

    def execute(self) -> bool:
        ic("debug", "entrei no execute")
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
    def __create_file(content, path, label=""):
        Decoder.save(path, content)
        DownProblem.fnprint(path + " " + label)

    @staticmethod
    def unpack_json_drafts(loaded, destiny, lang: str) -> bool:
        found = False
        if "draft" in loaded:
            if lang in loaded["draft"]:
                for file in loaded["draft"][lang]:
                    path = os.path.join(destiny, file["name"])
                    DownProblem.__create_file(file["contents"], path, "(Rascunho)")
                    found = True

        return found

    @staticmethod
    def unpack_problem_files(loaded, destiny):
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
    def  compare_and_save(content: str, path: str):
        if not os.path.exists(path):
            Decoder.save(path, content)
            DownProblem.fnprint(path + " (Novo)")
        else:
            path_content = Decoder.load(path)
            if path_content != content:
                DownProblem.fnprint(path + " (Atualizado)")
                Decoder.save(path, content)
            else:
                DownProblem.fnprint(path + " (Inalterado)")

    @staticmethod
    def down_readme(readme_path: str,  remote_url: RemoteUrl):
        temp_file = tempfile.mktemp()
        remote_url.download_absolute_to(temp_file)
        content = Decoder.load(temp_file)
        DownProblem.compare_and_save(content, readme_path)
    
    @staticmethod
    def create_problem_folder(destiny: str) -> bool:
        if not os.path.exists(destiny):
            os.makedirs(destiny, exist_ok=True)
            return True
        
        DownProblem.fnprint("Pasta do problema "+ destiny + " encontrada, juntando conteúdo.")
        return False

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
            DownProblem.fnprint(draft_path + " (Vazio)")
        else:
            DownProblem.fnprint(draft_path + " (Não sobrescrito)")