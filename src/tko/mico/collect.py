#!/usr/bin/env python3
from __future__ import annotations
import json
import csv
import os
from typing import Any
import subprocess
from tko.mico.student_repo import StudentRepo
from tko.mico.class_task import ClassTask
from tko.util.text import Text

class Collect:

    @staticmethod
    def find_common_prefix(folders: list[str]) -> str:
        if not folders:
            return ""
        common = ""
        for chars in zip(*folders):
            if all(c == chars[0] for c in chars):
                common += chars[0]
            else:
                break
        return common
    
    # @staticmethod
    # def extract_usernames_from_reps(folders: list[str]) -> list[str]:
    #     common_prefix = Collect.find_common_prefix(folders)
    #     usernames = [rep[len(common_prefix):].strip("/\\") for rep in folders]
    #     return usernames

    @staticmethod
    def run_tko_collect(repo: StudentRepo, daily: bool = True, resume: bool = True, game: bool = True) -> str:
        """
        Run the tko collect command in the student's repository.
        """
        folder = repo.folder
        rep = repo.tko_subfolder
        rep_folder = os.path.join(folder, rep)
        if not os.path.isdir(rep_folder):
            return ""
        
        args: list[str] = []
        if daily:
            args.append("--daily")
        if resume:
            args.append("--resume")
        if game:
            args.append("--game")

        result = subprocess.run(["tko", "rep", rep_folder, "collect"] + args + ["--json"], capture_output=True, text=True)
        return result.stdout


    @staticmethod
    def collect_student_text_map(class_task: ClassTask) -> dict[str, Any]:
        repo_list = class_task.load_student_repo_list()
        student_text_map: dict[str, Any] = {}
        for repo in repo_list:
            text = Collect.run_tko_collect(repo, daily=True, resume=True, game=True)
            if text != "":
                student_text_map[repo.get_student_key()] = text
        return student_text_map

    @staticmethod
    def find_tko_path_inside_repo(folder: str) -> str | None:
        if os.path.isdir(os.path.join(folder, ".tko")):
            return "."
        for subfolder in os.listdir(folder):
            subfolder_path = os.path.join(folder, subfolder)
            if os.path.isdir(subfolder_path) and os.path.isdir(os.path.join(subfolder_path, ".tko")):
                return subfolder
        return None

    @staticmethod
    def extract_to(reps: list[str], json_path: str | None = None, csv_path: str | None = None, block_prefix: str | None = None):
        folders = [rep for rep in reps if os.path.isdir(rep)]
        common_prefix = Collect.find_common_prefix(folders)

        usernames = [rep[len(common_prefix):].strip("/\\") for rep in folders]
        padding = max(len(username) for username in usernames) + 1

        output_map: dict[str, Any] = {}
        for rep, username in zip(folders, usernames):
            subfolder = Collect.find_tko_path_inside_repo(rep)
            if subfolder is None:
                print(Text("").addf("r", f"{username: <{padding}}").addf("y", f"No tko repository found inside {rep}"))
                continue
            print(Text("").addf("y", f"{username: <{padding}}").add(f"Running tko collect in " + rep + "/").addf("g", subfolder))
            repo = StudentRepo(rep, subfolder)
            output = Collect.run_tko_collect(repo, daily=False, resume=True, game=False)

            try:
                json_output: dict[str, Any] = json.loads(output) if output != "" else {}
            except json.JSONDecodeError:
                print(Text("").addf("r", f"{username: <{padding}}").addf("r", "Error: Failed to parse JSON output"))
                continue
            if "error" in json_output:
                print(Text("").addf("r", f"{username: <{padding}}").addf("r", f"Error: {json_output['error']}"))
                continue

            output_map[username] = json_output["resume"] if "resume" in json_output else ""
        if json_path is not None:
            with open(json_path, "w", encoding="utf-8") as f:
                print(Text("").addf("g", f"Saving extracted data to {json_path}"))
                json.dump(output_map, f, indent=4, ensure_ascii=False)
        
        header_keys = ["username", "key", "minutes", "versions", "executions", "rate", "percent", "study", "human", "other", "guide", "alone", "iagen"]
        if block_prefix is not None:
            header_keys = ["block"] + header_keys
        if csv_path is not None:
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=header_keys)
                writer.writeheader()
                for student_key, info in output_map.items():
                    for key, data in info.items():
                        if "@" in key:
                            key = key.split("@")[1]
                        minutes = data.get("minutes", 0)
                        versions = data.get("versions", 0)
                        executions = data.get("executions", 0)
                        rate = round(float(data.get("rate", 0.0)))
                        percent = round(float(data.get("percent", 0.0)))
                        study = data.get("study", "")
                        human = data.get("human", "")
                        other = data.get("other", "")
                        guide = data.get("guide", "")
                        alone = data.get("alone", "")
                        iagen = data.get("iagen", "")

                        row: dict[str, Any] = {
                            "username": student_key,
                            "key": key,
                            "minutes": minutes,
                            "versions": versions,
                            "executions": executions,
                            "rate": rate,
                            "percent": percent,
                            "study": study,
                            "human": human,
                            "other": other,
                            "guide": guide,
                            "alone": alone,
                            "iagen": iagen
                            }
                        if block_prefix is not None:
                            row["block"]= f"{block_prefix}"
                        writer.writerow(row)
            print(Text("").addf("g", f"Saving extracted data to {csv_path}"))



    @staticmethod
    def main(target: str) -> None:
        class_task = ClassTask(target).load_from_file()
        student_text_map = Collect.collect_student_text_map(class_task)
        collected_path = class_task.get_default_collected()
        os.makedirs(os.path.dirname(collected_path), exist_ok=True)
        with open(collected_path, "w", encoding="utf-8") as f:
            print(f"Saving collected data to {collected_path}")
            json.dump(student_text_map, f, indent=4, ensure_ascii=False)