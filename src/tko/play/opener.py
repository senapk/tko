from tko.play.floating import Floating
from tko.play.floating_manager import FloatingManager
from tko.util.text import Text
from tko.settings.settings import Settings
from tko.down.drafts import Drafts

import tempfile
import os
import subprocess

class Opener:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.fman: None | FloatingManager = None
        self.folders: list[str] = []
        self.language: str = ""

    def set_fman(self, fman: FloatingManager):
        self.fman = fman
        return self
    
    def set_target(self, folders: list[str]):
        self.folders = folders
        return self

    def set_language(self, language: str):
        self.language = language
        return self

    def open_files(self, files_to_open: list[str]):
        files_raw = list(set(files_to_open))
        files_patched: list[str] = []
        for f in files_raw:
            if " " in f and not f.startswith('"'):
                files_patched.append(f'"{f}"')
            else:
                files_patched.append(f)

        cmd = self.settings.app.get_editor()
        folder = os.path.dirname(os.path.abspath(files_to_open[0]))
        aviso = (Floating(self.settings, "v>")
                .warning()
                .put_sentence(Text().add("Pasta: ").addf("g", folder).add(" "))
                .put_text("Abrindo arquivos com o comando")
                )
        files = [os.path.basename(path) for path in files_to_open]
        aviso.put_sentence(Text().addf("g", f"{cmd}").add(" ").addf("g", " ".join(files)).add(" "))
        self.send_floating(aviso)
        fullcmd = "{} {}".format(cmd, " ".join(files_patched))
        outfile = tempfile.NamedTemporaryFile(delete=False)
        subprocess.Popen(fullcmd, stdout=outfile, stderr=outfile, shell=True)

    def send_floating(self, floating: Floating):
        if self.fman is not None:
            self.fman.add_input(floating)

    @staticmethod
    def try_add(files_to_open: list[str], folder: str, file: str):
        path = os.path.join(folder, file)
        if os.path.isfile(path):
            files_to_open.append(path)

    def load_folder(self, folder: str):
        files_to_open: list[str] = []
        # Opener.try_add(files_to_open, folder, "Readme.md")
        # Opener.try_add(files_to_open, folder, "cases.tio")
        files_to_open += Drafts.load_drafts_only(folder, self.language, ["md"])
        return files_to_open

    def load_folders_and_open(self):
        files_to_open: list[str] = []
        for folder in self.folders:
            files_to_open += self.load_folder(folder)
        if len(files_to_open) != 0:
            self.open_files(files_to_open)

    def __call__(self):
        self.load_folders_and_open()