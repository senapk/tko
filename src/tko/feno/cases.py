import subprocess
import os
import glob


class Cases:

    @staticmethod
    def run(cases_file: str, source_readme: str, source_dir: str):
        # find all files in the directory terminatig with .tio or .vpl
        files = list(glob.iglob(source_dir + '/**', recursive=True))
        files = [f for f in files if os.path.isfile(f)]
        files = [f for f in files if f.endswith(".tio") or f.endswith(".vpl")]
        cmd = " ".join(["tko", "build", cases_file, source_readme] + files)
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
