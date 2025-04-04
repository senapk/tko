from __future__ import annotations

import argparse
import sys

from tko.cmds.cmd_rep import CmdRep
from tko.cmds.cmd_open import CmdOpen
from tko.cmds.cmd_down import CmdLineDown
from tko.cmds.cmd_run import Run
from tko.cmds.cmd_build import CmdBuild
from tko.cmds.cmd_config import CmdConfig, ConfigParams
from tko.settings.logger import Logger
from tko.util.text import AnsiColor

from tko.util.param import Param
from tko.util.pattern import PatternLoader
from tko.util.consts import DiffCount, DiffMode
from tko.settings.settings import Settings

from tko.settings.repository import Repository
from tko.util.raw_terminal import RawTerminal
from tko.util.symbols import symbols
from tko.settings.check_version import CheckVersion
from tko.settings.repository_starter import RepStarter

import os

from tko.__init__ import __version__


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
        cmd_run = Run(settings, args.target_list, param)
        cmd_run.execute()

    @staticmethod
    def run(args):
        PatternLoader.pattern = args.pattern
        param = Param.Basic().set_index(args.index)
        settings = Settings()
        param.set_diff_mode(settings.app.get_diff_mode())
        if args.filter:
            param.set_filter(True)
        cmd_run = Run(settings, args.target_list, param)
        cmd_run.set_curses()
        cmd_run.execute()

    @staticmethod
    def build(args):
        PatternLoader.pattern = args.pattern
        manip = Param.Manip().set_unlabel(args.unlabel).set_to_sort(args.sort).set_to_number(args.number)
        build = CmdBuild(args.target, args.target_list, manip)
        build.execute()

    @staticmethod
    def open(args):
        settings = Settings()
        folder = args.folder
        rec_folder = Repository.rec_search_for_repo(folder)
        if rec_folder != "":
            folder = rec_folder
        action = CmdOpen(settings).load_folder(folder)
        if not CheckVersion().is_updated():
            action.set_need_update()
        action.execute()

    @staticmethod
    def down(args):
        settings = Settings()
        folder = args.folder
        rec_folder = Repository.rec_search_for_repo(folder)
        if rec_folder != "":
            folder = rec_folder
        CmdLineDown(settings, folder, args.key).execute()

    @staticmethod
    def init(args):
        remote: str | None = args.remote
        source: str | None = args.source
        folder: str | None = args.folder
        RepStarter(remote=remote, source=source, folder=folder)


    @staticmethod
    def config(args):
        settings = Settings()
        param = ConfigParams()
        param.side = args.side
        param.down = args.down
        param.images = args.images
        param.editor = args.editor
        param.borders = args.borders
        param.timeout = args.timeout
        CmdConfig.execute(settings, param)

    @staticmethod
    def list(_args):
        settings = Settings()
        print(str(settings))


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
        self.add_parser_config()
        self.add_parser_rep_tools()
        self.add_parser_rep_actions()


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
        parser_r = self.subparsers.add_parser('run', parents=[self.parent_basic], help='Run with test cases using curses.')
        parser_r.add_argument('target_list', metavar='T', type=str, nargs='*', help='solvers, test cases or folders.')
        parser_r.add_argument('--filter', '-f', action='store_true', help='filter solver in temp dir before run')
        parser_r.set_defaults(func=Main.run)

    def add_parser_exec(self):
        parser_r = self.subparsers.add_parser('test', parents=[self.parent_basic], help='Run with test cases using raw terminal.')
        parser_r.add_argument('target_list', metavar='T', type=str, nargs='*', help='solvers, test cases or folders.')
        parser_r.add_argument('--filter', '-f', action='store_true', help='filter solver in temp dir before run')
        parser_r.add_argument('--compact', '-c', action='store_true', help='Do not show case descriptions in failures')

        group_n = parser_r.add_mutually_exclusive_group()
        group_n.add_argument('--quiet', '-q', action='store_true', help='quiet mode, do not show any failure.')
        group_n.add_argument('--all', '-a', action='store_true', help='show all failures.')

        # add an exclusive group for diff mode
        group = parser_r.add_mutually_exclusive_group()
        group.add_argument('--down', '-d', action='store_true', help="diff mode up-to-down.")
        group.add_argument('--side', '-s', action='store_true', help="diff mode side-by-side.")
        parser_r.set_defaults(func=Main.test)

    def add_parser_build(self):
        parser_b = self.subparsers.add_parser('build', parents=[self.parent_manip], help='Build a test target.')
        parser_b.add_argument('target', metavar='T_OUT', type=str, help='target to be build.')
        parser_b.add_argument('target_list', metavar='T', type=str, nargs='+', help='input test targets.')
        parser_b.set_defaults(func=Main.build)

    # def add_parser_down(self):
    #     parser_d = self.subparsers.add_parser('down', help='download problem from repository.')
    #     parser_d.add_argument('course', type=str, nargs='?', help=" [ fup | ed | poo ].")
    #     parser_d.add_argument('activity', type=str, nargs='?', help="activity @label.")
    #     parser_d.add_argument('--language', '-l', type=str, nargs='?', help="[ c | cpp | js | ts | py | java ]")
    #     parser_d.set_defaults(func=Main.down)

    def add_parser_config(self):
        parser_cfg = self.subparsers.add_parser('config', help='Settings tool.')
        subpar_repo = parser_cfg.add_subparsers(title='subcommands', help='help for subcommand.')

        cfg_reset = subpar_repo.add_parser('reset', help='reset all repositories, folders and values to factory default.')
        cfg_reset.set_defaults(func=CmdRep.reset)

        cfg_set = subpar_repo.add_parser('set', help='set default config values.')

        g_diff = cfg_set.add_mutually_exclusive_group()
        g_diff.add_argument('--side', action='store_true', help='set side_by_side diff mode.')
        g_diff.add_argument('--down', action='store_true', help='set up_to_down   diff mode.')

        cfg_set.add_argument("--editor", metavar="cmd", type=str, help='set editor command.')
        cfg_set.add_argument("--borders", metavar="[0|1]", type=str, help='enable borders.')
        cfg_set.add_argument("--images", metavar="[0|1]", type=str, help='enable images.')
        cfg_set.add_argument("--timeout", metavar="sec", type=int, help='set timeout.')

        cfg_set.set_defaults(func=Main.config)

        cfg_list = subpar_repo.add_parser('list', help='list default config values.')
        cfg_list.set_defaults(func=Main.list)


    def add_parser_rep_tools(self):

        parser_repo = self.subparsers.add_parser('rep', help='Repository validation tools.')

        subpar_repo = parser_repo.add_subparsers(title='subcommands', help='help for subcommand.')
        repo_log = subpar_repo.add_parser("check", help="validates log of the repository.")
        repo_log.add_argument('folder', type=str, help='folder to be checked.')
        repo_log.set_defaults(func=CmdRep.check)

        repo_resume = subpar_repo.add_parser("resume", help="resume log of the repository.")
        repo_resume.add_argument('folder', type=str, help='folder to be checked.')
        repo_resume.set_defaults(func=CmdRep.resume)

        repo_resume = subpar_repo.add_parser("graph", help="resume log of the repository.")
        repo_resume.add_argument('folder', type=str, help='folder to be checked.')
        repo_resume.set_defaults(func=CmdRep.graph)



    def add_parser_rep_actions(self):
        parser_open = self.subparsers.add_parser('open', help='Open a folder with a repository.')
        parser_open.add_argument('folder', type=str, nargs='?', default='.', help='repository folder.')
        parser_open.set_defaults(func=Main.open)

        parser_down = self.subparsers.add_parser('down', help='Down a task from a repository.')
        parser_down.add_argument('folder', type=str, nargs='?', default='.', help='repository folder.')
        parser_down.add_argument('key', type=str, nargs='?', default='.', help='task key.')
        parser_down.set_defaults(func=Main.down)

        parser_init = self.subparsers.add_parser('init', help='Initialize a repository in a folder.')
        source = parser_init.add_mutually_exclusive_group()
        source.add_argument('--remote', '-r', type=str, help='remote source [fup|ed|poo].')
        source.add_argument('--source', '-s', type=str, help='http url or local file.')
        parser_init.add_argument('--folder', '-f', type=str, help='local directory.')
        parser_init.set_defaults(func=Main.init)


def exec(parser: argparse.ArgumentParser, args):
    settings = Settings()
    if args.w is not None:
        RawTerminal.set_terminal_size(args.w)
    if args.c:
        settings.set_settings_file(args.c)
    settings.load_settings()
    Logger.instance = Logger()

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
        print("")
        print(w)
        sys.exit(1)
    # except Exception as e:
    #     print(e)
    #     sys.exit(1)

# NÃO RETIRE ESSA TAG POR CAUSA DO MERGE DO REPLIT
if __name__ == '__main__': # MERGE_INSERT 
    main()
