#!/usr/bin/env python3
from __future__ import annotations
import json
import os
from typing import Any
from tko.mico.class_task import ClassTask
from tko.cmds.cmd_collect import CollectSingle

class Collect:


    
    # @staticmethod
    # def extract_usernames_from_reps(folders: list[str]) -> list[str]:
    #     common_prefix = Collect.find_common_prefix(folders)
    #     usernames = [rep[len(common_prefix):].strip("/\\") for rep in folders]
    #     return usernames


    @staticmethod
    def collect_student_text_map(class_task: ClassTask) -> dict[str, Any]:
        repo_list = class_task.load_student_repo_list()
        student_text_map: dict[str, Any] = {}
        for repo in repo_list:
            text = CollectSingle.collect_to_json(repo.tko_subfolder, daily=True, resume=True, game=True)
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
            print(f"Saving collected data to {collected_path}")
            json.dump(student_text_map, f, indent=4, ensure_ascii=False)