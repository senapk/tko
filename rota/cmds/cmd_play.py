from rota.settings.settings import Settings
from rota.game.game import Game
from rota.settings.repository import Repository
from rota.play.play import Play
from rota.util.logger import Logger, LogAction
from typing import Dict
from rota.util.text import Text
import os

class CmdPlay:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.rep: Repository | None = None
        self.folder = ""

    def load_folder(self, folder: str):
        self.folder = folder
        self.rep = Repository(folder)
        if not self.rep.has_local_config_file():
            print(Text.format("{r}: O parâmetro para o comando {g} {y} deve a pasta onde você iniciou o repositório.", "Erro", "rota play", "<pasta>"))
            print(Text.format("{g}: Navegue ou passe o caminho até a pasta do repositório e tente novamente.", "Ação"))
            print(Text.format("{g}: Ou use {y} para criar um novo repositório.", "Ação","rota init --remote [fup|poo|ed]"))
            raise Warning(Text.format("{r}: {y} {}", "Erro:", folder, "não contém um repositório do rota"))
        self.rep.load_config().load_game()
        return self


    def execute(self):
        if self.rep is None:
            raise Warning("Repositório não encontrado")
        
        logger: Logger = Logger.get_instance()
        logger.set_history_file(self.rep.get_history_file())
        logger.record_open()
        play = Play(self.settings, self.rep)
        logger.set_daily(self.rep.get_daily_file(), play.game.tasks)
        play.play()
        logger.record_quit()


    # @staticmethod
    # def choose_destiny(rep_alias):
    #     print(Text().add("Repositório local ainda não foi criado, onde você deseja criá-lo?"))
    #     here_cwd = os.path.join(os.getcwd(), rep_alias)
    #     qxcode = os.path.join(os.path.expanduser("~"), "qxcode", rep_alias)

    #     while True:
    #         print(Text().addf("r", "1").add(" - ").add(here_cwd))
    #         print(Text().addf("r", "2").add(" - ").add(qxcode))
    #         print(Text().addf("r", "3").add(" - ").add("Outra pasta"))
    #         print(Text().add("Default ").addf("r", "1").add(": "), end="")
    #         op = input()
    #         if op == "":
    #             op = "1"
    #         if op == "1":
    #             home_qxcode = here_cwd
    #             break
    #         if op == "2":
    #             home_qxcode = qxcode
    #             break
    #         if op == "3":
    #             print(Text().addf("y", "Navegue até o diretório desejado e execute o rota novamente."))
    #             exit(1)

    #     if not os.path.exists(home_qxcode):
    #         os.makedirs(home_qxcode)
    #     return home_qxcode