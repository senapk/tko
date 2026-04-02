from __future__ import annotations
from pathlib import Path
from typing import Any
from tko.settings.repository import Repository
from tko.settings.settings import Settings
from tko.logger.logger import Logger
from tko.logger.task_resume import TaskResume
from tko.logger.log_sort import LogSort
from tko.play.daily_graph import DailyGraph
from tko.mico.collected import Collected, Game
from tko.util.text import Text
from tko.settings.rep_paths import RepPaths

import yaml # type: ignore
import json
import os
import argparse
import csv
    

class CmdCollect:
    @staticmethod
    def resume(rep: Repository) -> dict[str, TaskResume]:
        logger: Logger = rep.logger
        tasks: dict[str, LogSort] = logger.tasks.task_dict
        resume_dict: dict[str, TaskResume] = {}

        for key in tasks:
            log_sort = tasks[key]
            resume = TaskResume(key).from_log_sort(log_sort)
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
            output_quest = Game.Quest(quest.get_full_key())
            output.append(output_quest)
            for task in quest.get_tasks():
                output_quest.tasks.append(Game.Task(key=task.get_full_key(), value=task.xp, is_leet=task.is_auto(), opt=task.is_optional()))
        return output
    
    @staticmethod
    def collect_batch(args: argparse.Namespace):
        git_repo_list: list[Path] = [Path(x) for x in args.path]
        CollectMany.execute(git_repo_list, json_path=args.json, csv_path=args.csv, block_prefix=args.block_prefix)

    @staticmethod
    def collect_main(args: argparse.Namespace):
        params = CollectSingle.CollectParams()
        params.folder = Path() if args.changedir is None else Path(args.changedir)
        params.width = args.width
        params.height = args.height
        params.daily = args.daily
        params.resume = args.resume
        params.game = args.game
        params.log = args.log
        params.json_output = args.json
        params.colored = args.color
        data: Collected = CollectSingle.collect(params)

        if params.json_output:
            # print(yaml.dump(data))
            print(json.dumps(data.to_dict(), indent=4, ensure_ascii=False))


    @staticmethod
    def update(args: argparse.Namespace):
        folder = args.folder
        if not os.path.isdir(folder):
            print(f"Folder {folder} does not exist.")
            return
        rep = Repository(folder)
        if not rep.found():
            print(f"Folder {folder} is not a valid tko repository.")
            return
        rep.load_config().load_game()
        print(f"Repositório cache atualizado.")

    @staticmethod
    def list(args: argparse.Namespace):
        settings = Settings(args.settings)
        print(f"SettingsFile\n- {settings.settings_dir}")
        print(str(settings))

    # @staticmethod
    # def graph(args):
    #     rep = Repository(args.folder).load_config().load_game()
    #     rep.game.check_cycle()
    #     Graph(rep.game).generate()

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
        rep.set_global_cache().load_config().load_game(silent=True)
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
            log_data = sorted(rep.logger.history.get_entries().items(), key=lambda x: x[0])
            data.log = [str(entry) for _, entry in log_data]
            if not param.json_output:
                for _, entry in log_data:
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
            tko_rep_folder_list = RepPaths.rec_search_for_repo_subdir(git_dir)
            if not tko_rep_folder_list:
                print(Text("").addf("r", f"{username: <{padding}}").addf("r", f"TKO repo not found in {git_dir}"))
                continue
            tko_folder = tko_rep_folder_list[0]
            multiple_found = Text().addf("r", " - Multiple TKO repos found, using the first one." if len(tko_rep_folder_list) > 1 else "")
            print(Text("").addf("g" if not multiple_found else "y", f"{username: <{padding}}").addf("", f"Running tko collect in {tko_folder}").add(multiple_found))
            output = CollectSingle.collect_to_json(tko_folder, daily=False, resume=True, game=False)

            try:
                json_output: dict[str, Any] = json.loads(output) if output != "" else {}
            except json.JSONDecodeError:
                print(Text("").addf("r", f"{username: <{padding}}").addf("r", "Error: Failed to parse JSON output"))
                continue
            if "error" in json_output:
                print(Text("").addf("r", f"{username: <{padding}}").addf("r", f"Error: {json_output['error']}"))
                continue

            output_map[username] = json_output["resume"] if "resume" in json_output else {}
        if json_path is not None:
            with open(json_path, "w", encoding="utf-8") as f:
                print(Text("").addf("g", f"Saving extracted data to {json_path}"))
                json.dump(output_map, f, indent=4, ensure_ascii=False)
        
        header_keys = ["username", "key", "minutes", "versions", "executions", "rate", "study", "self", "friend", "concept", "problem", "code", "debug", "refactor", "guided"]
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
                            "key": key,
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
            print(Text("").addf("g", f"Saving extracted data to {csv_path}"))