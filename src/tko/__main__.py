from __future__ import annotations

import argparse
import sys

from tko.cmds.cmd_rep import CmdRep
from tko.cmds.cmd_eval import CmdEval
from tko.cmds.cmd_open import CmdOpen
from tko.cmds.cmd_down import CmdLineDown
from tko.cmds.cmd_run import Run
from tko.cmds.cmd_build import CmdBuild
from tko.cmds.cmd_config import CmdConfig, ConfigParams
from tko.enums.diff_mode import DiffMode
from tko.settings.logger import Logger
from tko.util.text import AnsiColor
from tko.enums.diff_count import DiffCount

from tko.util.param import Param
from tko.util.pattern_loader import PatternLoader

from tko.settings.settings import Settings
from tko.cmds.cmd_diff import cmd_diff


from tko.settings.repository import Repository
from tko.util.raw_terminal import RawTerminal
from tko.util.symbols import symbols
from tko.settings.check_version import CheckVersion
from tko.settings.repository_starter import RepStarter

from tko.__init__ import __version__


class Main:
    @staticmethod
    def eval(args: argparse.Namespace) -> int:
        PatternLoader.pattern = args.pattern
        cmd = CmdEval()
        cmd.set_target_list(args.target_list)
        cmd.set_norun(args.norun)
        cmd.set_track(args.track)
        cmd.set_self(args.self)
        cmd.set_complex(args.complex)
        cmd.set_timeout(args.timeout)
        cmd.set_result_file(args.result_file)
        return cmd.execute()

    @staticmethod
    def run(args: argparse.Namespace) -> None:
        if args.tui:
            Main.tui(args)
            return
        
        PatternLoader.pattern = args.pattern
        param = Param.Basic().set_index(args.index)
        if args.none:
            param.set_diff_count(DiffCount.NONE)
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
        if args.eval:
            cmd_run.show_track_info().show_self_info()

        cmd_run.execute()

    @staticmethod
    def tui(args: argparse.Namespace) -> None:
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
    def build(args: argparse.Namespace):
        PatternLoader.pattern = args.pattern
        manip = Param.Manip().set_unlabel(args.unlabel).set_to_sort(args.sort).set_to_number(args.number)
        build = CmdBuild(args.target, args.target_list, manip)
        build.execute()

    @staticmethod
    def diff(args: argparse.Namespace):
        cmd_diff(args)

    @staticmethod
    def open(args: argparse.Namespace):
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
    def down(args: argparse.Namespace):
        settings = Settings()
        folder = args.folder
        print("Folder: ", folder)
        rec_folder = Repository.rec_search_for_repo(folder)
        if rec_folder != "":
            folder = rec_folder
        CmdLineDown(settings, folder, args.label).execute()

    @staticmethod
    def init(args: argparse.Namespace):
        remote: str | None = args.remote
        source: str | None = args.source
        folder: str | None = args.folder
        language: str | None = args.language
        database: str | None = args.database
        RepStarter(remote=remote, source=source, folder=folder, language=language, database=database)


    @staticmethod
    def config(args: argparse.Namespace):
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
    def list(_: argparse.Namespace):
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
        self.add_parser_tui()
        self.add_parser_run()
        self.add_parser_build()
        self.add_parser_config()
        self.add_parser_rep_tools()
        self.add_parser_rep_actions()
        self.add_parser_diff()
        self.add_parser_eval()


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

    def add_parser_tui(self):
        parser_r = self.subparsers.add_parser('tui', parents=[self.parent_basic], help='Run using Terminal User Interface.')
        parser_r.add_argument('target_list', metavar='T', type=str, nargs='*', help='solvers, test cases or folders.')
        parser_r.add_argument('--filter', '-f', action='store_true', help='filter solver in temp dir before run')
        parser_r.set_defaults(func=Main.tui)

    def add_parser_run(self):
        parser = self.subparsers.add_parser('run', parents=[self.parent_basic], help='Run using raw terminal.')
        parser.add_argument('target_list', metavar='T', type=str, nargs='*', help='solvers, test cases or folders.')
        parser.add_argument('--filter', '-f', action='store_true', help='filter solver in temp dir before run')

        group_a = parser.add_mutually_exclusive_group()

        group_a.add_argument("--tui", '-t', action='store_true', help='use TUI interface.')
        group_a.add_argument('--eval', action='store_true', help='Get percent running testes')       

        parser.add_argument('--compact', '-c', action='store_true', help='Do not show case descriptions in failures')

        group_n = parser.add_mutually_exclusive_group()
        group_n.add_argument('--none', '-n', action='store_true', help='do not show any failure.')
        group_n.add_argument('--all', '-a', action='store_true', help='show all failures.')

        # add an exclusive group for diff mode
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--down', '-d', action='store_true', help="diff mode up-to-down.")
        group.add_argument('--side', '-s', action='store_true', help="diff mode side-by-side.")
        parser.set_defaults(func=Main.run)

    def add_parser_eval(self):
        parser = self.subparsers.add_parser('eval', parents=[self.parent_basic], help='Evaluate test cases or collect data.')
        parser.add_argument('target_list', metavar='T', type=str, nargs='*', help='solvers, test cases or folders.')
        parser.add_argument('--norun', '-n', action='store_true', help='Not calc coverage percent by running testes')
        parser.add_argument('--self', '-s', action='store_true', help='Display coverage, approach, autonomy, howClear, howFun, howEasy')
        parser.add_argument('--track', '-t', action='store_true', help='Display attemps, lines, elapsed')
        parser.add_argument('--complex', '-c', action='store_true', help='Final Percent combines coverage, approach and autonomy')
        parser.add_argument('--timeout', type=int, help='Set timeout in seconds for each test case.')
        parser.add_argument('--result_file', '-r', type=str, help='Save percent result in result_file.')
        parser.set_defaults(func=Main.eval)

    def add_parser_build(self):
        parser_b = self.subparsers.add_parser('build', parents=[self.parent_manip], help='Build a test target.')
        parser_b.add_argument('target', metavar='T_OUT', type=str, help='target to be build.')
        parser_b.add_argument('target_list', metavar='T', type=str, nargs='+', help='input test targets.')
        parser_b.set_defaults(func=Main.build)

    def add_parser_diff(self):

        parser_b = self.subparsers.add_parser('diff', help='Build a test target.')
        exclusive_group_target = parser_b.add_mutually_exclusive_group(required=True)
        exclusive_group_target.add_argument('--path', '-f', action='store_true', help='targets are paths.')
        exclusive_group_target.add_argument('--text', '-t', action='store_true', help='compare two texts.')
        parser_b.add_argument('target_a', type=str, help='first  target to be compared.')
        parser_b.add_argument('target_b', type=str, help='second target to be compared.')
        exclusive_group = parser_b.add_mutually_exclusive_group()
        exclusive_group.add_argument('--side', '-s', action='store_true', help="diff mode side-by-side.")
        exclusive_group.add_argument('--down', '-d', action='store_true', help="diff mode up-to-down.")
        parser_b.set_defaults(func=Main.diff)

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
        parser_down.add_argument('folder', type=str, help='repository folder.')
        parser_down.add_argument('label', type=str, help='task label.')
        parser_down.set_defaults(func=Main.down)

        parser_init = self.subparsers.add_parser('init', help='Initialize a repository in a folder.')
        source = parser_init.add_mutually_exclusive_group()
        source.add_argument('--remote', '-r', type=str, help='remote source [fup|ed|poo].')
        source.add_argument('--source', '-s', type=str, help='http url or local file.')
        parser_init.add_argument('--folder', '-f', type=str, help='local directory.')
        parser_init.add_argument('--language', '-l', type=str, help='draft language for the repository.')
        parser_init.add_argument('--database', '-d', type=str, help='define database folder.')
        parser_init.set_defaults(func=Main.init)


def execute(parser: argparse.ArgumentParser, args: argparse.Namespace) -> int:
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
            return 0
    else:
        if "func" in args:
            code = args.func(args)
            return code if code is not None else 0
        else:
            parser.print_help()
    return 0

def main():
    try:
        parser = Parser().parser
        args = parser.parse_args()
        execute(parser, args)
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
