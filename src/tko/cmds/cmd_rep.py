from tko.settings.repository import Repository
from tko.settings.settings import Settings
from tko.logger.logger import Logger
from tko.logger.log_resume import LogResume
from tko.logger.log_sort import LogSort
from tko.play.week_graph import DailyGraph
import yaml # type: ignore
import os
import argparse


class CmdRep:
    @staticmethod
    def show(args: argparse.Namespace):
        rep = Repository(args.folder).load_config().load_game()
        if args.weekgraph:
            CmdRep.graph(rep, week_mode=True)
        if args.daygraph:
            CmdRep.graph(rep, week_mode=False)
        if args.resume:
            CmdRep.resume(rep)

    @staticmethod
    def resume(rep: Repository):
        logger: Logger = rep.logger
        tasks: dict[str, LogSort] = logger.tasks.task_dict
        resume_dict: dict[str, LogResume] = {}

        for key in tasks:
            log_sort = tasks[key]
            resume = LogResume().from_log_sort(log_sort)
            resume_dict[key] = resume

        
        tasks_str: dict[str, dict[str, str]] = {}
        for key, value in resume_dict.items():
            tasks_str[key] = value.to_dict()

        print (yaml.dump(tasks_str, sort_keys=False))

    @staticmethod
    def graph(rep: Repository, week_mode: bool):
        wg = DailyGraph(rep.logger, 100, 24, week_mode)
        image = wg.get_graph()
        week = wg.get_collected()
        pad = " " * 12
        print(f"{pad}{image[0]}")
        print(f"{pad}{image[1]}")
        image = image[2:]

        for i, line in enumerate(image):
            if i < len(week):
                index = i + 1
                index_pad = str(index).rjust(2, " ")
                print(f"{index_pad} - {week[i]}h ", end="")
            else:
                print(pad, end="")
            print(line)

        # for i in range(len(week)):
        #     print(f"{i} - {week[i]}h")

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
