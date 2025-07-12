#!/usr/bin/env python3
from __future__ import annotations
import json
import os
from typing import Any
import subprocess
from .student_repo import StudentRepo
from .class_task import ClassTask

class Collect:

    @staticmethod
    def run_tko_collect(repo: StudentRepo) -> str:
        """
        Run the tko collect command in the student's repository.
        """
        folder = repo.folder
        rep = repo.tko_subfolder
        print("Loading info from " + folder)
        rep_folder = os.path.join(folder, rep)
        if not os.path.isdir(rep_folder):
            return ""
        result = subprocess.run(["tko", "rep", rep_folder, "collect", "--daily", "--resume", "--game", "--json"], capture_output=True, text=True)
        return result.stdout


    @staticmethod
    def collect_student_text_map(class_task: ClassTask) -> dict[str, Any]:
        repo_list = class_task.load_student_repo_list()
        student_text_map: dict[str, Any] = {}
        for repo in repo_list:
            text = Collect.run_tko_collect(repo)
            if text != "":
                student_text_map[repo.get_student_key()] = text
        return student_text_map

    @staticmethod
    def main(target: str) -> None:
        class_task = ClassTask(target).load_from_file()
        student_text_map = Collect.collect_student_text_map(class_task)
        collected_path = class_task.get_default_collected()
        os.makedirs(os.path.dirname(collected_path), exist_ok=True)
        with open(collected_path, "w", encoding="utf-8") as f:
            json.dump(student_text_map, f, indent=4, ensure_ascii=False)