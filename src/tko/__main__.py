from __future__ import annotations

import argparse
import sys
from icecream import ic # type: ignore

from tko.feno.build import build_main
from tko.feno.indexer import indexer_main
from tko.feno.html import html_main
from tko.feno.mdpp import mdpp_main
from tko.feno.older import older_main
from tko.feno.remote_md import remote_main
from tko.feno.filter import filter_main
from tko.feno.grading import Grading

from tko.cmds.cmd_task import CmdTask
from tko.cmds.cmd_rep import CmdRep
from tko.cmds.cmd_open import CmdOpen
from tko.cmds.cmd_down import CmdLineDown
from tko.cmds.cmd_run import Run
from tko.cmds.cmd_build import CmdBuild
from tko.cmds.cmd_config import CmdConfig, ConfigParams
from tko.enums.diff_mode import DiffMode
from tko.util.text import AnsiColor
from tko.enums.diff_count import DiffCount

from tko.util.param import Param
from tko.util.pattern_loader import PatternLoader

from tko.settings.settings import Settings
from tko.cmds.cmd_diff import cmd_diff

from tko.settings.repository import Repository
from tko.settings.rep_paths import RepPaths
from tko.util.raw_terminal import RawTerminal
from tko.util.symbols import symbols
from tko.settings.check_version import CheckVersion
from tko.settings.rep_starter import RepStarter
from tko.settings.rep_source_actions import RepSourceActions

from tko.__init__ import __version__


