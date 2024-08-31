from .tasktree import TaskTree, Task
from .floating import Floating
from .floating_manager import FloatingManager
from ..settings.app_settings import AppSettings
from ..settings.rep_settings import RepData
from ..util.runner import Runner
from ..util.sentence import Sentence
import tempfile
import os
import subprocess
from typing import List

class Opener:
    def __init__(self, tree: TaskTree, fman: FloatingManager, geral: AppSettings, rep_data: RepData, rep_alias: str):
        self.tree = tree
        self.fman = fman
        self.geral = geral
        self.rep = rep_data
        self.rep_alias = rep_alias

    def set_fman(self, fman: FloatingManager):
        self.fman = fman
        return self

    def get_task_readme_path(self) -> str:
        obj = self.tree.get_selected()
        if isinstance(obj, Task):
            rootdir = self.geral.get_rootdir()
            if rootdir != "":
                path = os.path.join(self.geral.get_rootdir(), self.rep_alias, obj.key, "Readme.md")
                if os.path.isfile(path):
                    return path
        return ""

    def open_files(self, files_to_open: List[str]):
        cmd = self.geral.get_editor()
        folder = os.path.dirname(os.path.abspath(files_to_open[0]));
        aviso = (Floating("v>")
                .warning()
                .put_sentence(Sentence().add("Pasta: ").addf("g", folder).add(" "))
                .put_text("Abrindo arquivos com o comando")
                )
        files = [os.path.basename(path) for path in files_to_open]
        aviso.put_sentence(Sentence().addf("g", f"{cmd}").add(" ").addf("g", " ".join(files)).add(" "))
        self.fman.add_input(aviso)
        fullcmd = "{} {}".format(cmd, " ".join(files_to_open))
        outfile = tempfile.NamedTemporaryFile(delete=False)
        subprocess.Popen(fullcmd, stdout=outfile, stderr=outfile, shell=True)

    def open_code(self, open_drafts: bool=False, open_readme: bool=False, open_dir: bool = False, open_cases: bool = False):
        obj = self.tree.get_selected()
        if isinstance(obj, Task):
            path = self.get_task_readme_path()
            # code, _, _ = Runner().subprocess_run("whereis {}".format(cmd))
            if not os.path.isfile(path):
                if open_readme:
                    self.fman.add_input(
                        Floating("v>").error().put_text("Não achei nada baixado para você ler.")
                    )
                if open_drafts:
                    self.fman.add_input(
                        Floating("v>").error().put_text("Não achei nada baixado para você editar.")
                    )
                if open_dir:
                    self.fman.add_input(
                        Floating("v>").error().put_text("Não achei nada baixado para você abrir.")
                    )
                return
            if open_dir:
                open_cases = True
                open_readme = True
                open_drafts = True
                
            files_to_open: List[str] = []
            if open_readme:
                files_to_open.append(path)
                # Runner.subprocess_run(f"{cmd} {path}")
            if open_cases:
                cases = os.path.join(os.path.dirname(path), "cases.tio")
                if os.path.isfile(cases):
                    files_to_open.append(cases)
                    # Runner.subprocess_run(f"{cmd} {cases}")
            folder = os.path.dirname(path)
            files = os.listdir(folder)
            if open_drafts:
                drafts = []
                for f in files:
                    allowed = [self.rep.get_lang()]
                    if self.rep.get_lang() == "c" or self.rep.get_lang() == "cpp":
                        allowed.append("h")
                        allowed.append("hpp")
                    if not f.endswith(tuple(allowed)):
                        continue
                    drafts.append(os.path.join(folder, f))
                if len(drafts) == 0:
                    self.fman.add_input(
                        Floating("v>").error().put_text("Não achei nenhum arquivo de rascunho.")
                    )
                    return
                for f in drafts:
                    files_to_open.append(f)
            if len(files_to_open) != 0:
                self.open_files(files_to_open)