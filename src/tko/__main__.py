from __future__ import annotations

import argparse
import sys

from .actions import Run, Build
from .basic import Param
from .pattern import PatternLoader
from .basic import DiffMode
from .format import Report, Color
from .down import Down
from .settings import SettingsParser, RepoSettings, Settings
from .guide import tko_guide
from .guide import bash_guide
from .format import symbols
from .game import Game, Play
from .__init__ import __version__


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
        if not args.sideby and not args.updown:
            local = SettingsParser().load_settings().local
            updown = local.updown
            size_too_short = Report.get_terminal_size() < local.sideto_min
            param.set_up_down(updown or size_too_short)
        elif args.sideby:
            param.set_up_down(False)
        elif args.updown:
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
        
        if args.ascii:
            settings.local.ascii = True
            print("Encoding mode now is: ASCII")
        if args.unicode:
            settings.local.ascii = False
            print("Encoding mode now is: UNICODE")
        if args.mono:
            settings.local.color = False
            print("Color mode now is: MONOCHROMATIC")
        if args.color:
            settings.local.color = True
            print("Color mode now is: COLORED")
        if args.side:
            settings.local.updown = False
            print("Diff mode now is: SIDE_BY_SIDE")
        if args.updown:
            settings.local.updown = True
            print("Diff mode now is: UP_DOWN")
        if args.lang:
            settings.local.lang = args.lang
            print("Default language extension now is:", args.lang)
        if args.ask:
            settings.local.lang = "ask"
            print("Language extension will be asked always.")
        if args.show:
            print(SettingsParser.get_settings_file())
            print(str(settings.local))
        sp.save_settings()

    @staticmethod
    def repo(args):
        sp = SettingsParser()
        settings = sp.load_settings()

        if args.list:
            print("listing all repositories")
            for rep in settings.reps:
                value = settings.reps[rep]
                print(f"{rep}: ", end="")
                if value.url != "":
                    print(f"url: {settings.reps[rep].url}")
                else:
                    print(f"file: {settings.reps[rep].file}")
        if args.add:
            print("adding repo", args.add)
            if args.url:
                print("url", args.url)
                rep = RepoSettings().set_url(args.url)
                settings.reps[args.add] = rep
                sp.save_settings()
            elif args.file:
                print("file", args.file)
                rep = RepoSettings().set_file(args.file)
                print(str(rep))
                settings.reps[args.add] = rep
                sp.save_settings()
            else:
                print("no url or file selected as source for the repository.")
        if args.rm:
            print("removing repo", args.rm)
            settings.reps.pop(args.rm)
        if args.graph:
            print("generating graph.puml", args.graph)
            rep = settings.reps[args.graph]
            file = rep.get_file()
            game = Game()
            game.parse_file(file)
            game.check_cycle()
            game.generate_graph("graph")
        if args.reset:
            print("resetting all repositories to factory default.")
            sp.settings = Settings()
            sp.save_settings()

    @staticmethod
    def play(args):
        if args.repo:
            print("playing repo", args.repo)
            sp = SettingsParser()
            settings = sp.load_settings()
            repo = settings.reps[args.repo]
            game = Game()
            file = repo.get_file()
            game.parse_file(file)
            #passsing a lambda function to the play class to save the settings
            play = Play(game, repo, lambda: sp.save_settings())
            play.play()
            


    # @staticmethod
    # def rebuild(args):
    #     if args.width is not None:
    #         Report.set_terminal_size(args.width)
    #     PatternLoader.pattern = args.pattern
    #     manip = Param.Manip().set_unlabel(args.unlabel).set_to_sort(args.sort).set_to_number(args.number)
    #     Actions.update(args.target_list, manip, args.cmd)
    #     return 0

    # @staticmethod
    # def update(_args):
    #     Down.update()

    @staticmethod
    def down(args):
        Down.entry_unpack(args.course, args.activity, args.language)

    @staticmethod
    def main():
        parent_basic = argparse.ArgumentParser(add_help=False)
        parent_basic.add_argument('--index', '-i', metavar="I", type=int, help='run a specific index.')
        parent_basic.add_argument('--pattern', '-p', metavar="P", type=str, default='@.in @.sol',
                                  help='pattern load/save a folder, default: "@.in @.sol"')

        parent_manip = argparse.ArgumentParser(add_help=False)
        parent_manip.add_argument('--width', '-w', type=int, help="term width.")
        parent_manip.add_argument('--unlabel', '-u', action='store_true', help='remove all labels.')
        parent_manip.add_argument('--number', '-n', action='store_true', help='number labels.')
        parent_manip.add_argument('--sort', '-s', action='store_true', help="sort test cases by input size.")
        parent_manip.add_argument('--pattern', '-p', metavar="@.in @.out", type=str, default='@.in @.sol',
                                  help='pattern load/save a folder, default: "@.in @.sol"')

        parser = argparse.ArgumentParser(prog='tko', description='A tool for competitive programming.')
        parser.add_argument('-c', metavar='CONFIG_FILE', type=str, help='config json file.')
        parser.add_argument('-w', metavar='WIDTH', type=int, help="terminal width.")
        parser.add_argument('-v', action='store_true', help='show version.')
        parser.add_argument('-g', action='store_true', help='show tko simple guide.')
        parser.add_argument('-b', action='store_true', help='show bash simple guide.')
        parser.add_argument('-m', action='store_true', help='monochromatic.')
        
        subparsers = parser.add_subparsers(title='subcommands', help='help for subcommand.')

        # run
        parser_r = subparsers.add_parser('run', parents=[parent_basic], help='run with test cases.')
        parser_r.add_argument('target_list', metavar='T', type=str, nargs='*', help='solvers, test cases or folders.')
        parser_r.add_argument('--filter', '-f', action='store_true', help='filter solver in temp dir before run')
        parser_r.add_argument('--compact', '-c', action='store_true', help='Dont show case descriptions in failures')
        parser_r.add_argument("--cmd", type=str, help="bash command to run code")

        group_n = parser_r.add_mutually_exclusive_group()
        group_n.add_argument('--quiet', '-q', action='store_true', help='quiet mode, do not show any failure.')
        group_n.add_argument('--all', '-a', action='store_true', help='show all failures.')

        # add a exclusive group for diff mode
        group = parser_r.add_mutually_exclusive_group()
        group.add_argument('--updown', '-u', action='store_true', help="diff mode up-to-down.")
        group.add_argument('--sideby', '-s', action='store_true', help="diff mode side-by-side.")
        parser_r.set_defaults(func=Main.run)

        # build
        parser_b = subparsers.add_parser('build', parents=[parent_manip], help='build a test target.')
        parser_b.add_argument('target', metavar='T_OUT', type=str, help='target to be build.')
        parser_b.add_argument('target_list', metavar='T', type=str, nargs='+', help='input test targets.')
        parser_b.add_argument('--force', '-f', action='store_true', help='enable overwrite.')
        parser_b.set_defaults(func=Main.build)

        # down
        parser_d = subparsers.add_parser('down', help='download problem from repository.')
        parser_d.add_argument('course', type=str, nargs='?', help=" [ fup | ed | poo ].")
        parser_d.add_argument('activity', type=str, nargs='?', help="activity @label.")
        parser_d.add_argument('--language', '-l', type=str, nargs='?', help="[ c | cpp | js | ts | py | java ]")
        parser_d.set_defaults(func=Main.down)

        # settings
        parser_s = subparsers.add_parser('config', help='settings tool.')
        parser_s.add_argument('--show',  '-s', action='store_true', help='show current settings.')

        g_encoding = parser_s.add_mutually_exclusive_group()
        g_encoding.add_argument('--ascii', action='store_true',    help='set ascii mode.')
        g_encoding.add_argument('--unicode', action='store_true', help='set unicode mode.')

        g_color = parser_s.add_mutually_exclusive_group()
        g_color.add_argument('--color', action='store_true', help='set colored mode.')
        g_color.add_argument('--mono',  action='store_true', help='set mono    mode.')
        

        g_diff = parser_s.add_mutually_exclusive_group()
        g_diff.add_argument('--side', action='store_true', help='set side_by_side diff mode.')
        g_diff.add_argument('--updown', action='store_true', help='set up_to_down   diff mode.')


        g_lang = parser_s.add_mutually_exclusive_group()
        g_lang.add_argument("--lang", '-l', metavar='ext', type=str, help="set default language extension.")
        g_lang.add_argument("--ask", action='store_true', help='ask language extension every time.')

        parser_repo = subparsers.add_parser('repo', help='manipulate repositories.')
        repo_actions = parser_repo.add_mutually_exclusive_group()
        repo_actions.add_argument("--list", action='store_true', help="list all repositories.")
        repo_actions.add_argument("--add",  metavar='repo', type=str, help="alias of the repository to be added.")
        repo_actions.add_argument("--rm", metavar='repo', type=str, help="alias of the repository to be removed.")
        repo_actions.add_argument("--reset", action='store_true', help="reset all repositories to factory default.")
        repo_actions.add_argument("--graph", '-g', metavar='repo', type=str, help="generate graph of the repository.")
        
        init_source = parser_repo.add_mutually_exclusive_group()
        init_source.add_argument("--url", type=str, help="add a repository url to the settings file.")
        init_source.add_argument("--file", type=str, help="add a repository file to the settings file.")

        parser_repo.set_defaults(func=Main.repo)

        parser_play = subparsers.add_parser('play', help='play a repository.')
        parser_play.add_argument('repo', metavar='T', type=str, help='repository to be played.')
        parser_play.set_defaults(func=Main.play)

        parser_s.set_defaults(func=Main.settings)

        args = parser.parse_args()

        if len(sys.argv) == 1:
            parser.print_help()
            return

        # setting general settings options
        if args.w is not None:
            Report.set_terminal_size(args.width)

        if args.c:
            SettingsParser.set_settings_file(args.c)
        
        settings = SettingsParser().load_settings()

        if settings.local.ascii:
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
                args.func(args)
            except ValueError as e:
                print(str(e))


if __name__ == '__main__':
    try:
        Main.main()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nKeyboard Interrupt")
        sys.exit(1)