class Main:

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
        update: bool = args.update
        cache_folder: str | None = args.cache
        folder = args.folder
        rec_folder = RepPaths.rec_search_for_repo(folder)
        if rec_folder != "":
            folder = rec_folder
        action = CmdOpen(settings, update, cache_folder).load_folder(folder)
        if not CheckVersion(settings).is_updated():
            action.set_need_update()
        action.execute()

    @staticmethod
    def collect_task(args: argparse.Namespace):
        settings = Settings()
        folder = args.folder
        rec_folder = RepPaths.rec_search_for_repo(folder)
        if rec_folder != "":
            folder = rec_folder
        rep = Repository(folder)
        width: int  = args.graph[0]
        height: int  = args.graph[1]
        CmdTask.show_graph(settings, rep, args.label, width, height)

    @staticmethod
    def init(args: argparse.Namespace):
        folder: str | None = args.folder
        language: str | None = args.language
        rep_starter = RepStarter(folder=folder, language=language)
        ok: bool = rep_starter.execute()
        remote: str | None = args.git
        enable: list[str] | None = args.enable
        if ok and remote is not None:
            rep_actions = RepSourceActions(folder)
            rep_actions.add_source(alias=remote, default_repo_aliases=remote, clone_url=None, filters=enable, local_source_folder=None, writeable=False)
        rep_starter.print_end_msg()

    @staticmethod
    def source_list(args: argparse.Namespace):
        folder: str | None = args.folder
        try:
            RepSourceActions(folder)
            rep_actions = RepSourceActions(folder)
            rep_actions.list_sources()
        except ValueError as e:
            print(f"Erro ao listar fontes: {e}")

    @staticmethod
    def source_del(args: argparse.Namespace):
        alias: str = args.alias
        folder: str | None = args.folder
        try:
            RepSourceActions(folder)
            rep_actions = RepSourceActions(folder)
            rep_actions.del_source(alias=alias)
        except ValueError as e:
            print(f"Erro ao deletar fonte: {e}")

    @staticmethod
    def source_add(args: argparse.Namespace):
        default_git_alias: str | None = args.git
        git_clone: str | None = args.clone
        git_branch: str = args.branch
        local_source: str | None = args.local
        writeable: bool = args.writeable

        rep_folder: str | None = args.folder
        
        alias: str = args.alias
        enable: list[str] | None = args.enable
        try:
            rep_actions = RepSourceActions(rep_folder)
            rep_actions.add_source(alias=alias, default_repo_aliases=default_git_alias, branch=git_branch, clone_url=git_clone, local_source_folder=local_source, filters=enable, writeable=writeable)
            rep_actions.print_end_msg()
        except ValueError as e:
            print(f"Erro ao adicionar fonte: {e}")

    @staticmethod
    def source_enable(args: argparse.Namespace):
        alias: str = args.alias
        folder: str | None = args.folder
        enable: list[str] | None = args.enable
        rep_actions = RepSourceActions(folder)
        rep_actions.source_enable(alias=alias, filters=enable)

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
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(prog='tko',
                                                                       description=f'tko version {__version__}')
        self.subparsers = self.parser.add_subparsers(title='subcommands', help='help for subcommand.')

        self.parent_manip = Parser.create_parent_manip()
        self.parent_basic = Parser.create_parent_basic()
        self.parent_folder = Parser.create_parent_folder()

        self.add_parser_global()
        self.create_parent_basic()
        self.create_parent_manip()
        self.add_parser_rep_actions()
        self.add_parser_run()
        self.add_parser_config()
        self.add_parser_collect()
        self.add_parser_build()
        # self.add_parser_eval()

    def add_parser_global(self):
        self.parser.add_argument('-c', metavar='CONFIG_FILE', type=str, help='Config json file.')
        self.parser.add_argument('-w', metavar='WIDTH', type=int, help="Terminal width.")
        self.parser.add_argument('-v', action='store_true', help='Show version.')
        self.parser.add_argument('-m', action='store_true', help='Monochromatic.')
        self.parser.add_argument('--debug', '-D', action='store_true', help='Debug mode.')

    @staticmethod
    def create_parent_basic():
        parent_basic = argparse.ArgumentParser(add_help=False)
        parent_basic.add_argument('--index', '-i', metavar="I", type=int, help='Run a specific index.')
        parent_basic.add_argument('--pattern', '-p', metavar="P", type=str, default='@.in @.sol',
                                  help='Pattern load/save a folder, default: "@.in @.sol"')
        return parent_basic

    @staticmethod
    def create_parent_folder():
        parent_folder = argparse.ArgumentParser(add_help=False)
        parent_folder.add_argument('--folder', '-f', type=str, nargs='?', default='.', help='Repository folder.')
        return parent_folder

    @staticmethod
    def create_parent_manip():
        parent_manip = argparse.ArgumentParser(add_help=False)
        parent_manip.add_argument('--width', '-w', type=int, help="Terminal width.")
        parent_manip.add_argument('--unlabel', '-u', action='store_true', help='Remove all labels.')
        parent_manip.add_argument('--number', '-n', action='store_true', help='Number labels.')
        parent_manip.add_argument('--sort', '-s', action='store_true', help="Sort test cases by input size.")
        parent_manip.add_argument('--pattern', '-p', metavar="@.in @.out", type=str, default='@.in @.sol',
                                  help='Pattern load/save a folder, default: "@.in @.sol"')
        return parent_manip

    def add_parser_run(self):
        parser = self.subparsers.add_parser('run', parents=[self.parent_basic], help='Run task in raw terminal or tui.')
        parser.add_argument('target_list', metavar='T', type=str, nargs='*', help='Solvers, test cases or folders.')
        parser.add_argument('--filter', '-f', action='store_true', help='Filter solver in temp dir before run')

        group_a = parser.add_mutually_exclusive_group()

        group_a.add_argument("--tui", '-t', action='store_true', help='Use TUI interface.')
        group_a.add_argument('--eval', action='store_true', help='Get percent running tests.')

        parser.add_argument('--compact', '-c', action='store_true', help='Do not show case descriptions in failures.')

        group_n = parser.add_mutually_exclusive_group()
        group_n.add_argument('--none', '-n', action='store_true', help='Do not show any failure.')
        group_n.add_argument('--all', '-a', action='store_true', help='Show all failures.')

        # add an exclusive group for diff mode
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--down', '-d', action='store_true', help="Diff mode up-to-down.")
        group.add_argument('--side', '-s', action='store_true', help="Diff mode side-by-side.")
        parser.set_defaults(func=Main.run)

    def add_parser_config(self):
        parser_cfg = self.subparsers.add_parser('config', help='Global config tool.')
        subpar_repo = parser_cfg.add_subparsers(title='subcommands', help='Help for subcommand.')

        cfg_reset = subpar_repo.add_parser('reset',
                                           help='Reset all repositories, folders and values to factory default.')
        cfg_reset.set_defaults(func=CmdRep.reset)

        cfg_set = subpar_repo.add_parser('set', help='Set default config values.')

        g_diff = cfg_set.add_mutually_exclusive_group()
        g_diff.add_argument('--side', action='store_true', help='Set side_by_side diff mode.')
        g_diff.add_argument('--down', action='store_true', help='Set up_to_down   diff mode.')

        cfg_set.add_argument("--editor", metavar="cmd", type=str, help='Set editor command.')
        cfg_set.add_argument("--borders", metavar="[0|1]", type=str, help='Enable borders.')
        cfg_set.add_argument("--images", metavar="[0|1]", type=str, help='Enable images.')
        cfg_set.add_argument("--timeout", metavar="sec", type=int, help='Set timeout.')

        cfg_set.set_defaults(func=Main.config)

        cfg_list = subpar_repo.add_parser('list', help='list default config values.')
        cfg_list.set_defaults(func=Main.list)

    def add_parser_collect(self):
        parser_repo = self.subparsers.add_parser('collect', help='Tools to collect data.')
        subpar_collect = parser_repo.add_subparsers(title='subcommands', help='Help for subcommand.')

        # repo_update = subpar_repo.add_parser("update", parents=[self.parent_folder], help="Update repository cache.")
        # repo_update.set_defaults(func=CmdRep.update)

        parser_task = subpar_collect.add_parser('task', parents=[self.parent_folder], help='Collect data from task.')
        parser_task.add_argument('label', type=str, help='Task label.')
        parser_task.add_argument('graph', nargs=2, type=int, metavar=('WIDTH', 'HEIGHT'), help="Show task graph.")
        parser_task.set_defaults(func=Main.collect_task)

        repo_collect = subpar_collect.add_parser("rep", parents=[self.parent_folder], help="Collect data from repository.")
        repo_collect.add_argument("--json", action='store_true', help="Collect as json data")
        repo_collect.add_argument("--resume", action='store_true', help="Collect resume")
        repo_collect.add_argument("--log", action='store_true', help="Collect history log")
        repo_collect.add_argument('--game', action='store_true', help="Collect game info")
        repo_collect.add_argument('--daily', action='store_true', help="Daily graph")
        repo_collect.add_argument('--width', type=int, default=100, help="Daily graph width")
        repo_collect.add_argument('--height', type=int, default=10, help="Daily graph height")
        repo_collect.add_argument('--color', type=int, default=1, help="Daily graph color [0|1]")
        repo_collect.set_defaults(func=CmdRep.collect_main)

        extract_cmd = subpar_collect.add_parser("batch", help="Extract problems data from this reps.")
        extract_cmd.add_argument("--reps", "-r", required=True, type=str, nargs="+", help="Reps to extract data from.")
        extract_cmd.add_argument("--json", "-j", type=str, help="Path to save the extracted JSON data.")
        extract_cmd.add_argument("--csv", "-c", type=str, help="Path to save the extracted CSV data.")
        extract_cmd.add_argument("--block_prefix", "-b", type=str, help="Block prefix to insert in csv file.")
        extract_cmd.set_defaults(func=CmdRep.collect_batch)

    def add_parser_rep_actions(self):
        parser_open = self.subparsers.add_parser('open', help='Open a folder with a repository.')
        parser_open.add_argument('folder', type=str, nargs='?', default='.', help='Repository folder.')
        parser_open.add_argument('--cache', '-c', type=str, help='Cache folder.')
        parser_open.add_argument('--update', '-u', action='store_true', help='Force update.')
        parser_open.set_defaults(func=Main.open)

        parser_init = self.subparsers.add_parser('init', parents=[self.parent_folder], help='Initialize a empty repository in a folder.')
        parser_init.add_argument('--language', '-l', type=str, metavar=('EXTENSION'), help='Draft language for the repository.')
        parser_init.add_argument('--git', '-g', '-r', type=str, metavar=('ALIAS '), help='Init with remote git source [fup|ed|poo].')
        parser_init.add_argument('--enable', '-e', type=str, nargs='*', help='Only show enabled items')
        parser_init.set_defaults(func=Main.init)

        parser_source = self.subparsers.add_parser('source', help='Manipulate sources in a repository folder.')
        sub_source = parser_source.add_subparsers(title='source commands', help='help for subcommand.')
        # create subcommands inside source
        source_add = sub_source.add_parser("add", parents=[self.parent_folder], help="Add a new task source")
        source_add.add_argument('--alias', "-a", required=True, type=str, help='Alias for the remote.')
        source_from = source_add.add_mutually_exclusive_group(required=True)
        source_from.add_argument('--git', '-g', type=str, metavar=('ALIAS'), help='Clone one of the default remote git sources [fup|ed|poo].')
        source_from.add_argument('--clone', '-c', type=str, metavar=('REPO_URL'), help='Clone a git rep with a Readme.md source. Ex: tko source add ed --clone https://github.com/qxcodeed/arcade.git')
        source_from.add_argument('--local', '-l', type=str, metavar=('FOLDER'), help='Add a local folder as a source.')
        source_add.add_argument('--enable', '-e', metavar=('SUBSTRING'), type=str, nargs='*', help='Only show enabled items')
        source_add.add_argument('--branch', '-b', type=str, default='master', help='Branch name for clone source.')
        source_add.add_argument('--writeable', '-w', action='store_true', help='Set source as writeable, allowing modifications.')
        source_add.set_defaults(func=Main.source_add)

        source_list = sub_source.add_parser("list", parents=[self.parent_folder], help="List tko repository sources")
        source_list.set_defaults(func=Main.source_list)

        source_del = sub_source.add_parser("del", parents=[self.parent_folder], help="Delete a tko repository source")
        source_del.add_argument('--alias', required=True, type=str, help='Alias for the remote.')
        source_del.set_defaults(func=Main.source_del)

        source_enable = sub_source.add_parser("enable", parents=[self.parent_folder], help="Enable filters on a tko repository source.")
        source_enable.add_argument('--alias', type=str, required=True, help='Alias for the remote.')
        source_enable.add_argument('enable', type=str, nargs='*', help='Only show enabled items')
        source_enable.set_defaults(func=Main.source_enable)

    def add_parser_build(self):
        parser_build = self.subparsers.add_parser('build', help='Tools to build tko reps.')
        subparsers = parser_build.add_subparsers(title='subcommands', help='Help for subcommand.')

        parser_b = subparsers.add_parser('tests', parents=[self.parent_manip], help='Build a test target.')
        parser_b.add_argument('target', metavar='T_OUT', type=str, help='Target to be built.')
        parser_b.add_argument('target_list', metavar='T', type=str, nargs='+', help='Input test targets.')
        parser_b.set_defaults(func=Main.build)

        # subparser for the 'build' command
        parser_r = subparsers.add_parser('mapi', help='Build .mapi file.')
        parser_r.add_argument('targets', metavar='T', type=str, nargs='*', help='folders')
        parser_r.add_argument("--check", "-c", action="store_true", help="Check if the file needs to be rebuilt")
        parser_r.add_argument("--brief", "-b", action="store_true", help="Brief mode")
        # parser_r.add_argument("--pandoc", "-p", action="store_true", help="Use pandoc rather than python markdown")
        parser_r.add_argument("--remote", "-r", action="store_true", help="Search for remote.cfg file and create absolute links")
        parser_r.add_argument("--erase", "-e", action="store_true", help="Erase .md and .tio temp files")
        parser_r.add_argument("--debug", "-d", action='store_true', help="Display debug msgs")
        parser_r.set_defaults(func=build_main)

        # subparser for the 'indexer' command
        parser_i = subparsers.add_parser('indexer', help='Index Readme file.')
        parser_i.add_argument('path', type=str, help='Path to Markdown file')
        parser_i.add_argument("base", type=str, help="Folder with the problems")
        parser_i.set_defaults(func=indexer_main)

        # subparser for the 'html' command
        parser_h = subparsers.add_parser('html', help='Generate HTML file from markdown file.')
        parser_h.add_argument('input', type=str, help='Input markdown file')
        parser_h.add_argument('output', type=str, help='Output HTML file')
        parser_h.add_argument('--title', type=str, default="Problema", help='Title of the HTML file')
        parser_h.set_defaults(func=html_main)

        # subparser for the 'mdpp' command
        parser_m = subparsers.add_parser('mdpp', help='Preprocessor for markdown files.')
        parser_m.add_argument('targets', metavar='T', type=str, nargs='*', help='Readmes or folders')
        parser_m.add_argument('--quiet', '-q', action="store_true", help='quiet mode')
        parser_m.add_argument('--clean', '-c', action="store_true", help='clean mode')
        parser_m.set_defaults(func=mdpp_main)

        # subparser for the 'older' command
        parser_o = subparsers.add_parser('older', help='Check if the source is newer than the target')
        parser_o.add_argument('targets', type=str, nargs='+', help='Target files or directories')
        parser_o.set_defaults(func=older_main)

        parser_diff = subparsers.add_parser('diff', help='Show diff for 2 inputs or files.')
        exclusive_group_target = parser_diff.add_mutually_exclusive_group(required=True)
        exclusive_group_target.add_argument('--path', '-f', action='store_true', help='Targets are paths.')
        exclusive_group_target.add_argument('--text', '-t', action='store_true', help='Compare two texts.')
        parser_diff.add_argument('target_a', type=str, help='First target to be compared.')
        parser_diff.add_argument('target_b', type=str, help='Second target to be compared.')
        exclusive_group = parser_diff.add_mutually_exclusive_group()
        exclusive_group.add_argument('--side', '-s', action='store_true', help="Diff mode side-by-side.")
        exclusive_group.add_argument('--down', '-d', action='store_true', help="Diff mode up-to-down.")
        parser_diff.set_defaults(func=Main.diff)

        # subparser for the 'remote' command
        parser_rm = subparsers.add_parser('remote', help='Create remote markdown file.')
        parser_rm.add_argument('target', type=str, help='Folders')
        parser_rm.add_argument('--output', '-o', type=str, help='Output file')
        parser_rm.set_defaults(func=remote_main)

        # subparser for the 'filter' command
        parser_f = subparsers.add_parser('filter', help='Filter code removing answers.')

        parser_f.add_argument('target', type=str, help='file or folder to process')
        parser_f.add_argument('-u', '--update', action="store_true", help='update source file')
        parser_f.add_argument('-c', '--cheat', action="store_true", help='recursive cheat mode cleaning comments on students files')
        parser_f.add_argument('-o', '--output', type=str, help='output target')
        parser_f.add_argument("-r", "--recursive", action="store_true", help="recursive mode")
        parser_f.add_argument("-f", "--force", action="store_true", help="force mode")
        parser_f.add_argument("-q", "--quiet", action="store_true", help="quiet mode")
        parser_f.add_argument("-i", "--indent", type=int, default=0, help="indent using spaces")
        parser_f.set_defaults(func=filter_main)

        parser_grading = subparsers.add_parser('grading', help='Grade the tests.')

        parser_grading.add_argument("--output", "-o", type=str, help="Output file for the awarded grade.")
        grading_exclusive = parser_grading.add_mutually_exclusive_group(required=True)
        grading_exclusive.add_argument("--config", "-c", type=str, help="Path to the configuration file.")
        grading_exclusive.add_argument("--readme", "-r", type=str, help="Path to the README file for questions")
        parser_grading.set_defaults(func=Grading.main)


def execute(parser: argparse.ArgumentParser, args: argparse.Namespace) -> int:
    settings = Settings()
    if args.w is not None:
        RawTerminal.set_terminal_size(args.w)
    if args.c:
        settings.set_settings_file(args.c)
    settings.load_settings()

    if args.m:
        AnsiColor.enabled = False
    else:
        AnsiColor.enabled = True
        symbols.set_colors()

    if args.debug:
        ic.configureOutput(includeContext=True, outputFunction=print)
        ic.enable()
        ic("Debug mode enabled")
    else:
        ic.disable()

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
        print(w)
        sys.exit(1)
    # except Exception as e:
    #     print(e)
    #     sys.exit(1)


# NÃO RETIRE ESSA TAG POR CAUSA DO MERGE DO REPLIT
if __name__ == '__main__':  # MERGE_INSERT
    main()
