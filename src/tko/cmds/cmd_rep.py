from tko.game.game import Game
from tko.game.graph import Graph
from tko.settings.rep_settings import RepSource
from tko.settings.settings import Settings

import os

class CmdRep:
    @staticmethod
    def list(_args):
        settings = Settings()
        print(f"SettingsFile\n- {settings.settings_file}")
        print(str(settings))

    @staticmethod
    def add(args):
        settings = Settings()
        rep = RepSource()
        if args.url:
            rep.set_url(args.url)
        elif args.file:
            rep.set_file(args.file)
        settings.reps[args.alias] = rep
        settings.save_settings()

    @staticmethod
    def rm(args):
        sp = Settings()
        if args.alias in sp.reps:
            sp.reps.pop(args.alias)
            sp.save_settings()
        else:
            print("Repository not found.")

    @staticmethod
    def reset(_):
        sp = Settings().reset()
        print(sp.settings_file)
        print(sp.app._rootdir)
        sp.save_settings()

    @staticmethod
    def graph(args):
        settings = Settings()
        rep_source:RepSource = settings.get_rep_source(args.alias)
        file = rep_source.get_file(os.path.join(settings.app._rootdir, args.alias))
        game = Game()
        game.parse_file(file)
        game.check_cycle()
        Graph(game).generate()