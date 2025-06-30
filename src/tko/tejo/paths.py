from tko.tejo.class_task import ClassTask

import os

class Paths:
    @staticmethod
    def get_default_collected(class_task: ClassTask) -> str:
        base_dir = os.path.dirname(class_task.get_path())
        name, _ = os.path.splitext(os.path.basename(class_task.get_path()))
        return os.path.join(base_dir, f"{name}_collected.json")

    @staticmethod
    def get_default_graph_joined(class_task: ClassTask) -> tuple[str, str]:
        base_dir = os.path.dirname(class_task.get_path())
        name, _ = os.path.splitext(os.path.basename(class_task.get_path()))
        name = os.path.join(base_dir, f"{name}_graph_")
        return name + "color.txt", name + "mono.txt"
    
    @staticmethod
    def get_default_simple_csv(class_task: ClassTask) -> str:
        base_dir = os.path.dirname(class_task.get_path())
        name, _ = os.path.splitext(os.path.basename(class_task.get_path()))
        return os.path.join(base_dir, f"{name}_short_csv.csv")
        