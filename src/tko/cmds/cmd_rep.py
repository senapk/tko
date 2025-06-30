from tko.settings.repository import Repository
from tko.settings.settings import Settings
from tko.logger.logger import Logger
from tko.logger.task_resume import TaskResume
from tko.logger.log_sort import LogSort
from tko.play.week_graph import DailyGraph
from tko.tejo.collected_data import CollectedData
import yaml # type: ignore
import json
import os
import argparse
    

class CmdRep:
    @staticmethod
    def resume(rep: Repository) -> dict[str, TaskResume]:
        logger: Logger = rep.logger
        tasks: dict[str, LogSort] = logger.tasks.task_dict
        resume_dict: dict[str, TaskResume] = {}

        for key in tasks:
            log_sort = tasks[key]
            resume = TaskResume().from_log_sort(log_sort)
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
    def load_game_tasks(rep: Repository) -> list[CollectedData.Quest]:
        game = rep.game
        if not game:
            return []
        output: list[CollectedData.Quest] = []
        for cluster_key in game.ordered_clusters:
            cluster = game.clusters[cluster_key]
            opt_quest = not cluster.main_cluster
            for quest in cluster.get_quests():
                output_quest = CollectedData.Quest(quest.key, opt=opt_quest)
                for task in quest.get_tasks():
                    output_quest.tasks.append(CollectedData.Task(key=task.key, value=task.xp, is_leet=task.is_leet(), opt=task.opt))
                output.append(output_quest)
        return output

    @staticmethod
    def collect(args: argparse.Namespace):
        rep = Repository(args.folder)
        if not rep.found():
            path = os.path.abspath(args.folder)
            print(f"Repository not found in {path}")
            return
        rep.load_config().load_game()
        data = CollectedData()

        if args.daily:
            graph = CmdRep.graph(rep, args.width, args.height, args.color == 1)
            data.graph = graph
            if not args.json:
                print(graph)

        if args.resume:
            resume_data = CmdRep.resume(rep)
            data.resume = resume_data
            if not args.json:
                for key, value in resume_data.items():
                    print(f"{key}: {value.to_dict()}")

        if args.log:
            log_data = rep.logger.history.get_entries()
            data.log = [str(entry) for entry in log_data]
            if not args.json:
                for entry in log_data:
                    print(entry)
        
        if args.game:
            game_data = CmdRep.load_game_tasks(rep)
            data.game = game_data
            if not args.json:
                for quest in game_data:
                    print(str(quest))

        if args.json:
            # print(yaml.dump(data))
            print(json.dumps(data, indent=4, default=lambda o: o.__dict__))


    @staticmethod
    def upgrade(args: argparse.Namespace):
        folder: str = args.folder
        if os.path.exists(os.path.join(folder, "rep.json")):
            os.rename(os.path.join(folder, "rep.json"), os.path.join(folder, "repository.json"))
        remote_folder = os.path.join(folder, "remote")
        os.makedirs(remote_folder, exist_ok=True)
        for entry in os.listdir(folder):
            path = os.path.join(folder, entry)
            if entry == "remote":
                continue
            if os.path.isdir(path):
                os.rename(path, os.path.join(remote_folder, entry))
        print(f"Repositório {folder} foi atualizado.")

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
