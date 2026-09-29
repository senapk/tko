from tko.feno.title import FenoTitle
from tko.feno.older import Older
from tko.feno.html import convert_markdown_to_html
from tko.feno.cases import Cases
from tko.feno.embed_local_assets import LocalAssetError, embed_local_assets, validate_local_assets
from tko.feno.log import Log
from tko.feno.mdpp import Mdpp
from tko.feno.filter import DeepFilter
from tko.i18n import Msg
from tko.util.decoder import Decoder
from pathlib import Path
from tko.config.settings import Settings
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
    def __init__(self, source_dir: Path, settings: Settings | None = None) -> None:
        self.hook = source_dir.name
        self.source_dir = source_dir
        self.settings = settings if settings is not None else Settings(None)
        self.source_readme = self.source_dir / "README.md"
        self.source_src = self.source_dir / "src"
        self.local_sh = self.source_dir / "local.sh"
        self.title = ""

        self.cache = source_dir / ".cache"
        self.output_readme = self.cache / "README.md"
        self.output_cases = self.cache / "tests.vpl"
        self.output_starter = self.cache / "starter"
        self.output_html = self.cache / "README.html"
        self.use_pandoc: bool = False

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

    def _moodle_artifacts(self) -> list[Path]:
        artifacts: list[Path] = [
            self.output_readme,
            self.output_html,
            self.output_cases,
        ]
        if self.source_src.is_dir():
            artifacts.append(self.output_starter)
        return artifacts

    def need_rebuild(self, moodle: bool = False) -> bool:
        if moodle:
            validate_local_assets(Decoder.load(self.source_readme), self.source_dir)

        artifacts: list[Path]
        if moodle:
            artifacts = self._moodle_artifacts()
        else:
            artifacts = [self.output_starter]

        if any(not artifact.exists() for artifact in artifacts):
            return True

        latest_source: Path = self._latest_source_file()
        source_mtime: float = Older.last_update(latest_source)[1]
        if all(Older.last_update(artifact)[1] >= source_mtime for artifact in artifacts):
            return False

        Log.resume("Changes ", end="")
        Log.verbose(f"Changes in {self.source_dir}")
        return True

    def embed_markdown_assets(self) -> None:
        content: str = embed_local_assets(Decoder.load(self.source_readme), self.source_dir)
        Decoder.save(self.output_readme, content)
        Log.resume("Readme ", end="")
        Log.verbose(f"Readme file: {self.output_readme}")

    def html(self) -> None:
        title: str = FenoTitle.extract_title(self.source_readme)
        convert_markdown_to_html(title, self.output_readme, self.output_html)
        Log.resume("HTML ", end="")
        Log.verbose(f"HTML  file: {self.output_html}")

    # uses tko to generate cases file
    def build_cases(self) -> bool:
        succeeded: bool = Cases.run(self.output_cases, self.source_readme, self.source_dir, self.settings)
        Log.resume("Cases ", end="")
        Log.verbose(f"Cases file: {self.output_cases}")
        return succeeded

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

def build_task(
    targets: list[Path], moodle: bool, check: bool, erase: bool, brief: bool, settings: Settings | None = None
) -> bool:
    Log.set_verbose(not brief)
    succeeded: bool = True

    if len(targets) == 0:
        targets = [Path(".")]
        Console.print(_FENO_BUILD_NO_TARGET_SPECIFIED)

    for target in targets:
        if not os.path.isdir(target):
            Console.print(f"\n    {_FENO_BUILD_TARGET_NOT_DIRECTORY}".format(target=target))
            succeeded = False
            continue
        hook = target.name
        actions: Actions = Actions(target, settings if settings is not None else Settings(None))

        if not actions.in_blacklist():
            continue

        Log.resume("- " + hook, end=": [ ")
        Log.verbose("- " + hook)

        actions.load_title()
        actions.create_cache()
        try:
            rebuild: bool = not check or actions.need_rebuild(moodle)
            if rebuild:
                actions.recreate_cache()  # erase .cache
                actions.copy_drafts()
                actions.run_local_sh()
                actions.update_markdown()  # se os drafts tiverem mudado o markdown precisa ser atualizado
                if moodle:
                    actions.embed_markdown_assets()
                    actions.html()
                    if not actions.build_cases():
                        succeeded = False
                actions.clean(erase)
        except LocalAssetError as error:
            actions.output_readme.unlink(missing_ok=True)
            actions.output_html.unlink(missing_ok=True)
            actions.output_cases.unlink(missing_ok=True)
            Console.print(f"\n    fail: {target}: {error}")
            succeeded = False
        finally:
            Log.resume("]")

    return succeeded
