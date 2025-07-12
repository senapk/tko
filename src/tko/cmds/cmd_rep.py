from __future__ import annotations
from tko.settings.repository import Repository
from tko.settings.settings import Settings
from tko.logger.logger import Logger
from tko.logger.task_resume import TaskResume
from tko.logger.log_sort import LogSort
from tko.play.week_graph import DailyGraph
from tko.mico.collected import Collected, Game
import yaml # type: ignore
import json
import os
import argparse
    

class CmdRep:
    class CollectParams:
        def __init__(self):
            self.folder: str = ""
            self.width: int = 10
            self.height: int = 10
            self.daily: bool = False
            self.resume: bool = False
            self.game: bool = False
            self.log: bool = False
            self.json_output: bool = False
            self.colored: int = 1

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
    def graph(rep: Repository, width: int, height: int, colored: bool) -> str:
        dg = DailyGraph(rep.logger, width, height)
        image = dg.get_graph()
        if not colored:
            return "\n".join([x.get_str() for x in image])
        return "\n".join([str(x) for x in image])

    @staticmethod
    def load_game_as_cluster_list(rep: Repository) -> list[Game.Cluster]:
        game = rep.game
        if not game:
            return []
        output: list[Game.Cluster] = []
        for cluster_key in game.ordered_clusters:
            cluster = game.clusters[cluster_key]
            output_cluster = Game.Cluster(cluster.key)
            output.append(output_cluster)
            for quest in cluster.get_quests():
                output_quest = Game.Quest(quest.key, quest.value)
                output_cluster.quests.append(output_quest)
                for task in quest.get_tasks():
                    output_quest.tasks.append(Game.Task(key=task.key, value=task.xp, is_leet=task.is_leet(), opt=task.opt))
        return output

    @staticmethod
    def collect_main(args: argparse.Namespace):
        params = CmdRep.CollectParams()
        params.folder = args.folder
        params.width = args.width
        params.height = args.height
        params.daily = args.daily
        params.resume = args.resume
        params.game = args.game
        params.log = args.log
        params.json_output = args.json
        params.colored = args.color
        data = CmdRep.collect(params)

        if params.json_output:
            # print(yaml.dump(data))
            print(json.dumps(data.to_dict(), indent=4, ensure_ascii=False))

    @staticmethod
    def collect(param: CollectParams) -> Collected:
        rep = Repository(param.folder)
        if not rep.found():
            path = os.path.abspath(param.folder)
            print(f"Repository not found in {path}")
            return Collected()
        
        rep.load_config().load_game()
        data = Collected()

        if param.daily:
            graph = CmdRep.graph(rep, param.width, param.height, param.colored == 1)
            data.graph = graph
            if not param.json_output:
                print(graph)

        if param.resume:
            resume_data = CmdRep.resume(rep)
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
            game_data = CmdRep.load_game_as_cluster_list(rep)
            data.clusters = game_data
            if not param.json_output:
                for cluster in game_data:
                    print(str(cluster))

        return data


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
    def list(_args: argparse.Namespace):
        settings = Settings()
        print(f"SettingsFile\n- {settings.settings_file}")
        print(str(settings))

    @staticmethod
    def add(args: argparse.Namespace):
        settings = Settings().set_alias_remote(args.alias, args.value)
        settings.save_settings()

    @staticmethod
    def rm(args: argparse.Namespace):
        sp = Settings()
        if args.alias in sp.dict_alias_remote:
            sp.dict_alias_remote.pop(args.alias)
            sp.save_settings()
        else:
            print("Repository not found.")

    @staticmethod
    def reset(args: argparse.Namespace):
        _ = args
        sp = Settings().reset()
        print(sp.settings_file)
        sp.save_settings()

    # @staticmethod
    # def graph(args):
    #     rep = Repository(args.folder).load_config().load_game()
    #     rep.game.check_cycle()
    #     Graph(rep.game).generate()
