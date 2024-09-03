from tko.settings.settings import Settings
from tko.game.game import Game
from tko.settings.rep_settings import RepSource
from tko.play.play import Play
from typing import Dict
import os

class CmdPlay:
    @staticmethod
    def execute(rep_alias: str, settings: Settings, graph: bool, svg: bool):
        while True:
            rep_alias = settings.check_rep_alias(rep_alias)
            rep_source: RepSource = settings.get_rep_source(rep_alias)
            rep_data = settings.get_rep_data(rep_alias)

            game = Game()
            file = rep_source.get_file(os.path.join(settings.app._rootdir, rep_alias))
            game.parse_file(file)

            # passing a lambda function to the play class to save the settings
            ext = ""
            if graph:
                ext = ".svg" if svg else ".png"
            play = Play(settings=settings, game=game, rep_data=rep_data, rep_alias=rep_alias)
            print(f"Abrindo repositório de {rep_alias}")
            reload = play.play(ext)
            if not reload:
                break
