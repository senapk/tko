from __future__ import annotations

import argparse
import sys

from .actions import Actions
from .basic import Param
from .pattern import PatternLoader
from .basic import DiffMode
from .format import Report, Colored
from .down import Down
from .settings import SettingsParser
from .guide import tko_guide
from .guide import bash_guide
from .format import symbols
from .__init__ import __version__


class Main:

    @staticmethod
    def run(args):
        PatternLoader.pattern = args.pattern
        param = Param.Basic().set_index(args.index)
        if args.quiet:
            param.set_diff_mode(DiffMode.QUIET)
        elif args.first:
            param.set_diff_mode(DiffMode.FIRST)
        elif args.all:
            param.set_diff_mode(DiffMode.ALL)


        # load default diff from settings if not specified
        if not args.sideby and not args.updown:
            param.set_up_down(not SettingsParser().get_hdiff())
        elif args.sideby:
            param.set_up_down(False)
        elif args.updown:
            param.set_up_down(True)
        Actions.run(args.target_list, param)

    @staticmethod
    def build(args):
        PatternLoader.pattern = args.pattern
        manip = Param.Manip().set_unlabel(args.unlabel).set_to_sort(args.sort).set_to_number(args.number)
        Actions.build(args.target, args.target_list, manip, args.force)
    
    @staticmethod
    def settings(args):
        sp = SettingsParser()
        print("Settings file at " + sp.get_settings_file())

        if (args.color):
            SettingsParser().toggle_color()
        if (args.encoding):
           SettingsParser().toggle_ascii()
        if (args.diff):
            SettingsParser().toggle_hdiff()

        print("COLORMODE: " + ("COLORED" if sp.get_color() else "MONO"))
        print("DIFF MODE: " + ("SIDE_BY_SIDE" if sp.get_hdiff() else "UP_DOWN"))
        print("ENCODING : " + ("ASCII" if sp.get_ascii() else "UNICODE"))

        



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
        destiny = Down.create_problem_folder(args.disc, args.index, args.extension)
        Down.entry_unpack(destiny, args.disc, args.index, args.extension)

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
        parser.add_argument('-c', metavar='CONFIG_FILE', type=str, help='config file.')
        parser.add_argument('-w', metavar='WIDTH', type=int, help="terminal width.")
        parser.add_argument('-v', action='store_true', help='show version.')
        parser.add_argument('-g', action='store_true', help='show tko simple guide.')
        parser.add_argument('-b', action='store_true', help='show bash simple guide.')
        parser.add_argument('-m', action='store_true', help='monochromatic.')
        
        subparsers = parser.add_subparsers(title='subcommands', help='help for subcommand.')

        # run
        parser_r = subparsers.add_parser('run', parents=[parent_basic], help='run with test cases.')
        parser_r.add_argument('target_list', metavar='T', type=str, nargs='*', help='solvers, test cases or folders.')
        
        group_n = parser_r.add_mutually_exclusive_group()
        group_n.add_argument('--first', '-f', action='store_true', help='(default) show only first failure.')
        group_n.add_argument('--quiet', '-q', action='store_true', help='quiet mode, do not show any failure.')
        group_n.add_argument('--all', '-a', action='store_true', help='show all failures.')

        # add a exclusive group for diff mode
        group = parser_r.add_mutually_exclusive_group()
        group.add_argument('--updown', '-u', action='store_true', help="diff mode up-to-down.")
        group.add_argument('--sideby', '-s', action='store_true', help="diff mode sidebyside.")
        parser_r.set_defaults(func=Main.run)

        # build
        parser_b = subparsers.add_parser('build', parents=[parent_manip], help='build a test target.')
        parser_b.add_argument('target', metavar='T_OUT', type=str, help='target to be build.')
        parser_b.add_argument('target_list', metavar='T', type=str, nargs='+', help='input test targets.')
        parser_b.add_argument('--force', '-f', action='store_true', help='enable overwrite.')
        parser_b.set_defaults(func=Main.build)

        # down
        parser_d = subparsers.add_parser('down', help='download problem from repository.')
        parser_d.add_argument('disc', type=str, nargs='?', help=" [ fup | ed | poo ].")
        parser_d.add_argument('index', type=str, nargs='?', help="3 digits label like 021.")
        parser_d.add_argument('extension', type=str, nargs='?', default="-", help="[ c | cpp | js | ts | py | java ]")
        parser_d.set_defaults(func=Main.down)

        # settings
        parser_s = subparsers.add_parser('config', help='settings tool.')
        parser_s.add_argument('--encoding', '-e', action='store_true', help='toggle [ascii | unicode] mode.')
        parser_s.add_argument('--color', '-c', action='store_true', help='toggle [colored | mono] mode.')
        parser_s.add_argument('--diff', '-d', action='store_true', help='toggle [side_by_side | up_down] mode.')
        parser_s.set_defaults(func=Main.settings)

        args = parser.parse_args()

        if len(sys.argv) == 1:
            parser.print_help()
            return


        # setting general settings options
        if args.w is not None:
            Report.set_terminal_size(args.width)

        if args.c:
            SettingsParser().set_settings_file(args.config)
        
        if SettingsParser().get_ascii():
            symbols.set_ascii()
        else:
            symbols.set_unicode()

        if not args.m and SettingsParser().get_color():
            Colored.enabled = True
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
