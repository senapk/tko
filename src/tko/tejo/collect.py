#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json

from typing import Any
from .paths import Paths
from .student_repo import StudentRepo
from .class_task import ClassTask

class Collect:
    @staticmethod
    def get_student_info_map(repo_list: list[StudentRepo]) -> dict[str, Any]:
        user_text_map: dict[str, Any] = {}
        for repo in repo_list:
            text = repo.run_tko_collect()
            if text != "":
                user_text_map[repo.get_student_key()] = text
        return user_text_map

    @staticmethod
    def collect_student_text_map(class_task: ClassTask) -> dict[str, Any]:
        repo_list = class_task.load_student_repo_list()
        student_text_map = Collect.get_student_info_map(repo_list)
        return student_text_map

    @staticmethod
    def main(args: argparse.Namespace) -> None:
        class_task = ClassTask().load_from_file(args.target)
        student_text_map = Collect.collect_student_text_map(class_task)
        collected_path = Paths.get_default_collected(class_task)
        with open(collected_path, "w", encoding="utf-8") as f:
            json.dump(student_text_map, f, indent=4, ensure_ascii=False)