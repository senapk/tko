from tko.settings.settings import Settings
from tko.game.game import Game
from tko.settings.rep_settings import RepSource
from tko.play.play import Play
from tko.util.logger import Logger, LogAction
from typing import Dict
import os

class CmdPlay:
    @staticmethod
    def execute(rep_alias: str, settings: Settings):
        while True:
            rep_alias = settings.check_rep_alias(rep_alias)
            rep_source: RepSource = settings.get_rep_source(rep_alias)
            rep = settings.get_rep_data(rep_alias)
            rep_dir = rep.get_rep_dir()
            file = rep_source.get_file_or_cache(rep_dir)
            game = Game()
            game.parse_file(file)

            # passing a lambda function to the play class to save the settings
            play = Play(settings=settings, game=game, rep=rep)
            logger: Logger = Logger.get_instance()
            logger.set_rep(rep_alias)
            logger.record_event(LogAction.OPEN)
            print(f"Abrindo repositório de {rep_alias}")
            reload = play.play()
            if not reload:
                break
        logger.record_event(LogAction.QUIT)
