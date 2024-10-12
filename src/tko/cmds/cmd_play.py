from tko.settings.settings import Settings
from tko.game.game import Game
from tko.settings.repository import Repository
from tko.play.play import Play
from tko.util.logger import Logger, LogAction
from typing import Dict
from tko.util.text import Text
import os

class CmdPlay:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.rep: Repository | None = None
        self.alias = ""
        self.folder = ""

    def set_alias(self, rep_alias: str):
        if self.settings.has_rep_folder(rep_alias):
            folder = self.settings.get_rep_folder(rep_alias)
            print(f"Abrindo repositório de {rep_alias} em {folder}")
            rep = Repository(folder).load_data_from_json().load_game()
        elif rep_alias in self.settings.remote:
            folder = CmdPlay.choose_destiny(rep_alias)
            os.makedirs(folder, exist_ok=True)
            rep = Repository(folder)
            rep.set_remote_url(self.settings.get_remote(rep_alias))
            rep.save_data_to_json()
            rep.load_data_from_json()
            rep.load_game()
            self.settings.set_rep_folder(rep_alias, folder)
        else:
            raise Warning("Repositório remoto não encontrado")
        self.rep = rep
        return self

    def set_folder(self, folder: str):
        self.folder = folder
        self.rep = Repository(folder).load_data_from_json().load_game()
        return self


    def execute(self):
        if self.rep is None:
            raise Warning("Repositório não encontrado")
        
        logger: Logger = Logger.get_instance()
        logger.set_log_file(self.rep.get_log_file())
        logger.record_event(LogAction.OPEN)
        target = ""
        if self.folder != "":
            target = self.folder
        else:
            target = self.alias
        print(f"Abrindo repositório {target}")
        play = Play(self.settings, self.rep)
        play.play()
        logger.record_event(LogAction.QUIT)


    @staticmethod
    def choose_destiny(rep_alias):
        print(Text().add("Repositório ainda não foi criado, onde você deseja criá-lo?"))
        here_cwd = os.path.join(os.getcwd(), rep_alias)
        qxcode = os.path.join(os.path.expanduser("~"), "qxcode", rep_alias)

        while True:
            print(Text().addf("r", "1").add(" - ").add(here_cwd))
            print(Text().addf("r", "2").add(" - ").add(qxcode))
            print(Text().addf("r", "3").add(" - ").add("Outra pasta"))
            print(Text().add("Default ").addf("r", "1").add(": "), end="")
            op = input()
            if op == "":
                op = "1"
            if op == "1":
                home_qxcode = here_cwd
                break
            if op == "2":
                home_qxcode = qxcode
                break
            if op == "3":
                print(Text().addf("y", "Navegue até o diretório desejado e execute o tko novamente."))
                exit(1)

        if not os.path.exists(home_qxcode):
            os.makedirs(home_qxcode)
        return home_qxcode