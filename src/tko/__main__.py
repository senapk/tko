from __future__ import annotations

import argparse
import sys


from .actions import Actions
from .basic import Param
from .pattern import PatternLoader
from .basic import DiffMode
from .format import Report
from .down import Down
from .settings import SettingsParser
from .guide import simple_guide
from .__init__ import __version__


class Main:
    @staticmethod
    def execute(args):
        Actions.exec(args.target_list)

    @staticmethod
    def run(args):
        if args.width is not None:
            Report.set_terminal_size(args.width)
        PatternLoader.pattern = args.pattern
        param = Param.Basic().set_index(args.index)
        if args.quiet:
            param.set_diff_mode(DiffMode.QUIET)
        if args.vertical:
            param.set_up_down(True)
        Actions.run(args.target_list, param)

    @staticmethod
    def list(args):
        if args.width is not None:
            Report.set_terminal_size(args.width)
        PatternLoader.pattern = args.pattern
        param = Param.Basic().set_index(args.index)
        Actions.list(args.target_list, param)

    @staticmethod
    def build(args):
        if args.width is not None:
            Report.set_terminal_size(args.width)
        PatternLoader.pattern = args.pattern
        manip = Param.Manip().set_unlabel(args.unlabel).set_to_sort(args.sort).set_to_number(args.number)
        Actions.build(args.target, args.target_list, manip, args.force)
    
    @staticmethod
    def settings(args):
        print("settings file at " + SettingsParser().get_settings_file())
        if (args.ascii):
            SettingsParser().toggle_ascii()
            print("Initializing symbols... in " + ("ASCII" if SettingsParser().get_ascii() else "UTF-8"))

    # @staticmethod
    # def rebuild(args):
    #     if args.width is not None:
    #         Report.set_terminal_size(args.width)
    #     PatternLoader.pattern = args.pattern
    #     manip = Param.Manip().set_unlabel(args.unlabel).set_to_sort(args.sort).set_to_number(args.number)
    #     Actions.update(args.target_list, manip, args.cmd)
    #     return 0

    @staticmethod
    def update(_args):
        Down.update()

    @staticmethod
    def down(args):
        destiny = Down.create_problem_folder(args.disc, args.index, args.extension)
        Down.entry_unpack(destiny, args.disc, args.index, args.extension)

    @staticmethod
    def main():
        parent_basic = argparse.ArgumentParser(add_help=False)
        parent_basic.add_argument('--width', '-w', type=int, help="term width")
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
        parser.add_argument('-v', '--version', action='store_true', help='show version.')
        parser.add_argument('-g', '--guide', action='store_true', help='show simple guide.')
        parser.add_argument('-c', '--config', type=str, help='config file.')
        
        subparsers = parser.add_subparsers(title='subcommands', help='help for subcommand.')

        # list
        parser_l = subparsers.add_parser('list', parents=[parent_basic], help='show test entries.')
        parser_l.add_argument('target_list', metavar='T', type=str, nargs='*', help='targets.')
        parser_l.set_defaults(func=Main.list)

        # exec
        parser_e = subparsers.add_parser('exec', parents=[parent_basic], help='run without test.')
        parser_e.add_argument('target_list', metavar='T', type=str, nargs='*', help='target.')
        parser_e.set_defaults(func=Main.execute)

        # run
        parser_r = subparsers.add_parser('run', parents=[parent_basic], help='run with test cases.')
        parser_r.add_argument('target_list', metavar='T', type=str, nargs='*', help='solvers, test cases or folders.')
        parser_r.add_argument('--vertical', '-v', action='store_true', help="use vertical mode.")
        parser_r.add_argument('--quiet', '-q', action='store_true', help='quiet mode, do not show diffs')
        parser_r.set_defaults(func=Main.run)

        # build
        parser_b = subparsers.add_parser('build', parents=[parent_manip], help='build a test target.')
        parser_b.add_argument('target', metavar='T_OUT', type=str, help='target to be build.')
        parser_b.add_argument('target_list', metavar='T', type=str, nargs='+', help='input test targets.')
        parser_b.add_argument('--force', '-f', action='store_true', help='enable overwrite.')
        parser_b.set_defaults(func=Main.build)

        # down
        parser_d = subparsers.add_parser('down', help='download problem from repository.')
        parser_d.add_argument('disc', type=str, help=" [ fup | ed | poo ]")
        parser_d.add_argument('index', type=str, help="3 digits label like 021")
        parser_d.add_argument('extension', type=str, nargs='?', default="-", help="[ c | cpp | js | ts | py | java ]")
        parser_d.set_defaults(func=Main.down)

        # update
        parser_u = subparsers.add_parser('update', help='update problem from repository.')
        parser_u.set_defaults(func=Main.update)

        # settings
        parser_s = subparsers.add_parser('settings', help='settings tool.')
        parser_s.add_argument('--ascii', '-a', action='store_true', help='toggle ascii mode.')
        parser_s.set_defaults(func=Main.settings)

        args = parser.parse_args()

        if args.config:
            SettingsParser().set_settings_file(args.config)

        if len(sys.argv) == 1:
            print("You must call a subcommand. Use --help for more information.")
        elif args.version:
            print("tko version " + __version__)
        elif args.guide:
            print(simple_guide)
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
