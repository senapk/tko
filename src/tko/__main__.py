from __future__ import annotations

import argparse
import sys

from .actions import Run, Build
from .run.basic import Param
from .util.pattern import PatternLoader
from .run.basic import DiffMode
from .down import Down
from .settings import SettingsParser, RepoSettings, Settings

from .util.guide import tko_guide
from .util.guide import bash_guide

from .run.report import Report
from .util.term_color import Color
from .util.symbols import symbols

from .game.game import Game
from .play.play import Play

from .__init__ import __version__


class MRep:
    @staticmethod
    def list(_args):
        sp = SettingsParser()
        settings = sp.load_settings()
        print(f"SettingsFile\n- {sp.settings_file}")
        print(str(settings))

    @staticmethod
    def add(args):
        sp = SettingsParser()
        settings = sp.load_settings()
        rep = RepoSettings()
        if args.url:
            rep.set_url(args.url)
        elif args.file:
            rep.set_file(args.file)
        settings.reps[args.alias] = rep
        sp.save_settings()
    
    @staticmethod
    def rm(args):
        sp = SettingsParser()
        settings = sp.load_settings()
        if args.alias in settings.reps:
            settings.reps.pop(args.alias)
            sp.save_settings()
        else:
            print("Repository not found.")

    @staticmethod
    def reset(_args):
        sp = SettingsParser()
        sp.settings = Settings()
        sp.save_settings()

    @staticmethod
    def graph(args):
        sp = SettingsParser()
        settings = sp.load_settings()
        rep = settings.get_repo(args.alias)
        file = rep.get_file()
        game = Game()
        game.parse_file(file)
        game.check_cycle()
        game.generate_graph("graph")


class Main:
    @staticmethod
    def run(args):
        PatternLoader.pattern = args.pattern
        param = Param.Basic().set_index(args.index)
        if args.quiet:
            param.set_diff_mode(DiffMode.QUIET)
        elif args.all:
            param.set_diff_mode(DiffMode.ALL)
        else:
            param.set_diff_mode(DiffMode.FIRST)

        if args.filter:
            param.set_filter(True)
        if args.compact:
            param.set_compact(True)

        # load default diff from settings if not specified
        if not args.side and not args.down:
            local = SettingsParser().load_settings().local
            updown = local.updown
            size_too_short = Report.get_terminal_size() < local.sideto_min
            param.set_up_down(updown or size_too_short)
        elif args.side:
            param.set_up_down(False)
        elif args.down:
            param.set_up_down(True)
        run = Run(args.target_list, args.cmd, param)
        run.execute()

    @staticmethod
    def build(args):
        PatternLoader.pattern = args.pattern
        manip = Param.Manip().set_unlabel(args.unlabel).set_to_sort(args.sort).set_to_number(args.number)
        build = Build(args.target, args.target_list, manip, args.force)
        build.execute()
    
    @staticmethod
    def settings(args):
        sp = SettingsParser()
        settings = sp.load_settings()
        
        action = False

        if args.ascii:
            action = True
            settings.local.ascii = True
            print("Encoding mode now is: ASCII")
        if args.unicode:
            action = True
            settings.local.ascii = False
            print("Encoding mode now is: UNICODE")
        if args.mono:
            action = True
            settings.local.color = False
            print("Color mode now is: MONOCHROMATIC")
        if args.color:
            action = True
            settings.local.color = True
            print("Color mode now is: COLORED")
        if args.side:
            action = True
            settings.local.updown = False
            print("Diff mode now is: SIDE_BY_SIDE")
        if args.down:
            action = True
            settings.local.updown = True
            print("Diff mode now is: UP_DOWN")
        if args.lang:
            action = True
            settings.local.lang = args.lang
            print("Default language extension now is:", args.lang)
        if args.ask:
            action = True
            settings.local.lang = ""
            print("Language extension will be asked always.")
            
        if args.root:
            action = True
            settings.local.set_rootdir(".")
            print("Root directory now is: current directory")

        if not action:
            action = True
            print(sp.get_settings_file())
            print(str(settings.local))

        sp.save_settings()

    @staticmethod
    def play(args):
        if args.repo:
            print("playing repo", args.repo)

            while True:
                sp = SettingsParser()
                settings = sp.load_settings()
                repo = settings.get_repo(args.repo)
                local = settings.local
                game = Game()
                file = repo.get_file()
                game.parse_file(file)

                # passing a lambda function to the play class to save the settings
                ext = ""
                if args.graph:
                    ext = ".svg" if args.svg else ".png"
                play = Play(local, game, repo, args.repo, lambda: sp.save_settings())
                reload = play.play(ext)
                if not reload:
                    break

    @staticmethod
    def down(args):
        Down.download_problem(".", args.course, args.activity, args.language, print)


class Parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='tko', description=f'tko version {__version__}')        
        self.subparsers = self.parser.add_subparsers(title='subcommands', help='help for subcommand.')

        self.parent_manip = None
        self.parent_basic = None

        self.add_parser_global()
        self.add_parent_basic()
        self.add_parent_manip()
        self.add_parser_run()
        self.add_parser_build()
        self.add_parser_down()
        self.add_parser_config()
        self.add_parser_repo()
        self.add_parser_play()

    def add_parser_global(self):
        self.parser.add_argument('-c', metavar='CONFIG_FILE', type=str, help='config json file.')
        self.parser.add_argument('-w', metavar='WIDTH', type=int, help="terminal width.")
        self.parser.add_argument('-v', action='store_true', help='show version.')
        self.parser.add_argument('-g', action='store_true', help='show tko simple guide.')
        self.parser.add_argument('-b', action='store_true', help='show bash simple guide.')
        self.parser.add_argument('-m', action='store_true', help='monochromatic.')
        self.parser.add_argument('-a', action='store_true', help='asc2 mode.')

    def add_parent_basic(self):
        parent_basic = argparse.ArgumentParser(add_help=False)
        parent_basic.add_argument('--index', '-i', metavar="I", type=int, help='run a specific index.')
        parent_basic.add_argument('--pattern', '-p', metavar="P", type=str, default='@.in @.sol',
                                  help='pattern load/save a folder, default: "@.in @.sol"')
        self.parent_basic = parent_basic
    
    def add_parent_manip(self):
        parent_manip = argparse.ArgumentParser(add_help=False)
        parent_manip.add_argument('--width', '-w', type=int, help="term width.")
        parent_manip.add_argument('--unlabel', '-u', action='store_true', help='remove all labels.')
        parent_manip.add_argument('--number', '-n', action='store_true', help='number labels.')
        parent_manip.add_argument('--sort', '-s', action='store_true', help="sort test cases by input size.")
        parent_manip.add_argument('--pattern', '-p', metavar="@.in @.out", type=str, default='@.in @.sol',
                                  help='pattern load/save a folder, default: "@.in @.sol"')
        self.parent_manip = parent_manip

    def add_parser_run(self):
        parser_r = self.subparsers.add_parser('run', parents=[self.parent_basic], help='run with test cases.')
        parser_r.add_argument('target_list', metavar='T', type=str, nargs='*', help='solvers, test cases or folders.')
        parser_r.add_argument('--filter', '-f', action='store_true', help='filter solver in temp dir before run')
        parser_r.add_argument('--compact', '-c', action='store_true', help='Do not show case descriptions in failures')
        parser_r.add_argument("--cmd", type=str, help="bash command to run code")

        group_n = parser_r.add_mutually_exclusive_group()
        group_n.add_argument('--quiet', '-q', action='store_true', help='quiet mode, do not show any failure.')
        group_n.add_argument('--all', '-a', action='store_true', help='show all failures.')

        # add an exclusive group for diff mode
        group = parser_r.add_mutually_exclusive_group()
        group.add_argument('--down', '-d', action='store_true', help="diff mode up-to-down.")
        group.add_argument('--side', '-s', action='store_true', help="diff mode side-by-side.")
        parser_r.set_defaults(func=Main.run)

    def add_parser_build(self):
        parser_b = self.subparsers.add_parser('build', parents=[self.parent_manip], help='build a test target.')
        parser_b.add_argument('target', metavar='T_OUT', type=str, help='target to be build.')
        parser_b.add_argument('target_list', metavar='T', type=str, nargs='+', help='input test targets.')
        parser_b.add_argument('--force', '-f', action='store_true', help='enable overwrite.')
        parser_b.set_defaults(func=Main.build)

    def add_parser_down(self):
        parser_d = self.subparsers.add_parser('down', help='download problem from repository.')
        parser_d.add_argument('course', type=str, nargs='?', help=" [ fup | ed | poo ].")
        parser_d.add_argument('activity', type=str, nargs='?', help="activity @label.")
        parser_d.add_argument('--language', '-l', type=str, nargs='?', help="[ c | cpp | js | ts | py | java ]")
        parser_d.set_defaults(func=Main.down)

    def add_parser_config(self):
        parser_s = self.subparsers.add_parser('config', help='settings tool.')

        g_encoding = parser_s.add_mutually_exclusive_group()
        g_encoding.add_argument('--ascii', action='store_true',    help='set ascii mode.')
        g_encoding.add_argument('--unicode', action='store_true', help='set unicode mode.')

        g_color = parser_s.add_mutually_exclusive_group()
        g_color.add_argument('--color', action='store_true', help='set colored mode.')
        g_color.add_argument('--mono',  action='store_true', help='set mono    mode.')

        g_diff = parser_s.add_mutually_exclusive_group()
        g_diff.add_argument('--side', action='store_true', help='set side_by_side diff mode.')
        g_diff.add_argument('--down', action='store_true', help='set up_to_down   diff mode.')

        g_lang = parser_s.add_mutually_exclusive_group()
        g_lang.add_argument("--lang", '-l', metavar='ext', type=str, help="set default language extension.")
        g_lang.add_argument("--ask", action='store_true', help='ask language extension every time.')
        
        parser_s.add_argument("--root", action='store_true', help='set root directory to current.')

        parser_s.set_defaults(func=Main.settings)

    def add_parser_repo(self):
        parser_repo = self.subparsers.add_parser('rep', help='manipulate repositories.')
        subpar_repo = parser_repo.add_subparsers(title='subcommands', help='help for subcommand.')

        repo_list = subpar_repo.add_parser('list', help='list all repositories')
        repo_list.set_defaults(func=MRep.list)

        repo_add = subpar_repo.add_parser('add', help='add a repository.')
        repo_add.add_argument('alias', metavar='alias', type=str, help='alias of the repository to be added.')
        repo_add.add_argument('--url', '-u', type=str, help='add a repository url to the settings file.')
        repo_add.add_argument('--file', '-f', type=str, help='add a repository file to the settings file.')
        repo_add.set_defaults(func=MRep.add)

        repo_rm = subpar_repo.add_parser('rm', help='remove a repository.')
        repo_rm.add_argument('alias', metavar='alias', type=str, help='alias of the repository to be removed.')
        repo_rm.set_defaults(func=MRep.rm)

        repo_reset = subpar_repo.add_parser('reset', help='reset all repositories to factory default.')
        repo_reset.set_defaults(func=MRep.reset)

        repo_graph = subpar_repo.add_parser('graph', help='generate graph of the repository.')
        repo_graph.add_argument('alias', metavar='alias', type=str, help='alias of the repository to be graphed.')
        repo_graph.set_defaults(func=MRep.graph)

    def add_parser_play(self):
        parser_p = self.subparsers.add_parser('play', help='play a game.')
        parser_p.add_argument('repo', metavar='repo', type=str, help='repository to be played.')
        parser_p.add_argument("--graph", "-g", action='store_true', help='generate graph of the game using graphviz.')
        parser_p.add_argument("--svg", "-s", action='store_true', help='generate graph in svg instead png.')
        parser_p.set_defaults(func=Main.play)

    def main(self):
        args = self.parser.parse_args()

        if len(sys.argv) == 1:
            self.parser.print_help()
            return
        if args.w is not None:
            Report.set_terminal_size(args.width)
        if args.c:
            SettingsParser.user_settings_file = args.c
        settings = SettingsParser().load_settings()
        if args.a or settings.local.ascii:
            symbols.set_ascii()
        else:
            symbols.set_unicode()
        if not args.m and settings.local.color:
            Color.enabled = True
            symbols.set_colors()


        if args.v or args.g or args.b:
            if args.v:
                print("tko version " + __version__)
            if args.b:
                print(bash_guide[1:], end="")
            if args.g:
                print(tko_guide[1:], end="")
        else:
            try:
                if "func" in args:
                    args.func(args)
                else:
                    self.parser.print_help()
            except ValueError as e:
                print(str(e))


def main():
    try:
        parser = Parser()
        parser.main()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nKeyboard Interrupt")
        sys.exit(1)


if __name__ == '__main__':
    main()
