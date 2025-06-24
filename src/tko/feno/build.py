from tko.feno.title import FenoTitle
from tko.feno.jsontools import JsonVPL
from tko.feno.older import Older
from tko.feno.remote_md import Absolute
from tko.feno.html import convert_markdown_to_html
from tko.feno.cases import Cases
from tko.feno.log import Log
from tko.feno.mdpp import Mdpp
from tko.feno.filter import DeepFilter
from tko.util.decoder import Decoder
from pathlib import Path
import subprocess
import argparse
import os
import shutil

def norm_join(*args: str) -> str:
    return str(Path(*args).resolve())


class Actions:
    def __init__(self, source_dir: str):
        self.cache = norm_join(source_dir, ".cache")
        self.target = norm_join(self.cache, "mapi.json")
        self.source_dir = source_dir
        self.hook = os.path.basename(os.path.abspath(source_dir))
        self.source_readme = norm_join(self.source_dir, "Readme.md")
        self.remote_readme = norm_join(self.cache, "Readme.md")
        self.target_html = norm_join(self.cache, "q.html")
        self.title = ""
        self.cases = norm_join(self.cache, "q.tio")
        self.mapi_json = norm_join(self.cache, "mapi.json")
        self.cache_src = norm_join(self.cache, "draft")
        self.vpl: JsonVPL | None = None
        self.make_remote: bool = False
        self.use_pandoc: bool = False

    def set_remote(self, make_remote: bool):
        self.make_remote = make_remote
        return self

    def validate(self):
        if self.hook == "node_modules" or self.hook.endswith(".json"):
            return False
        if not os.path.isdir(self.source_dir):
            print(f"\n    fail: {self.source_dir} is not a directory")
            return False
        if not os.path.isfile(self.source_readme):
            print(f"\n    fail: {self.source_readme} not found")
            return False
        return True

    def load_title(self):
        self.title = FenoTitle.extract_title(self.source_readme)

    def create_cache(self):
        if not os.path.exists(self.cache):
            os.makedirs(self.cache)
        return self

    def recreate_cache(self):
        shutil.rmtree(self.cache, ignore_errors=True)
        os.makedirs(self.cache)
        return self

    def need_rebuild(self):
        if not os.path.exists(self.target):
            return True
        older = Older.find_older([self.source_dir, self.target])
        if older == self.target:
            return False

        Log.resume("Changes ", end="")
        Log.verbose(f"  Changes in {self.source_dir}")
        return True

    def remote_md(self):
        Absolute.convert_or_copy_or_print(self.source_readme, self.remote_readme, self.make_remote)
        Log.verbose(f"  RemoteFile: {self.remote_readme}")

    def html(self):
        title = FenoTitle.extract_title(self.source_readme)
        convert_markdown_to_html(title, self.remote_readme, self.target_html)
        Log.resume("HTML ", end="")
        Log.verbose(f"  HTML  file: {self.target_html}")

    # uses tko to generate cases file
    def build_cases(self):
        Cases.run(self.cases, self.source_readme, self.source_dir)
        Log.resume("Cases ", end="")
        Log.verbose(f"  Cases file: {self.cases}")

    def copy_drafts(self):
        source_src = norm_join(self.source_dir, "src")
        if os.path.isdir(source_src):
            Log.resume("Drafts ", end="")
            Log.verbose(f"  Drafts dir: {source_src}")
            filter = DeepFilter().set_indent(4)
            filter.copy(source_src, self.cache_src, 5)

    def run_local_sh(self):
        local_sh = norm_join(self.source_dir, "local.sh")
        actual_chdir = os.getcwd()
        if os.path.isfile(local_sh):
            Log.verbose(f"  Execute local.sh")
            os.chdir(self.source_dir)
            subprocess.run("bash local.sh", shell=True)
            os.chdir(actual_chdir)
            Log.resume("Local.sh ", end="")

    def init_vpl(self):
        html_content = Decoder.load(self.target_html)
        # md_content = Decoder.load(self.remote_readme)
        self.vpl = JsonVPL(self.title, html_content)
        self.vpl.set_tests(self.cases)
        if self.vpl.load_drafts(self.cache_src):
            Log.resume("Drafts ", end="")

    def create_mapi(self):
        Decoder.save(self.mapi_json, str(self.vpl) + "\n")
        Log.resume("Mapi ", end="")
        Log.verbose(f"  Mapi  file: {self.mapi_json}")

    def clean(self, erase: bool):
        if erase:
            Log.resume("Cleaning ", end="")
            Log.verbose("  Cleaning  : html and cases files")
            os.remove(self.cases)
            os.remove(self.target_html)
            os.remove(self.remote_readme)

    # run mdpp script on source readme
    def update_markdown(self):
        if Mdpp.update_file(self.source_readme):
            Log.resume("Mdpp ", end="")
            Log.verbose(f"  Mdpp updading")


def build_main(args: argparse.Namespace):
    Log.set_verbose(not args.brief)

    if len(args.targets) == 0:
        print("fail: No targets specified")
        exit(1)

    for target in args.targets:
        hook = os.path.basename(os.path.abspath(target))

        actions = Actions(target) \
            .set_remote(args.remote)

        if not actions.validate():
            continue

        Log.resume("- " + hook, end=": [ ")
        Log.verbose("- " + hook)

        actions.load_title()
        actions.create_cache()
        actions.update_markdown()

        if not args.check or actions.need_rebuild():
            actions.recreate_cache()  # erase .cache
            actions.copy_drafts()
            actions.run_local_sh()
            actions.update_markdown()  # se os drafts tiverem mudado o markdown precisa ser atualizado
            actions.remote_md()
            actions.html()
            actions.build_cases()
            actions.init_vpl()
            actions.create_mapi()
            actions.clean(args.erase)

        Log.resume("]")