from tko.down.drafts import Drafts


import os
import urllib.error
import urllib.request
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
                    DownProblem.__create_file(file["contents"], path, "(Draft)")

    @staticmethod
    def __compare_and_save(content, path):
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content.encode("utf-8").decode("utf-8"))
            DownProblem.fnprint("  " + path + " (Novo)")
        else:
            if open(path, encoding="utf-8").read() != content:
                DownProblem.fnprint(path + " (Atualizado)")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
            else:
                DownProblem.fnprint("  " + path + " (Inalterado)")

    @staticmethod
    def down_problem_def(destiny, cache_url) -> Tuple[str, str]:
        # downloading Readme
        readme = os.path.join(destiny, "Readme.md")
        [tempfile, __content] = urllib.request.urlretrieve(cache_url + "Readme.md")

        # content = ""
        try:
            content = open(tempfile, encoding="utf-8").read()
        except FileNotFoundError:
            content = open(tempfile, encoding="utf-8").read()

        DownProblem.__compare_and_save(content, readme)

        # downloading mapi
        mapi = os.path.join(destiny, "mapi.json")
        urllib.request.urlretrieve(cache_url + "mapi.json", mapi)
        return readme, mapi

    @staticmethod
    def create_problem_folder(rootdir: str, activity: str) -> str:
        # create dir
        destiny: str = os.path.join(rootdir, activity)
        if not os.path.exists(destiny):
            os.makedirs(destiny, exist_ok=True)
        else:
            DownProblem.fnprint("  Pasta do problema "+ destiny + " encontrada, juntando conteúdo.")

        return destiny

    @staticmethod
    def download_drafts(loaded_json, destiny: str, language, cache_url, ask_ext):
        if len(loaded_json["required"]) == 1:  # you already have the students file
            return

        if "draft" in loaded_json and language in loaded_json["draft"]:
            pass
        else:
            try:
                draft_path = os.path.join(destiny, "draft." + language)
                urllib.request.urlretrieve(cache_url + "draft." + language, draft_path)
                DownProblem.fnprint("  " + draft_path + " (Rascunho) Renomeie antes de modificar")

            except urllib.error.HTTPError:  # draft not found
                filename = "draft."
                draft_path = os.path.join(destiny, filename + language)
                if not os.path.exists(draft_path):
                    with open(draft_path, "w", encoding="utf-8") as f:
                        if language in Drafts.drafts:
                            f.write(Drafts.drafts[language])
                        else:
                            f.write("")
                    DownProblem.fnprint("  " + draft_path + " (Vazio)")

        if ask_ext:
            print("\nVocê pode escolher a extensão padrão com o comando\n$ tko config -l <extension>")