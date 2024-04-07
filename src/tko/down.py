from typing import Tuple, Optional
import os
import urllib.request
import urllib.error
import json

from .settings import SettingsParser

class Down:

    ts_draft = (r'let _cin_ : string[] = [];' + '\n'
                r'try { _cin_ = require("fs").readFileSync(0).toString().split(/\r?\n/); } catch(e){}' + '\n'
                r'let input = () : string => _cin_.length === 0 ? "" : _cin_.shift()!;' + '\n'
                r'let write = (text: any, end:string="\n")=> process.stdout.write("" + text + end);' + '\n')

    js_draft = (r'let __lines = require("fs").readFileSync(0).toString().split("\n");'  + '\n'
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
    def create_file(content, path, label=""):
        with open(path, "w") as f:
            f.write(content)
        print(path, label)

    @staticmethod
    def unpack_json(loaded, destiny, lang: str):
        # extracting all files to folder
        for entry in loaded["upload"]:
            if entry["name"] == "vpl_evaluate.cases":
                Down.compare_and_save(entry["contents"], os.path.join(destiny, "cases.tio"))

        # for entry in loaded["keep"]:
        #    Down.compare_and_save(entry["contents"], os.path.join(destiny, entry["name"]))

        # for entry in loaded["required"]:
        #    path = os.path.join(destiny, entry["name"])
        #    Down.compare_and_save(entry["contents"], path)

        if "draft" in loaded:
            if lang in loaded["draft"]:
                for file in loaded["draft"][lang]:
                    path = os.path.join(destiny, file["name"])
                    Down.create_file(file["contents"], path, "(Draft)")

    @staticmethod
    def compare_and_save(content, path):
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content.encode("utf-8").decode("utf-8"))
            print(path + " (New)")
        else:
            if open(path).read() != content:
                print(path + " (Updated)")
                with open(path, "w") as f:
                    f.write(content)
            else:
                print(path + " (Unchanged)")
    
    @staticmethod
    def down_problem_def(destiny, cache_url) -> Tuple[str, str]:
        # downloading Readme
        readme = os.path.join(destiny, "Readme.md")
        [tempfile, __content] = urllib.request.urlretrieve(cache_url + "Readme.md")
        content = ""
        try:
            content = open(tempfile, encoding="utf-8").read()
        except:
            content = open(tempfile).read()

        Down.compare_and_save(content, readme)
        
        # downloading mapi
        mapi = os.path.join(destiny, "mapi.json")
        urllib.request.urlretrieve(cache_url + "mapi.json", mapi)
        return readme, mapi

    @staticmethod
    def create_problem_folder(_course, activity):
        # create dir
        destiny = activity
        if not os.path.exists(destiny):
            os.makedirs(destiny, exist_ok=True)
        else:
            print("problem folder", destiny, "found, merging content.")

        return destiny

    @staticmethod
    def entry_unpack(course: str, activity: str, language: Optional[str]) -> None:
        course_url = SettingsParser().get_repository(course)
        if course_url is None:
            print("fail: course", course, "not found")
            return
        
        index_url = course_url + activity + "/"
        cache_url = index_url + ".cache/"
        

        # downloading Readme
        try:
            destiny = Down.create_problem_folder(course, activity)
            print(cache_url)
            [_readme_path, mapi_path] = Down.down_problem_def(destiny, cache_url)
        except urllib.error.HTTPError:
            print("fail: activity not found in course")
            # verifi if destiny folder is empty and remove it
            if len(os.listdir(destiny)) == 0:
                os.rmdir(destiny)

            return

        with open(mapi_path) as f:
            loaded_json = json.load(f)
        os.remove(mapi_path)

        language_def = SettingsParser().get_language()
        ask_ext = False
        if language is None:
            if language_def != "ask":
                language = language_def
            else:
                print("Choose extension for draft: [c, cpp, py, ts, js, java]: ", end="")
                language = input()
                ask_ext = True
        
        Down.unpack_json(loaded_json, destiny, language)

        if len(loaded_json["required"]) == 1:  # you already have the students file
            return

        if "draft" in loaded_json and language in loaded_json["draft"]:
            pass
        else:
            try:
                draft_path = os.path.join(destiny, "draft." + language)
                urllib.request.urlretrieve(cache_url + "draft." + language, draft_path)
                print(draft_path + " (Draft) Rename before modify.")

            except urllib.error.HTTPError:  # draft not found
                filename = "draft."
                draft_path = os.path.join(destiny, filename + language)
                if not os.path.exists(draft_path):
                    with open(draft_path, "w") as f:
                        if language in Down.drafts:
                            f.write(Down.drafts[language])
                        else:
                            f.write("")
                    print(draft_path, "(Empty)")
        
        if ask_ext:
            print("\nYou can choose default extension with command\n$ tko config -l <extension>")

        # download all files in folder with the same extension or compatible
        # try:
        #     filelist = os.path.join(index, "filelist.txt")
        #     urllib.request.urlretrieve(cache_url + "filelist.txt", filelist)
        #     files = open(filelist, "r").read().splitlines()
        #     os.remove(filelist)

        #     for file in files:
        #         filename = os.path.basename(file)
        #         fext = filename.split(".")[-1]
        #         if fext == ext or ((fext == "h" or fext == "hpp") and ext == "cpp") or ((fext == "h" and ext == "c")):
        #             filepath = os.path.join(index, filename)
        #             # urllib.request.urlretrieve(index_url + file, filepath)
        #             [tempfile, _content] = urllib.request.urlretrieve(index_url + file)
        #             Down.compare_and_save(open(tempfile).read(), filepath)
        # except urllib.error.HTTPError:
        #     return
