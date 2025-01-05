from rota.game.game import Game
# from rota.game.graph import Graph
from rota.settings.repository import Repository
from rota.settings.settings import Settings
from rota.settings.logger import Logger
from rota.game.task import Task
import yaml # type: ignore
import os

class TaskResume:
    def __init__(self):
        self.coverage = 0
        self.autonomy = 0
        self.skill = 0
        self.elapsed = 0
        self.attempts = 0

    def set_coverage(self, value: int):
        self.coverage = value
        return self
    
    def set_autonomy(self, value: int):
        self.autonomy = value
        return self
    
    def set_skill(self, value: int):
        self.skill = value
        return self
    
    def set_elapsed(self, value: int):
        self.elapsed = value
        return self
    
    def set_attempts(self, value: int):
        self.attempts = value
        return self

    def to_dict(self):
        return {
            "coverage": self.coverage,
            "autonomy": self.autonomy,
            "skill": self.skill,
            "elapsed": self.elapsed,
            "attempts": self.attempts
        }

    def __str__(self):
        return f"coverage:{self.coverage}, autonomy:{self.autonomy}, skill:{self.skill}, elapsed:{self.elapsed}, attempts:{self.attempts}"

class CmdRep:
    @staticmethod
    def check(args):
        rep = Repository(args.folder).load_config().load_game()
        logger = Logger.get_instance()
        logger.set_log_files(rep.get_history_file())

        output = logger.check_log_file_integrity()
        if len(output) == 0:
            print(f"Arquivo de log do repositório {rep} está íntegro.")
        else:
            print(f"Arquivo de log do repositório {rep} está corrompido.")
            print("Erros:")
            for error in output:
                print(f"- {error}")

    @staticmethod
    def resume(args):
        rep = Repository(args.folder).load_config().load_game()
        logger = Logger.get_instance()
        logger.set_log_files(rep.get_history_file())
        history_resume = logger.tasks.resume()
        repository_tasks: dict[str, Task] = rep.game.tasks

        tasks: dict[str, TaskResume] = {}
        for task in repository_tasks.values():
            if task.coverage != 0:
                tasks[task.key] = TaskResume().set_coverage(task.coverage).set_autonomy(task.autonomy).set_skill(task.skill)

        for key in history_resume:
            if key not in tasks:
                continue
            entry = history_resume[key]
            tasks[key].set_elapsed(entry.get_minutes()).set_attempts(entry.attempts)
        
        tasks_str: dict[str, dict[str, int]] = {}
        for key in tasks:
            tasks_str[key] = tasks[key].to_dict()

        print (yaml.dump(tasks_str, sort_keys=False))


    @staticmethod
    def upgrade(args):
        folder = args.folder
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
    def list(_args):
        settings = Settings()
        print(f"SettingsFile\n- {settings.settings_file}")
        print(str(settings))

    @staticmethod
    def add(args):
        settings = Settings().set_alias_remote(args.alias, args.value)
        settings.save_settings()

    @staticmethod
    def rm(args):
        sp = Settings()
        if args.alias in sp.dict_alias_remote:
            sp.dict_alias_remote.pop(args.alias)
            sp.save_settings()
        else:
            print("Repository not found.")

    @staticmethod
    def reset(_):
        sp = Settings().reset()
        print(sp.settings_file)
        sp.save_settings()

    # @staticmethod
    # def graph(args):
    #     rep = Repository(args.folder).load_config().load_game()
    #     rep.game.check_cycle()
    #     Graph(rep.game).generate()
