from tko.play.floating import Floating
from tko.play.floating_manager import FloatingManager
from tko.util.text import Text
from tko.settings.settings import Settings
from tko.cmds.drafts_finder_cached import DraftsFinderCached
from pathlib import Path

import tempfile
import subprocess

class Opener:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.fman: None | FloatingManager = None
        self.files_to_open: list[Path] = []
        self.language: str = ""

    def set_fman(self, fman: FloatingManager):
        self.fman = fman
        return self
    
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

    def open_files(self):
        files_to_open = (list(set(self.files_to_open)))

        cmd = self.settings.app.editor
        folder: Path = files_to_open[0].parent.resolve()
        aviso = (Floating()
                .bottom()
                .right()
                .set_warning()
                .put_sentence(Text().add("Pasta: ").addf("g", folder).add(" "))
                .put_text("Abrindo arquivos com o comando")
                )
        files = [path.name for path in files_to_open]
        aviso.put_sentence(Text().addf("g", f"{cmd}").add(" ").addf("g", " ".join(files)).add(" "))
        self.send_floating(aviso)
        fullcmd = "{} {}".format(cmd, " ".join([f'"{f}"' for f in files_to_open]))
        outfile = tempfile.NamedTemporaryFile(delete=False)
        subprocess.Popen(fullcmd, stdout=outfile, stderr=outfile, shell=True)

    def send_floating(self, floating: Floating):
        if self.fman is not None:
            self.fman.add_input(floating)


    def __call__(self):
        self.open_files()