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
import os
import shutil

class Actions:
    def __init__(self, source_dir: Path):
        self.hook = source_dir.name
        self.source_dir = source_dir
        self.source_readme = self.source_dir / "README.md"
        self.source_src = self.source_dir / "src"
        self.local_sh = self.source_dir / "local.sh"
        self.title = ""

        self.cache = source_dir / ".cache"
        self.output_readme = self.cache / "README.md"
        self.output_cases = self.cache / "tests.vpl"
        self.output_drafts = self.cache / "drafts"
        self.output_html = self.cache / "README.html"
        self.mapi_json = self.cache / "mapi.json"
        self.vpl: JsonVPL | None = None
        self.make_remote: bool = False
        self.use_pandoc: bool = False

    def set_use_remote(self, make_remote: bool):
        self.make_remote = make_remote
        return self

    def in_blacklist(self):
        if self.hook == "node_modules":
            return False
        if self.hook.startswith(".") or self.hook.startswith("_") or self.hook.startswith("+"):
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
        if not os.path.exists(self.mapi_json):
            return True
        older = Older.find_older([self.source_dir, self.mapi_json])
        if older == self.mapi_json:
            return False

        Log.resume("Changes ", end="")
        Log.verbose(f"Changes in {self.source_dir}")
        return True

    def remote_md(self):
        Absolute.convert_or_copy_or_print(self.source_readme, self.output_readme, self.make_remote)
        Log.verbose(f"RemoteFile: {self.output_readme}")

    def html(self):
        title = FenoTitle.extract_title(self.source_readme)
        convert_markdown_to_html(title, self.output_readme, self.output_html)
        Log.resume("HTML ", end="")
        Log.verbose(f"HTML  file: {self.output_html}")

    # uses tko to generate cases file
    def build_cases(self):
        Cases.run(self.output_cases, self.source_readme, self.source_dir)
        Log.resume("Cases ", end="")
        Log.verbose(f"Cases file: {self.output_cases}")

    def copy_drafts(self):
        source_src = self.source_src
        if os.path.isdir(source_src):
            Log.resume("Drafts ", end="")
            Log.verbose(f"Drafts dir: {source_src}")
            filter = DeepFilter().set_indent(4)
            filter.execute(source_src, self.output_drafts, 5)

    def run_local_sh(self):
        actual_chdir = os.getcwd()
        if os.path.isfile(self.local_sh):
            Log.verbose(f"Execute local.sh")
            os.chdir(self.source_dir)
            subprocess.run("bash local.sh", shell=True)
            os.chdir(actual_chdir)
            Log.resume("Local.sh ", end="")

    def init_vpl(self):
        html_content = Decoder.load(self.output_html)
        # md_content = Decoder.load(self.remote_readme)
        self.vpl = JsonVPL(self.title, html_content)
        self.vpl.set_tests(self.output_cases)
        if self.vpl.load_drafts(self.output_drafts):
            Log.resume("Drafts ", end="")

    def create_mapi(self):
        Decoder.save(self.mapi_json, str(self.vpl) + "\n")
        Log.resume("Mapi ", end="")
        Log.verbose(f"Mapi  file: {self.mapi_json}")

    def clean(self, erase: bool):
        if erase:
            Log.resume("Cleaning ", end="")
            Log.verbose("  Cleaning  : html and cases files")
            os.remove(self.output_cases)
            os.remove(self.output_html)
            os.remove(self.output_readme)

    # run mdpp script on source readme
    def update_markdown(self):
        if Mdpp.update_file(self.source_readme):
            Log.resume("Mdpp ", end="")
            Log.verbose(f"Mdpp updading")

def build_all(targets: list[Path], remote: bool, check: bool, erase: bool, brief: bool, moodle: bool):
    Log.set_verbose(not brief)

    if len(targets) == 0:
        targets = [Path(".")]
        print("No target specified, using current directory")

    for target in targets:
        if not os.path.isdir(target):
            print(f"\n    fail: {target} is not a directory")
            continue
        hook = target.name
        actions = Actions(target).set_use_remote(remote)

        if not actions.in_blacklist():
            continue

        Log.resume("- " + hook, end=": [ ")
        Log.verbose("- " + hook)

        actions.load_title()
        actions.create_cache()
        actions.update_markdown()

        if not check or actions.need_rebuild():
            actions.recreate_cache()  # erase .cache
            actions.copy_drafts()
            actions.run_local_sh()
            actions.update_markdown()  # se os drafts tiverem mudado o markdown precisa ser atualizado
            if moodle:
                actions.remote_md()
                actions.html()
                actions.build_cases()
                actions.init_vpl()
                actions.create_mapi()
            actions.clean(erase)

        Log.resume("]")