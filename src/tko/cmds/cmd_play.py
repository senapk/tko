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
        if self.settings.has_alias_folder(rep_alias):
            folder = self.settings.get_alias_folder(rep_alias)
            rep = Repository(folder)
            if rep.has_local_config_file():
                rep.load_data_from_config_file().load_game()
                print(Text("Abrindo repositório de {g} em {g}", rep_alias, folder))
                self.rep = rep
                self.alias = rep_alias
                return self
            else:
                print(f"Repositório {rep_alias} não encontrado em {folder}")
                self.settings.del_alias_folder(rep_alias)
                # vai para o próximo bloco

        if rep_alias in self.settings.dict_alias_remote:
            print(Text("Repositório remoto {g} encontrado", rep_alias))
            folder = CmdPlay.choose_destiny(rep_alias)
            os.makedirs(folder, exist_ok=True)
            rep = Repository(folder)
            rep.set_remote_source(self.settings.get_alias_remote(rep_alias))
            rep.save_data_to_config_file()
            rep.load_data_from_config_file()
            rep.load_game()
            self.settings.set_alias_folder(rep_alias, folder)
            self.rep = rep
            self.alias = rep_alias
            return self
        
        raise Warning(Text("Repositório remoto {r} não encontrado", rep_alias))

    def load_folder(self, folder: str):
        self.folder = folder
        
        self.rep = Repository(folder)
        if not self.rep.has_local_config_file():
            print("Arquivo de configuração do repositório não encontrado")
            print("Você deseja criar um repositorio na pasta {}? ".format(folder), end="")
            print("s/n: ", end="")
            op = input()
            if op == "s":
                self.rep.create_empty_config_file(point_to_local_readme=True)
                self.settings.set_alias_folder(self.alias, folder)
                print("Repositório criado com sucesso")
            else:
                raise Warning("Repositório não encontrado")
        self.rep.load_data_from_config_file().load_game()
        return self


    def execute(self):
        if self.rep is None:
            raise Warning("Repositório não encontrado")
        
        logger: Logger = Logger.get_instance()
        logger.set_history_file(self.rep.get_history_file())
        logger.record_other_event(LogAction.OPEN)
        # target = ""
        # if self.folder != "":
        #     target = self.folder
        # else:
        #     target = self.alias
        play = Play(self.settings, self.rep)
        logger.set_daily(self.rep.get_daily_file(), play.game.tasks)
        play.play()
        logger.record_other_event(LogAction.QUIT)


    @staticmethod
    def choose_destiny(rep_alias):
        print(Text().add("Repositório local ainda não foi criado, onde você deseja criá-lo?"))
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