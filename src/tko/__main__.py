from __future__ import annotations

import argparse
import sys

from tko.cmds.cmd_rep import CmdRep
from tko.cmds.cmd_play import CmdPlay
from tko.cmds.cmd_down import CmdDown
from tko.cmds.cmd_run import Run
from tko.cmds.cmd_build import CmdBuild
from tko.cmds.cmd_config import CmdConfig, ConfigParams
from tko.util.logger import LogAction, Logger, LoggerFS
from tko.util.text import AnsiColor

from tko.util.param import Param
from tko.util.pattern import PatternLoader
from tko.util.consts import DiffCount, DiffMode
from .settings.settings import Settings

from tko.util.guide import tko_guide
from tko.util.guide import bash_guide

from tko.util.raw_terminal import RawTerminal
from tko.util.symbols import symbols
from tko.settings.check_version import CheckVersion

from .__init__ import __version__


class Main:
    @staticmethod
    def test(args):
        PatternLoader.pattern = args.pattern
        param = Param.Basic().set_index(args.index)
        if args.quiet:
            param.set_diff_count(DiffCount.QUIET)
        elif args.all:
            param.set_diff_count(DiffCount.ALL)
        else:
            param.set_diff_count(DiffCount.FIRST)

        if args.filter:
            param.set_filter(True)
        if args.compact:
            param.set_compact(True)

        settings = Settings()
        if not args.side and not args.down:
            param.set_diff_mode(settings.app.get_diff_mode())
        elif args.side:
            param.set_diff_mode(DiffMode.SIDE)
        elif args.down:
            param.set_diff_mode(DiffMode.DOWN)
        cmd_run = Run(settings, args.target_list, args.cmd, param)
        cmd_run.execute()

    @staticmethod
    def run(args):
        PatternLoader.pattern = args.pattern
        param = Param.Basic().set_index(args.index)
        settings = Settings()
        param.set_diff_mode(settings.app.get_diff_mode())
        if args.filter:
            param.set_filter(True)
        cmd_run = Run(settings, args.target_list, args.cmd, param)
        cmd_run.set_curses()
        cmd_run.execute()

    @staticmethod
    def build(args):
        PatternLoader.pattern = args.pattern
        manip = Param.Manip().set_unlabel(args.unlabel).set_to_sort(args.sort).set_to_number(args.number)
        build = CmdBuild(args.target, args.target_list, manip, args.force)
        build.execute()

    @staticmethod
    def play(args):
        settings = Settings()
        settings.check_rootdir()
        CmdPlay.execute(args.repo, settings)
        CheckVersion().version_check()

    @staticmethod
    def down(args):
        settings = Settings().check_rootdir()
        CmdDown.execute(args.course, args.activity, args.language, settings, print)

    @staticmethod
    def config(args):
        settings = Settings()
        param = ConfigParams()
        param.side = args.side
        param.down = args.down
        param.lang = args.lang
        param.ask = args.ask
        param.root = args.root
        param.editor = args.editor
        param.borders = args.borders
        param.hud = args.hud

        CmdConfig.execute(settings, param)


