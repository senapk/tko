from tko.down.drafts import Drafts


import os
import urllib.error
import urllib.request
import tempfile
from tko.util.remote_url import RemoteUrl
from typing import Callable, Tuple


class DownProblem:
    fnprint: Callable[[str], None] = print

    @staticmethod
    def __create_file(content, path, label=""):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        DownProblem.fnprint("  " + path + " " + label)

    @staticmethod
    def unpack_json(loaded, destiny, lang: str):
        # extracting all files to folder
        for entry in loaded["upload"]:
            if entry["name"] == "vpl_evaluate.cases":
                DownProblem.__compare_and_save(entry["contents"], os.path.join(destiny, "cases.tio"))

        if "draft" in loaded:
            if lang in loaded["draft"]:
                for file in loaded["draft"][lang]:
                    path = os.path.join(destiny, file["name"])
                    DownProblem.__create_file(file["contents"], path, "(Rascunho)")

    @staticmethod
    def __compare_and_save(content: str, path: str):
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content.encode("utf-8").decode("utf-8"))
            DownProblem.fnprint("  " + path + " (Novo)")
        else:
            if open(path, encoding="utf-8").read() != content:
                DownProblem.fnprint("  " + path + " (Atualizado)")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
            else:
                DownProblem.fnprint("  " + path + " (Inalterado)")

    @staticmethod
    def down_readme(readme_path: str,  remote_url: RemoteUrl):
        temp_file = tempfile.mktemp()
        remote_url.download_absolute_to(temp_file)
        content = open(temp_file, encoding="utf-8").read()
        DownProblem.__compare_and_save(content, readme_path)
    
    @staticmethod
    def create_problem_folder(destiny: str):
        if not os.path.exists(destiny):
            os.makedirs(destiny, exist_ok=True)
        else:
            DownProblem.fnprint("  Pasta do problema "+ destiny + " encontrada, juntando conteúdo.")

    @staticmethod
    def check_draft_existence(loaded_json, destiny: str, language: str, cache_url: str) -> bool:
        if len(loaded_json["required"]) == 1:  # you already have the students file
            return True

        if "draft" in loaded_json and language in loaded_json["draft"]:
            return True
        try:
            draft_path = os.path.join(destiny, "draft." + language)
            urllib.request.urlretrieve(cache_url + "draft." + language, draft_path)
            DownProblem.fnprint("  " + draft_path + " (Rascunho)")
            return True
        except urllib.error.HTTPError:  # draft not found
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
            DownProblem.fnprint("  " + draft_path + " (Vazio)")
        else:
            DownProblem.fnprint("  " + draft_path + " (Não sobrescrito)")