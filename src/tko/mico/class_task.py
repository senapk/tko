from __future__ import annotations
from tko.mico.student_repo import StudentRepo
import json
import os

class ClassTask:
    def __init__(self, file_path: str = ""):
        self.file_path: str = os.path.abspath(file_path)  # path to the class task file
        self.task_name = os.path.basename(self.file_path)[:-5]
        self.class_dir: str = ""  # directory of the class task
        self.cache_dir: str = "." # cache dir folder to store collected data
        self.sub_dir: str = "."    # subdirectory for the class task, usually [ fup | ed | poo | . ]
        self.reference_dir: str | None = None  # directory for reference data, usually [ reference/fup | reference/ed | reference/poo | . ]

    def __str__(self):
        return f"{self.class_dir} {self.sub_dir}"

    def __repr__(self):
        return f"JsonTask({self.class_dir}, {self.sub_dir})"

    def load_from_dict(self, json_data: dict[str, str]):
        file_path_dir = os.path.dirname(self.file_path)
        self.class_dir = os.path.normpath(os.path.join(file_path_dir, json_data.get("class", self.class_dir)))
        self.cache_dir = os.path.normpath(os.path.join(file_path_dir, json_data.get("cache", self.cache_dir)))
        self.sub_dir = json_data.get("subdir", self.sub_dir)
        if "reference" in json_data:
            self.reference_dir = os.path.normpath(os.path.join(file_path_dir, json_data.get("reference", "")))

    def load_from_file(self) -> ClassTask:
        if not os.path.isfile(self.file_path):
            print(f"Class task file not found: {self.file_path}")
            exit(1)
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.load_from_dict(data)
            return self

    def get_reference_rep(self) -> str | None:
        return self.reference_dir
    
    def get_default_collected(self) -> str:
        return os.path.join(self.cache_dir, f"{self.task_name}_collected.json")

    def get_default_graph_joined(self) -> tuple[str, str]:
        name = os.path.join(self.cache_dir, f"{self.task_name}_graph_")
        return name + "color.txt", name + "mono.txt"

    def get_default_simple_csv(self) -> str:
        return os.path.join(self.cache_dir, f"{self.task_name}_grade_tasks.csv")
    
    def get_default_quest_csv(self) -> str:
        return os.path.join(self.cache_dir, f"{self.task_name}_grade_quests.csv")

    def get_default_full_csv(self) -> str:
        return os.path.join(self.cache_dir, f"{self.task_name}_grade_full.csv")

    def load_student_repo_list(self) -> list[StudentRepo]:
        student_list: list[str] = os.listdir(self.class_dir)
        student_list = sorted(student_list, key=lambda x: x.lower())  # sort students by name
        student_folder_list = [StudentRepo(os.path.join(self.class_dir, student), self.sub_dir) for student in student_list]
        return student_folder_list