class Parser:
    def __init__(self):
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(prog='tko', description=f'tko version {__version__}')
        self.subparsers = self.parser.add_subparsers(title='subcommands', help='help for subcommand.')

        self.parent_manip = self.create_parent_manip()
        self.parent_basic = self.create_parent_basic()

        self.add_parser_global()
        self.create_parent_basic()
        self.create_parent_manip()
        self.add_parser_run()
        self.add_parser_exec()
        self.add_parser_build()
        self.add_parser_down()
        self.add_parser_config()
        self.add_parser_repo()
        self.add_parser_play()

    def add_parser_global(self):
        self.parser.add_argument('-c', metavar='CONFIG_FILE', type=str, help='config json file.')
        self.parser.add_argument('-w', metavar='WIDTH', type=int, help="terminal width.")
        self.parser.add_argument('-v', action='store_true', help='show version.')
        self.parser.add_argument('-m', action='store_true', help='monochromatic.')

    def create_parent_basic(self):
        parent_basic = argparse.ArgumentParser(add_help=False)
        parent_basic.add_argument('--index', '-i', metavar="I", type=int, help='run a specific index.')
        parent_basic.add_argument('--pattern', '-p', metavar="P", type=str, default='@.in @.sol',
                                  help='pattern load/save a folder, default: "@.in @.sol"')
        return parent_basic

    def create_parent_manip(self):
        parent_manip = argparse.ArgumentParser(add_help=False)
        parent_manip.add_argument('--width', '-w', type=int, help="term width.")
        parent_manip.add_argument('--unlabel', '-u', action='store_true', help='remove all labels.')
        parent_manip.add_argument('--number', '-n', action='store_true', help='number labels.')
        parent_manip.add_argument('--sort', '-s', action='store_true', help="sort test cases by input size.")
        parent_manip.add_argument('--pattern', '-p', metavar="@.in @.out", type=str, default='@.in @.sol',
                                  help='pattern load/save a folder, default: "@.in @.sol"')
        return parent_manip

    def add_parser_run(self):
        parser_r = self.subparsers.add_parser('run', parents=[self.parent_basic], help='run with test cases using curses.')
        parser_r.add_argument('target_list', metavar='T', type=str, nargs='*', help='solvers, test cases or folders.')
        parser_r.add_argument('--filter', '-f', action='store_true', help='filter solver in temp dir before run')
        parser_r.add_argument("--cmd", type=str, help="bash command to run code")
        parser_r.set_defaults(func=Main.run)

    def add_parser_exec(self):
        parser_r = self.subparsers.add_parser('test', parents=[self.parent_basic], help='run with test cases.')
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
        parser_r.set_defaults(func=Main.test)

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

        g_diff = parser_s.add_mutually_exclusive_group()
        g_diff.add_argument('--side', action='store_true', help='set side_by_side diff mode.')
        g_diff.add_argument('--down', action='store_true', help='set up_to_down   diff mode.')

        g_lang = parser_s.add_mutually_exclusive_group()
        g_lang.add_argument("--lang", '-l', metavar='ext', type=str, help="set default language extension.")
        g_lang.add_argument("--ask", action='store_true', help='ask language extension every time.')

        parser_s.add_argument("--root", metavar="path", type=str, help='set root directory.')
        parser_s.add_argument("--editor", metavar="cmd", type=str, help='set editor command.')
        parser_s.add_argument("--borders", metavar="0or1", type=str, help='enable borders.')
        parser_s.add_argument("--hud", metavar="0or1", type=str, help='enable hud.')

        parser_s.set_defaults(func=Main.config)

    def add_parser_repo(self):
        parser_repo = self.subparsers.add_parser('rep', help='manipulate repositories.')
        subpar_repo = parser_repo.add_subparsers(title='subcommands', help='help for subcommand.')

        repo_list = subpar_repo.add_parser('list', help='list all repositories')
        repo_list.set_defaults(func=CmdRep.list)

        repo_add = subpar_repo.add_parser('add', help='add a repository.')
        repo_add.add_argument('alias', metavar='alias', type=str, help='alias of the repository to be added.')
        repo_add.add_argument('--url', '-u', type=str, help='add a repository url to the settings file.')
        repo_add.add_argument('--file', '-f', type=str, help='add a repository file to the settings file.')
        repo_add.set_defaults(func=CmdRep.add)

        repo_rm = subpar_repo.add_parser('rm', help='remove a repository.')
        repo_rm.add_argument('alias', metavar='alias', type=str, help='alias of the repository to be removed.')
        repo_rm.set_defaults(func=CmdRep.rm)

        repo_reset = subpar_repo.add_parser('reset', help='reset all repositories to factory default.')
        repo_reset.set_defaults(func=CmdRep.reset)

        repo_graph = subpar_repo.add_parser('graph', help='generate graph of the repository.')
        repo_graph.add_argument('alias', metavar='alias', type=str, help='alias of the repository to be graphed.')
        repo_graph.set_defaults(func=CmdRep.graph)

        repo_log = subpar_repo.add_parser("check", help="validates log of the repository.")
        repo_log.add_argument('alias', metavar='alias', type=str, help='alias of the repository to be log.')
        repo_log.set_defaults(func=CmdRep.check)

    def add_parser_play(self):
        parser_p = self.subparsers.add_parser('play', help='play a game.')
        parser_p.add_argument('repo', metavar='repo', type=str, nargs="?", default="__ask", help='repository to be played.')
        # parser_p.add_argument("--graph", "-g", action='store_true', help='generate graph of the game using graphviz.')
        # parser_p.add_argument("--svg", "-s", action='store_true', help='generate graph in svg instead png.')
        parser_p.set_defaults(func=Main.play)


def exec(parser: argparse.ArgumentParser, args):
    settings = Settings()
    if args.w is not None:
        RawTerminal.set_terminal_size(args.w)
    if args.c:
        settings.set_settings_file(args.c)
    settings.load_settings()
    Logger.instance = Logger(LoggerFS(settings))

    if args.m:
        AnsiColor.enabled = False
    else:
        AnsiColor.enabled = True
        symbols.set_colors()

    if args.v:
        if args.v:
            print("tko version " + __version__)
    else:
        if "func" in args:
            args.func(args)
        else:
            parser.print_help()

def main():
    try:
        parser = Parser().parser
        args = parser.parse_args()
        exec(parser, args)
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nKeyboard Interrupt")
        sys.exit(1)
    except Warning as w:
        print(w)
        sys.exit(1)
    # except Exception as e:
    #     print(e)
    #     sys.exit(1)

# NÃO RETIRE ESSA TAG POR CAUSA DO MERGE DO REPLIT
if __name__ == '__main__': # MERGE_INSERT 
    main()
