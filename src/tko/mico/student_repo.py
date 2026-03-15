from pathlib import Path

class StudentRepo:
    def __init__(self, folder: Path, rep: Path):
        self.__student_key: str = folder.name
        self.folder = folder
        self.tko_subfolder = rep

    def get_student_key(self) -> str:
        return self.__student_key

    def __str__(self):
        return f"{self.folder} {self.tko_subfolder}"

    def __repr__(self):
        return f"Target({self.folder}, {self.tko_subfolder})"
    
