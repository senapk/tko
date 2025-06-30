import os
import subprocess

class StudentRepo:
    def __init__(self, folder: str, rep: str):
        self.__student_key: str = os.path.basename(folder)
        self.folder = folder
        self.tko_subfolder = rep

    def get_student_key(self) -> str:
        return self.__student_key

    def __str__(self):
        return f"{self.folder} {self.tko_subfolder}"

    def __repr__(self):
        return f"Target({self.folder}, {self.tko_subfolder})"
    
    def run_tko_collect(self) -> str:
        """
        Run the tko collect command in the student's repository.
        """
        folder = self.folder
        rep = self.tko_subfolder
        print("Loading info from " + folder)
        rep_folder = os.path.join(folder, rep)
        if not os.path.isdir(rep_folder):
            return ""
        result = subprocess.run(["tko", "rep", rep_folder, "collect", "--daily", "--resume", "--game", "--json"], capture_output=True, text=True)
        return result.stdout
