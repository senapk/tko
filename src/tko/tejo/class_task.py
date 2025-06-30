from __future__ import annotations
from tko.tejo.student_repo import StudentRepo
import json
import os

class ClassTask:
    def __init__(self):
        self.folder: str = ""
        self.rep: str = ""
        self.__path: str = ""

    def __str__(self):
        return f"{self.folder} {self.rep}"

    def __repr__(self):
        return f"JsonTask({self.folder}, {self.rep})"

    def load_from_dict(self, json_data: dict[str, str]):
        self.folder = json_data.get("folder", self.folder)
        self.rep = json_data.get("rep", self.rep)

    def get_path(self) -> str:
        """
        Returns the absolute path of the class task file.
        If the path is not set, it returns an empty string.
        """
        return self.__path

    def load_from_file(self, class_task_path: str) -> ClassTask:
        if not os.path.isfile(class_task_path):
            print(f"Class task file not found: {class_task_path}")
            exit(1)
        with open(class_task_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.load_from_dict(data)
            self.__path = os.path.abspath(class_task_path)
            return self

    def load_student_repo_list(self) -> list[StudentRepo]:
        class_folders: str = self.folder
        rep: str = self.rep
        relative_path = os.path.abspath(os.path.join(os.path.dirname(self.__path), class_folders))
        student_list: list[str] = os.listdir(relative_path)
        student_folder_list = [StudentRepo(os.path.join(relative_path, student), rep) for student in student_list]
        return student_folder_list