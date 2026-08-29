from tko.feno.title import FenoTitle
from tko.feno.older import Older
from tko.feno.html import convert_markdown_to_html
from tko.feno.cases import Cases
from tko.feno.git_hub_cfg import GithubCfg
from tko.feno.link_rebase import LinkRebase
from tko.feno.log import Log
from tko.feno.mdpp import Mdpp
from tko.feno.filter import DeepFilter
from tko.i18n import Msg
from tko.util.decoder import Decoder
from pathlib import Path
from tko.util.console import Console
import subprocess
import os
import shutil


_FENO_BUILD_NO_TARGET_SPECIFIED = Msg.parse(
    pt="Nenhum target especificado, usando diretório atual",
    en="No target specified, using current directory",
)
_FENO_BUILD_TARGET_NOT_DIRECTORY = Msg.parse(
    pt="fail: {target} não é um diretório",
    en="fail: {target} is not a directory",
)

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
        self.output_starter = self.cache / "starter"
        self.output_html = self.cache / "README.html"
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

    def _latest_source_file(self) -> Path:
        files = [
            path
            for path in self.source_dir.rglob("*")
            if path.is_file() and self.cache not in path.parents
        ]
        if not files:
            return self.source_dir
        return max(files, key=lambda path: path.stat().st_mtime)

    def need_rebuild(self, moodle: bool = False):
        artifact = self.output_cases if moodle else self.output_starter
        if not os.path.exists(artifact):
            return True
        older = Older.find_older([self._latest_source_file(), artifact])
        if older == artifact:
            return False

        Log.resume("Changes ", end="")
        Log.verbose(f"Changes in {self.source_dir}")
        return True

    def remote_md(self):
        content = Decoder.load(self.source_readme)
        if self.make_remote:
            cfg = GithubCfg(self.source_dir, self.make_remote)
            if cfg.remote is not None:
                try:
                    relative_readme = self.source_readme.resolve().relative_to(cfg.get_cfg_path().parent)
                    remote = cfg.remote.set_relative_path(relative_readme.as_posix())
                    content = LinkRebase.rebase(content, remote)
                except ValueError:
                    pass
        else:
            relative_folder = Path(os.path.relpath(self.source_readme.parent, self.output_readme.parent))
            content = LinkRebase.change_to_relative_folder(content, relative_folder)

        Decoder.save(self.output_readme, content)
        Log.resume("Readme ", end="")
        Log.verbose(f"Readme file: {self.output_readme}")

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
            filter.execute(source_src, self.output_starter, 5)

    def run_local_sh(self):
        actual_chdir = os.getcwd()
        if os.path.isfile(self.local_sh):
            Log.verbose(f"Execute local.sh")
            os.chdir(self.source_dir)
            subprocess.run("bash local.sh", shell=True)
            os.chdir(actual_chdir)
            Log.resume("Local.sh ", end="")

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
        Console.print(_FENO_BUILD_NO_TARGET_SPECIFIED)

    for target in targets:
        if not os.path.isdir(target):
            Console.print(f"\n    {_FENO_BUILD_TARGET_NOT_DIRECTORY}".format(target=target))
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

        if not check or actions.need_rebuild(moodle):
            actions.recreate_cache()  # erase .cache
            actions.copy_drafts()
            actions.run_local_sh()
            actions.update_markdown()  # se os drafts tiverem mudado o markdown precisa ser atualizado
            if moodle:
                actions.remote_md()
                actions.html()
                actions.build_cases()
            actions.clean(erase)

        Log.resume("]")
