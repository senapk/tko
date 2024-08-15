from .tasktree import TaskTree, Task
from .floating import Floating
from .floating_manager import FloatingManager
from ..settings.geral_settings import GeralSettings
from ..settings.rep_settings import RepData
from ..util.runner import Runner
from ..util.sentence import Sentence
import tempfile
import os
import subprocess
from typing import List

class Opener:
    def __init__(self, tree: TaskTree, fman: FloatingManager, geral: GeralSettings, rep_data: RepData, rep_alias: str):
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

    def open_code(self, open_drafts: bool=False, open_readme: bool=False, open_dir: bool = False, open_cases: bool = False):
        obj = self.tree.get_selected()
        if isinstance(obj, Task):
            path = self.get_task_readme_path()
            cmd = self.geral.get_editor()
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
                # code, out, err = Runner.subprocess_run(f"{cmd} -h")
                # if ("Replit" in out) or ("replit" in err):
                open_cases = True
                open_readme = True
                open_drafts = True
                # else:
                #     outfile = tempfile.NamedTemporaryFile(delete=False)
                #     self.fman.add_input(
                #         Floating("v>")
                #             .warning()
                #             .put_text("Abrindo arquivos do problema com o comando")
                #             .put_sentence(Sentence().addf("g", f"  {cmd}"))
                #     )
                #     subprocess.Popen(f"{cmd} {os.path.dirname(path)}", stdout=outfile, shell=True)
                #     #code, out, err = Runner.subprocess_run(f"{cmd} {os.path.dirname(path)}")
                
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
                    if not f.endswith(self.rep.get_lang()):
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
                # print(" ".join(files_to_open))
                # Runner.subprocess_run("{} {}".format(cmd, " ".join(files_to_open)))
                cmd = "{} {}".format(cmd, " ".join(files_to_open))
                self.fman.add_input(
                    Floating("v>")
                        .warning()
                        .put_text("Abrindo arquivos do problema com o comando")
                        .put_sentence(Sentence().addf("g", f"  {cmd}"))
                )
                outfile = tempfile.NamedTemporaryFile(delete=False)
                subprocess.Popen(cmd, stdout=outfile, stderr=outfile, shell=True)