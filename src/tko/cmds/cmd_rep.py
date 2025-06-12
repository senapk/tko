from tko.settings.repository import Repository
from tko.settings.settings import Settings
from tko.logger.logger import Logger
from tko.game.task import Task
from tko.play.week_graph import WeekGraph
import yaml # type: ignore
import os
import argparse
# from typing import override

class TaskResume:
    def __init__(self):
        self.rate = 0
        self.flow = 0
        self.edge = 0
        self.time = 0
        self.runs = 0

    def set_coverage(self, value: int):
        self.rate = value
        return self
    
    def set_autonomy(self, value: int):
        self.flow = value
        return self
    
    def set_skill(self, value: int):
        self.edge = value
        return self
    
    def set_elapsed(self, value: int):
        self.time = value
        return self
    
    def set_attempts(self, value: int):
        self.runs = value
        return self

    def to_dict(self):
        return {
            "rate": self.rate,
            "flow": self.flow,
            "edge": self.edge,
            "time": self.time,
            "runs": self.runs
        }

    # @override
    def __str__(self):
        return f"rate:{self.rate}, flow:{self.flow}, edge:{self.edge}, time:{self.time}, runs:{self.runs}"

class CmdRep:
    # @staticmethod
    # def check(args: argparse.Namespace):
    #     rep = Repository(args.folder).load_config().load_game()
    #     logger = Logger.get_instance()
    #     logger.set_log_files(rep.get_history_file(), rep.get_track_folder())

    #     output = logger.check_log_file_integrity()
    #     if len(output) == 0:
    #         print(f"Arquivo de log do repositório {rep} está íntegro.")
    #     else:
    #         print(f"Arquivo de log do repositório {rep} está corrompido.")
    #         print("Erros:")
    #         for error in output:
    #             print(f"- {error}")

    @staticmethod
    def resume(args: argparse.Namespace):
        rep = Repository(args.folder).load_config().load_game()
        logger = Logger.get_instance()
        logger.set_log_files(rep.get_history_file(), rep.get_track_folder())
        history_resume = logger.tasks.resume()
        repository_tasks: dict[str, Task] = rep.game.tasks

        tasks: dict[str, TaskResume] = {}
        for task in repository_tasks.values():
            if task.rate != 0:
                tasks[task.key] = TaskResume().set_coverage(task.rate).set_autonomy(task.flow).set_skill(task.edge)

        for key in history_resume:
            entry = history_resume[key]
            elapsed = entry.get_minutes()
            attempts = entry.att
            if elapsed > 0 or attempts > 0:
                if key not in tasks:
                    tasks[key] = TaskResume()
                tasks[key].set_elapsed(entry.get_minutes()).set_attempts(entry.att)
        
        tasks_str: dict[str, dict[str, int]] = {}
        for key in tasks:
            tasks_str[key] = tasks[key].to_dict()

        print (yaml.dump(tasks_str, sort_keys=False))

    @staticmethod
    def graph(args: argparse.Namespace):
        rep = Repository(args.folder).load_config().load_game()
        logger = Logger.get_instance()
        logger.set_log_files(rep.get_history_file(), rep.get_track_folder())
        wg = WeekGraph(100, 24, week_mode=True)
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
