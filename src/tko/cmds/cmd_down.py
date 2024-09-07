from typing import Optional, List, Callable
import os
import urllib.request
import urllib.error
import json

from tko.down.down import DownProblem

from ..settings.settings import Settings
from ..game.game import Game
from ..util.remote import RemoteCfg


class CmdDown:
    @staticmethod
    def execute(rep_alias: str, task_key: str, language: Optional[str], settings: Settings, fnprint: Callable[[str], None], game: Optional[Game] = None) -> bool:
        DownProblem.fnprint = fnprint
        rep_dir = os.path.join(settings.app.get_rootdir(), rep_alias)
        rep_source = settings.get_rep_source(rep_alias)
        rep_data = settings.get_rep_data(rep_alias)
        if game is None:
            try:
                file = rep_source.get_file_or_cache(rep_dir)
            except urllib.error.HTTPError:
                DownProblem.fnprint("falha: Verifique sua internet")
            game = Game(file)
        item = game.get_task(task_key)
        if not item.link.startswith("http"):
            DownProblem.fnprint("falha: link para atividade não é um link remoto")
            return False
        cfg = RemoteCfg(item.link)
        cache_url = os.path.dirname(cfg.get_raw_url()) + "/.cache/"

        destiny = DownProblem.create_problem_folder(rep_dir, task_key)
        destiny = os.path.abspath(destiny)
        try:
            [_readme_path, mapi_path] = DownProblem.down_problem_def(destiny, cache_url)
        except urllib.error.HTTPError:
            DownProblem.fnprint("  falha: atividade não encontrada no curso")
            # verifi if destiny folder is empty and remove it
            if len(os.listdir(destiny)) == 0:
                os.rmdir(destiny)
            return False
        except urllib.error.URLError:
            DownProblem.fnprint("  falha: não consegui baixar a atividade, verifique sua internet")
            return False


        with open(mapi_path, encoding="utf-8") as f:
            loaded_json = json.load(f)
        os.remove(mapi_path)

        language_def = rep_data.get_lang()
        if language_def == "":
            language_def = Settings().app.get_lang_default()
        ask_ext = False
        if language is None:
            if language_def != "":
                language = language_def
            else:
                print("  Escolha uma extensão para os rascunhos: [c, cpp, py, ts, js, java]: ", end="")
                language = input()
                ask_ext = True

        DownProblem.unpack_json(loaded_json, destiny, language)
        DownProblem.download_drafts(loaded_json, destiny, language, cache_url, ask_ext)
        return True
