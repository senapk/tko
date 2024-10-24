from tko.game.game import Game
from tko.game.graph import Graph
from tko.settings.repository import Repository
from tko.settings.settings import Settings
from tko.util.logger import Logger

import os

class CmdRep:
    @staticmethod
    def check(args):
        folder = Settings().get_alias_folder(args.alias)
        rep = Repository(folder).load_data_from_config_file().load_game()
        logger = Logger.get_instance()
        logger.set_history_file(rep.get_history_file())

        output = logger.check_log_file_integrity()
        if len(output) == 0:
            print(f"Arquivo de log do repositório {rep} está íntegro.")
        else:
            print(f"Arquivo de log do repositório {rep} está corrompido.")
            print("Erros:")
            for error in output:
                print(f"- {error}")

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

    @staticmethod
    def graph(args):
        settings = Settings()
        folder:str = settings.get_alias_folder(args.alias)
        rep = Repository(folder).load_data_from_config_file().load_game()
        rep.game.check_cycle()
        Graph(rep.game).generate()
