from typing import Tuple, Optional, List, Callable
import os
import urllib.request
import urllib.error
import json

from .settings.app_settings import AppSettings
from .settings.settings import Settings
from .game.game import Game
from .util.remote import RemoteCfg

class Down:
    fnprint: Callable[[str], None] = print

    ts_draft = r"""
let _cin_ : string[] = [];
try { _cin_ = require("fs").readFileSync(0).toString().split(/\r?\n/); } catch(e){}
let input = () : string => _cin_.length === 0 ? "" : _cin_.shift()!;
let write = (text: any, end:string="\n")=> process.stdout.write("" + text + end);
export {};

write("qxcode");
"""[1:]

    js_draft = r"""
let __lines = require("fs").readFileSync(0).toString().split("\n");
let input = () => __lines.length === 0 ? "" : __lines.shift();
let write = (text, end="\n") => process.stdout.write("" + text + end);

write("qxcode");
"""[1:]

    c_draft = r"""
#include <stdio.h>

int main() {
    puts("qxcode");
    return 0;
}

"""[1:]
    
    cpp_draft = r"""
#include <iostream>

int main() {
    std::cout << "qxcode\n";
}

"""[1:]
    
    java_draft = r"""
public class draft {
    public static void main(String args[]) {
        System.out.println("qxcode");
    }
}

"""[1:]

    go_draft = (
        r"package main""\n"
        r'import "fmt"'"\n"
        r"func main() {""\n"
        r'    fmt.Println("qxcode")''\n'
        r"}""\n"
    )


    drafts = {'c': c_draft, 'cpp': cpp_draft, 'ts': ts_draft, 'js': js_draft, 'java': java_draft, 'go': go_draft}
    # def __init__(self):
    #     self.drafts = {}
    #     self.drafts['c'] = Down.c_draft
    #     self.drafts['cpp'] = Down.cpp_draft
    #     self.drafts['ts'] = Down.ts_draft
    #     self.drafts['js'] = Down.js_draft

    # @staticmethod
    # def update():
    #     if os.path.isfile(".info"):
    #         data = open(".info", "r").read().split("\n")[0]
    #         data = data.split(" ")
    #         discp = data[0]
    #         label = data[1]
    #         ext = data[2]
    #         Down.entry_unpack(".", discp, label, ext)
    #     else:
    #         print("No .info file found, skipping update...")

    @staticmethod
    def __create_file(content, path, label=""):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        Down.fnprint("  " + path + " " + label)

    @staticmethod
    def __unpack_json(loaded, destiny, lang: str):
        # extracting all files to folder
        for entry in loaded["upload"]:
            if entry["name"] == "vpl_evaluate.cases":
                Down.__compare_and_save(entry["contents"], os.path.join(destiny, "cases.tio"))

        # for entry in loaded["keep"]:
        #    Down.compare_and_save(entry["contents"], os.path.join(destiny, entry["name"]))

        # for entry in loaded["required"]:
        #    path = os.path.join(destiny, entry["name"])
        #    Down.compare_and_save(entry["contents"], path)

        if "draft" in loaded:
            if lang in loaded["draft"]:
                for file in loaded["draft"][lang]:
                    path = os.path.join(destiny, file["name"])
                    Down.__create_file(file["contents"], path, "(Draft)")

    @staticmethod
    def __compare_and_save(content, path):
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content.encode("utf-8").decode("utf-8"))
            Down.fnprint("  " + path + " (Novo)")
        else:
            if open(path, encoding="utf-8").read() != content:
                Down.fnprint(path + " (Atualizado)")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
            else:
                Down.fnprint("  " + path + " (Inalterado)")

    @staticmethod
    def __down_problem_def(destiny, cache_url) -> Tuple[str, str]:
        # downloading Readme
        readme = os.path.join(destiny, "Readme.md")
        [tempfile, __content] = urllib.request.urlretrieve(cache_url + "Readme.md")

        # content = ""
        try:
            content = open(tempfile, encoding="utf-8").read()
        except FileNotFoundError:
            content = open(tempfile, encoding="utf-8").read()

        Down.__compare_and_save(content, readme)

        # downloading mapi
        mapi = os.path.join(destiny, "mapi.json")
        urllib.request.urlretrieve(cache_url + "mapi.json", mapi)
        return readme, mapi

    @staticmethod
    def __create_problem_folder(rootdir: str, activity: str) -> str:
        # create dir
        destiny: str = os.path.join(rootdir, activity)
        if not os.path.exists(destiny):
            os.makedirs(destiny, exist_ok=True)
        else:
            Down.fnprint("  Pasta do problema "+ destiny + " encontrada, juntando conteúdo.")

        return destiny

    @staticmethod
    def download_problem(course: str, activity: str, language: Optional[str], fnprint: Callable[[str], None], game: Optional[Game] = None) -> bool:
        Down.fnprint = fnprint
        
        settings = Settings()
        rep_dir = os.path.join(settings.app.get_rootdir(), course)
        rep_source = settings.get_rep_source(course)
        rep_data = settings.get_rep_data(course)
        if game is None:
            try:
                file = rep_source.get_file(rep_dir)
            except urllib.error.HTTPError:
                Down.fnprint("falha: Verifique sua internet")
            game = Game(file)
        item = game.get_task(activity)
        if not item.link.startswith("http"):
            Down.fnprint("falha: link para atividade não é um link remoto")
            return False
        cfg = RemoteCfg(item.link)
        cache_url = os.path.dirname(cfg.get_raw_url()) + "/.cache/"

        destiny = Down.__create_problem_folder(rep_dir, activity)
        destiny = os.path.abspath(destiny)
        try:
            [_readme_path, mapi_path] = Down.__down_problem_def(destiny, cache_url)
        except urllib.error.HTTPError:
            Down.fnprint("  falha: atividade não encontrada no curso")
            # verifi if destiny folder is empty and remove it
            if len(os.listdir(destiny)) == 0:
                os.rmdir(destiny)
            return False
        except urllib.error.URLError:
            Down.fnprint("  falha: não consegui baixar a atividade, verifique sua internet")
            return False


        with open(mapi_path, encoding="utf-8") as f:
            loaded_json = json.load(f)
        os.remove(mapi_path)

        language_def = rep_data.get_lang()
        if language_def == "":
            language_def = Settings().app.get_lang_def()
        ask_ext = False
        if language is None:
            if language_def != "":
                language = language_def
            else:
                print("  Escolha uma extensão para os rascunhos: [c, cpp, py, ts, js, java]: ", end="")
                language = input()
                ask_ext = True

        Down.__unpack_json(loaded_json, destiny, language)
        Down.__download_drafts(loaded_json, destiny, language, cache_url, ask_ext)
        return True

    @staticmethod
    def __download_drafts(loaded_json, destiny: str, language, cache_url, ask_ext):
        if len(loaded_json["required"]) == 1:  # you already have the students file
            return

        if "draft" in loaded_json and language in loaded_json["draft"]:
            pass
        else:
            try:
                draft_path = os.path.join(destiny, "draft." + language)
                urllib.request.urlretrieve(cache_url + "draft." + language, draft_path)
                Down.fnprint("  " + draft_path + " (Rascunho) Renomeie antes de modificar")

            except urllib.error.HTTPError:  # draft not found
                filename = "draft."
                draft_path = os.path.join(destiny, filename + language)
                if not os.path.exists(draft_path):
                    with open(draft_path, "w", encoding="utf-8") as f:
                        if language in Down.drafts:
                            f.write(Down.drafts[language])
                        else:
                            f.write("")
                    Down.fnprint("  " + draft_path + " (Vazio)")

        if ask_ext:
            print("\nVocê pode escolher a extensão padrão com o comando\n$ tko config -l <extension>")
