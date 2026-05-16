from __future__ import annotations
from pathlib import Path
import sys # type: ignore
from typing import Any
import logging
from tko.repository.repository import Repository
from tko.logger.logger import Logger
from tko.logger.task_resume import TaskResume
from tko.logger.log_sort import LogSort
from tko.play.daily_graph import DailyGraph
from tko.mico.collected import Collected, Game
from tko.util.rtext import RText
from tko.repository.repository_paths import RepositoryPaths

import json
import os
import csv


logger = logging.getLogger(__name__)

class CmdCollect:
    @staticmethod
    def resume(repo: Repository) -> dict[str, TaskResume]:
        logger: Logger = repo.logger
        tasks: dict[str, LogSort] = logger.tasks.task_dict
        resume_dict: dict[str, TaskResume] = {}

        game = repo.game
        quest_map: dict[str, str] = {}
        for quest in game.quests.values():
            for task in quest.get_tasks():
                quest_map[task.basic.full_key] = quest.basic.full_key
        for key, log_sort in tasks.items():
            quest_key = quest_map.get(key, "")
            resume = TaskResume(key, quest_key).from_log_sort(log_sort)
            resume_dict[key] = resume
        return resume_dict

    @staticmethod
    def daily_graph(rep: Repository, width: int, height: int, colored: bool) -> str:
        dg = DailyGraph(rep.logger, width, height)
        header, image = dg.get_graph()
        if not colored:
            return "\n".join([x.get_str() for x in header + image])
        return "\n".join([str(x) for x in image])

    @staticmethod
    def load_game_as_quest_list(rep: Repository) -> list[Game.Quest]:
        game = rep.game
        if not game:
            return []
        output: list[Game.Quest] = []

        for quest in game.quests.values():
            output_quest = Game.Quest(quest.basic.full_key)
            output.append(output_quest)
            for task in quest.get_tasks():
                output_quest.tasks.append(Game.Task(key=task.basic.full_key, value=task.game.xp, is_leet=task.config.is_auto, opt=task.config.is_optional))
        return output
    

class CollectSingle:
    class CollectParams:
        def __init__(self):
            self.folder: Path = Path()
            self.width: int = 10
            self.height: int = 10
            self.daily: bool = False
            self.resume: bool = False
            self.game: bool = False
            self.log: bool = False
            self.json_output: bool = False
            self.colored: int = 1


    @staticmethod
    def collect_to_json(repo_folder: Path, daily: bool = True, resume: bool = True, game: bool = True) -> str:
        params = CollectSingle.CollectParams()
        params.folder = repo_folder
        params.daily = daily
        params.resume = resume
        params.game = game
        params.json_output = True # dont echo
        results: Collected = CollectSingle.collect(params)
        return json.dumps(results.to_dict(), indent=4, ensure_ascii=False)

    @staticmethod
    def collect(param: CollectParams) -> Collected:
        rep = Repository(param.folder)
        if not rep.found():
            path = os.path.abspath(param.folder)
            print(f"Repository not found in {path}")
            return Collected()
        rep.set_global_cache()
        from tko.repository.repository_loader import RepositoryLoader
        from tko.repository.game_coordinator import GameCoordinator
        RepositoryLoader(rep).load_config()
        GameCoordinator(rep).load_game(verbose=True)
        data = Collected()

        if param.daily:
            graph = CmdCollect.daily_graph(rep, param.width, param.height, param.colored == 1)
            data.graph = graph
            if not param.json_output:
                print(graph)

        if param.resume:
            resume_data = CmdCollect.resume(rep)
            data.resume = resume_data
            if not param.json_output:
                for key, value in resume_data.items():
                    print(f"{key}: {value.to_dict()}")

        if param.log:
            log_data = rep.logger.history.get_entries()
            data.log = [str(entry) for entry in log_data]
            if not param.json_output:
                for entry in log_data:
                    print(entry)

        if param.game:
            game_data = CmdCollect.load_game_as_quest_list(rep)
            data.quests = game_data
            if not param.json_output:
                for quest in game_data:
                    print(str(quest))
        return data

class CollectMany:
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


    @staticmethod
    def execute(git_dir_list: list[Path], json_path: str | None = None, csv_path: str | None = None, block_prefix: str | None = None):
        git_dir_list = [git_dir for git_dir in git_dir_list if git_dir.is_dir()]
        common_prefix = CollectMany.find_common_prefix([str(folder.name) for folder in git_dir_list])

        usernames = [repo.name[len(common_prefix):].strip("/\\") for repo in git_dir_list]
        padding = max(len(username) for username in usernames) + 1

        output_map: dict[str, Any] = {}
        for git_dir, username in zip(git_dir_list, usernames):
            tko_rep_folder_list = RepositoryPaths.rec_search_for_repo_subdir(git_dir)
            if not tko_rep_folder_list:
                print(RText(f"{username: <{padding}}", "r") + RText(f"TKO repo not found in {git_dir}", "r"))
                continue
            tko_folder = tko_rep_folder_list[0]
            multiple_found = RText(" - Multiple TKO repos found, using the first one.", "r") if len(tko_rep_folder_list) > 1 else RText()
            print(RText(f"{username: <{padding}}", "y" if multiple_found else "g") + f"Running tko collect in {tko_folder}" + multiple_found)
            output = CollectSingle.collect_to_json(tko_folder, daily=False, resume=True, game=False)

            try:
                json_output: dict[str, Any] = json.loads(output) if output != "" else {}
            except json.JSONDecodeError:
                logger.exception("Error: Failed to parse JSON output for %s", username)
                continue
            if "error" in json_output:
                print(RText(f"{username: <{padding}}", "r") + RText(f"Error: {json_output['error']}", "r"))
                continue

            output_map[username] = json_output["resume"] if "resume" in json_output else {}
        if json_path is not None:
            with open(json_path, "w", encoding="utf-8") as f:
                print(RText(f"Saving extracted data to {json_path}", "g"))
                json.dump(output_map, f, indent=4, ensure_ascii=False)
        
        header_keys = ["username", "key", "quest", "minutes", "versions", "executions", "rate", "study", "self", "friend", "concept", "problem", "code", "debug", "refactor", "guided"]
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

                        row: dict[str, Any] = {
                            "username": student_key,
                            "key": data.get("key", ""),
                            "quest": data.get("quest", ""),
                            "minutes": data.get("minutes", 0),
                            "versions": data.get("versions", 0),
                            "executions": data.get("executions", 0),
                            "rate": round(float(data.get("rate", 0.0))),
                            "study": data.get("study", 0),
                            "self": data.get("self", ""),
                            "friend": data.get("friend", ""),
                            "concept": data.get("concept", ""),
                            "problem": data.get("problem", ""),
                            "code": data.get("code", ""),
                            "debug": data.get("debug", ""),
                            "refactor": data.get("refactor", ""),
                            "guided": data.get("guided", "")
                        }

                        if block_prefix is not None:
                            row["block"]= f"{block_prefix}"
                        writer.writerow(row)
            print(RText(f"Saving extracted data to {csv_path}", "g"))
