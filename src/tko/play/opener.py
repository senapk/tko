from pathlib import Path
import subprocess
import tempfile

from tko.cmds.drafts_finder_cached import DraftsFinderCached
from tko.config.settings import Settings


class Opener:
    """Open source files in the configured editor without UI-side effects."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.files_to_open: list[Path] = []
        self.language = ""

    def add_files_to_open(self, files: list[Path]):
        self.files_to_open.extend(files)
        return self

    def add_task_folder_to_open(self, folder: Path):
        finder = DraftsFinderCached(folder, self.language)
        self.files_to_open.extend(finder.load_source_files([".md"]) + [folder / "README.md"])
        return self

    def set_language(self, language: str):
        self.language = language
        return self

    def open_files(self) -> None:
        files = list(dict.fromkeys(self.files_to_open))
        if not files:
            return
        command = "{} {}".format(self.settings.app.editor, " ".join(f'"{path}"' for path in files))
        output = tempfile.NamedTemporaryFile(delete=False)
        subprocess.Popen(command, stdout=output, stderr=output, shell=True)

    def __call__(self) -> None:
        self.open_files()
