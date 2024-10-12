from typing import Optional, List, Callable
import os
import urllib.request
import urllib.error
import json

from tko.settings.repository import Repository
from tko.down.down import DownProblem

from tko.settings.settings import Settings
from tko.game.game import Game
from tko.util.remote_url import RemoteUrl
from tko.cmds.cmd_build import CmdBuild
from tko.util.param import Param


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
    
    def get_game(self):
        if self.game is not None:
            return self.game
        try:
            file = self.rep.load_index_or_cache()
        except urllib.error.HTTPError:
            DownProblem.fnprint("falha: Verifique sua internet")
        return Game(file)

    def remove_empty_destiny_folder(self):
        if len(os.listdir(self.destiny_folder)) == 0:
                os.rmdir(self.destiny_folder)

    def download_readme(self, readme_remote_url) -> bool:
        DownProblem.create_problem_folder(self.destiny_folder)
        try:
            DownProblem.down_readme(self.readme_path, readme_remote_url)
            return True
        except urllib.error.HTTPError:
            DownProblem.fnprint("  falha: Arquivo de descrição não encontrado")
            return False
        except urllib.error.URLError:
            DownProblem.fnprint("  falha: Não consegui baixar a atividade, verifique sua internet")
            return False

    def download_mapi(self) -> bool:
        try:
            urllib.request.urlretrieve(self.cache_url + "mapi.json", self.mapi_file)
            return True
        except urllib.error.HTTPError:
            return False
        except urllib.error.URLError:
            DownProblem.fnprint("  falha: não consegui baixar a atividade, verifique sua internet")
            return False

    def build_cases_from_readme(self):
        cases_tio_target = os.path.join(self.rep.get_rep_dir(), self.task_key, "cases.tio")
        param = Param.Manip()
        cb = CmdBuild(cases_tio_target, [self.readme_path], param)
        cb.set_quiet(True)
        cb.execute()

    def execute(self) -> bool:
        item = self.get_game().get_task(self.task_key)
        if not item.link.startswith("http"):
            DownProblem.fnprint("falha: link para atividade não é um link remoto")
            return False
        
        readme_remote_url = RemoteUrl(item.link)
        self.cache_url = os.path.dirname(readme_remote_url.get_raw_url()) + "/.cache/"
        self.destiny_folder = os.path.abspath(os.path.join(self.rep.get_rep_dir(), self.task_key))
        self.readme_path =  os.path.join(self.destiny_folder, "Readme.md")
        self.mapi_file = os.path.join(self.destiny_folder, "mapi.json")
        if not self.download_readme(readme_remote_url):
            return False
        
        lang = self.check_and_select_language()
        
        if self.download_mapi():
            with open(self.mapi_file, encoding="utf-8") as f:
                loaded_json = json.load(f)
            os.remove(self.mapi_file)
            DownProblem.unpack_json(loaded_json, self.destiny_folder, lang)
            if not DownProblem.check_draft_existence(loaded_json, self.destiny_folder, lang, self.cache_url):
                DownProblem.create_default_draft(self.destiny_folder, lang)
        else:
            self.build_cases_from_readme()
            DownProblem.create_default_draft(self.destiny_folder, lang)
        DownProblem.fnprint("")
        DownProblem.fnprint("Atividade baixada com sucesso")
        return True

    def check_and_select_language(self) -> str:
        language_def = self.rep.get_lang()
        if language_def == "":
            language_def = Settings().app.get_lang_default()

        if self.language is None:
            if language_def != "":
                self.language = language_def
            else:
                print("  Escolha uma extensão para os rascunhos: [c, cpp, py, ts, js, java]: ", end="")
                self.language = input()
        return self.language
