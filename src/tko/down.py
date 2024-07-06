from typing import Tuple, Optional, List
import os
import urllib.request
import urllib.error
import json

from .settings.settings_parser import SettingsParser
from .game.game import Game
from .util.remote import RemoteCfg

class Down:
    fnprint = print

    ts_draft = (r'let _cin_ : string[] = [];' + '\n'
                r'try { _cin_ = require("fs").readFileSync(0).toString().split(/\r?\n/); } catch(e){}' + '\n'
                r'let input = () : string => _cin_.length === 0 ? "" : _cin_.shift()!;' + '\n'
                r'let write = (text: any, end:string="\n")=> process.stdout.write("" + text + end);' + '\n')

    js_draft = (r'let __lines = require("fs").readFileSync(0).toString().split("\n");' + '\n'
                r'let input = () => __lines.length === 0 ? "" : __lines.shift();' + '\n'
                r'let write = (text, end="\n") => process.stdout.write("" + text + end);') + '\n'

    c_draft = '#include <stdio.h>\n\nint main() {\n    return 0;\n}\n\n'
    cpp_draft = '#include <iostream>\n\nint main() {\n}\n\n'

    drafts = {'c': c_draft, 'cpp': cpp_draft, 'ts': ts_draft, 'js': js_draft}
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
        with open(path, "w") as f:
            f.write(content)
        Down.fnprint("  " + path, label)

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
            Down.fnprint("  " + path + " (New)")
        else:
            if open(path).read() != content:
                Down.fnprint(path + " (Updated)")
                with open(path, "w") as f:
                    f.write(content)
            else:
                Down.fnprint("  " + path + " (Unchanged)")

    @staticmethod
    def __down_problem_def(destiny, cache_url) -> Tuple[str, str]:
        # downloading Readme
        readme = os.path.join(destiny, "Readme.md")
        [tempfile, __content] = urllib.request.urlretrieve(cache_url + "Readme.md")

        # content = ""
        try:
            content = open(tempfile, encoding="utf-8").read()
        except FileNotFoundError:
            content = open(tempfile).read()

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
            Down.fnprint("  Problem folder "+ destiny + " found, merging content.")

        return destiny

    @staticmethod
    def download_problem(rootdir, course: str, activity: str, language: Optional[str], fnprint) -> bool:
        Down.fnprint = fnprint
        sp = SettingsParser()
        settings = sp.load_settings()
        rep = settings.get_repo(course)

        file = rep.get_file()
        game = Game(file)
        item = game.get_task(activity)
        if not item.link.startswith("http"):
            Down.fnprint("fail: link for activity is not a remote link")
            return False
        cfg = RemoteCfg(item.link)
        cache_url = os.path.dirname(cfg.get_raw_url()) + "/.cache/"

        destiny = Down.__create_problem_folder(rootdir, activity)
        destiny = os.path.abspath(destiny)
        try:
            [_readme_path, mapi_path] = Down.__down_problem_def(destiny, cache_url)
        except urllib.error.HTTPError:
            Down.fnprint("  fail: activity not found in course url")
            # verifi if destiny folder is empty and remove it
            if len(os.listdir(destiny)) == 0:
                os.rmdir(destiny)
            return False

        with open(mapi_path) as f:
            loaded_json = json.load(f)
        os.remove(mapi_path)

        language_def = SettingsParser().get_language()
        ask_ext = False
        if language is None:
            if language_def != "":
                language = language_def
            else:
                print("  Choose extension for draft: [c, cpp, py, ts, js, java]: ", end="")
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
                Down.fnprint("  " + draft_path + " (Draft) Rename before modify.")

            except urllib.error.HTTPError:  # draft not found
                filename = "draft."
                draft_path = os.path.join(destiny, filename + language)
                if not os.path.exists(draft_path):
                    with open(draft_path, "w") as f:
                        if language in Down.drafts:
                            f.write(Down.drafts[language])
                        else:
                            f.write("")
                    Down.fnprint("  " + draft_path + " (Empty)")

        if ask_ext:
            print("\nYou can choose default extension with command\n$ tko config -l <extension>")
