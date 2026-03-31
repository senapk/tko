from __future__ import annotations

import argparse
from pathlib import Path
import sys
from icecream import ic # type: ignore

from tko.feno.build import build_main
from tko.feno.indexer import indexer_main
from tko.feno.html import html_main
from tko.feno.mdpp import mdpp_main
from tko.feno.older import older_main
from tko.feno.remote_md import remote_main
from tko.feno.filter import filter_main, build_drafts_main

from tko.cmds.cmd_task import CmdTask
from tko.cmds.cmd_collect import CmdCollect
from tko.cmds.cmd_open import CmdOpen
from tko.cmds.cmd_run import Run
from tko.cmds.cmd_build import CmdBuild
from tko.cmds.cmd_config import CmdConfig, ConfigParams
from tko.enums.diff_mode import DiffMode
from tko.util.text import AnsiColor
from tko.enums.diff_count import DiffCount
from tko.mico.pull import pull_all_parallel_main

from tko.util.param import Param
from tko.util.pattern_loader import PatternLoader

from tko.settings.settings import Settings
from tko.cmds.cmd_diff import cmd_diff

from tko.settings.repository import Repository
from tko.settings.rep_paths import RepPaths
from tko.util.raw_terminal import RawTerminal
from tko.settings.check_version import CheckVersion
from tko.settings.rep_starter import RepStarter
from tko.settings.rep_source_actions import RepSourceActions
from tko.util.rtext import RenderConfig, RenderMode
from tko.__init__ import __version__


class Main:

    @staticmethod
    def load_repo(dir_path: Path, show_warnings: bool = True, auto_load: bool = True, global_cache: bool = False) -> tuple[Repository | None, Path | None]:
        if global_cache:
            RepPaths.use_global_cache_folder = True
            print(f"Usando cache global em: {RepPaths('').get_cache_folder()}")
        dir_parent = RepPaths.rec_search_for_repo_parents(dir_path)
        if dir_parent is not None:
            repo = Repository(dir_parent, recursive_search=False)
            if auto_load:
                repo.load_config().load_game()
            return repo, dir_parent

        if show_warnings:
            print("Nenhum repositório TKO encontrado.")
        return None, None

    @staticmethod
    def run(args: argparse.Namespace) -> None:
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

        settings = Settings(args.globaldir)
        if not args.side and not args.down:
            param.set_diff_mode(settings.app.diff_mode)
        elif args.side:
            param.set_diff_mode(DiffMode.SIDE)
        elif args.down:
            param.set_diff_mode(DiffMode.DOWN)
        cmd_run = Run(settings, args.target_list, param)
        if args.eval:
            cmd_run.show_track_info().show_self_info()

        cmd_run.execute()

    @staticmethod
    def task_list(args: argparse.Namespace) -> None:
        settings = Settings(args.globaldir)
        repo, _ = Main.load_repo(args.changedir, show_warnings=True, auto_load=True, global_cache=args.global_cache)
        if repo is None:
            return
        action = CmdOpen(settings, repo, args.update)
        # if not CheckVersion(settings).is_updated():
        #     action.display_need_update()
        action.list(show_all = args.all)

    @staticmethod
    def task_open(args: argparse.Namespace) -> None:
        PatternLoader.pattern = args.pattern
        param = Param.Basic().set_index(args.index)
        settings = Settings(args.globaldir)
        param.set_diff_mode(settings.app.diff_mode)
        if args.filter:
            param.set_filter(True)
        cmd_run = Run(settings, args.target_list, param)
        cmd_run.set_curses()
        cmd_run.execute()

    @staticmethod
    def build(args: argparse.Namespace):
        settings = Settings(args.globaldir)
        PatternLoader.pattern = args.pattern
        manip = Param.Manip().set_unlabel(args.unlabel).set_to_sort(args.sort).set_to_number(args.number)
        build = CmdBuild(Path(args.target), [Path(x) for x in args.target_list], manip, settings)
        build.execute()

    @staticmethod
    def diff(args: argparse.Namespace):
        cmd_diff(args)

    @staticmethod
    def open(args: argparse.Namespace):
        settings = Settings(args.globaldir)
        settings = Settings(args.globaldir)
        repo, _ = Main.load_repo(args.changedir, show_warnings=True, auto_load=True, global_cache=args.global_cache)
        if repo is None:
            return
        action = CmdOpen(settings, repo, args.update)
        if not args.offline:
            if not CheckVersion(settings).is_updated():
                action.display_need_update()
        action.execute()

    @staticmethod
    def collect_task(args: argparse.Namespace):
        settings = Settings(args.globaldir)
        repo, _ = Main.load_repo(args.changedir)
        if repo is None:
            return
        width: int  = args.graph[0]
        height: int  = args.graph[1]
        CmdTask.show_graph(settings, repo, args.label, width, height)

    @staticmethod
    def init(args: argparse.Namespace):
        settings = Settings(args.globaldir)
        changedir: Path | None = args.changedir
        language: str | None = args.language
        rep_starter = RepStarter(settings=settings, folder=changedir, language=language)
        rep_starter.execute()

    @staticmethod
    def remote_lists(args: argparse.Namespace):
        settings = Settings(args.globaldir)
        repo, _ = Main.load_repo(args.changedir)
        if repo is None:
            return
        rep_actions = RepSourceActions(settings, repo)
        rep_actions.remote_list()


    @staticmethod
    def remote_rm(args: argparse.Namespace):
        name: str = args.name
        settings = Settings(args.globaldir)
        repo, _ = Main.load_repo(args.changedir)
        if repo is None:
            return
        rep_actions = RepSourceActions(settings, repo)
        rep_actions.remote_rm(alias=name)


    @staticmethod
    def remote_add(args: argparse.Namespace):
        target: str = args.target
        default_git_alias: str | None = None
        git_repository_url: str | None = None
        local_source_dir: str | None = None

        if target.startswith("@"):
            default_git_alias = target[1:]
        elif target.startswith("http:") or target.startswith("https:") or target.startswith("ssh:"):
            git_repository_url = target
        else:
            local_source_dir = target

        git_branch: str = args.branch
        writeable: bool = args.write
        name: str = args.name
        quest_filter: list[str] | None = args.quest
        task_filter: list[str] | None = args.task
        try:
            settings = Settings(args.globaldir)
            repo, _ = Main.load_repo(args.changedir)
            if repo is None:
                return
            rep_actions = RepSourceActions(settings, repo)
            rep_actions.remote_add(
                name=name, 
                remote_default=default_git_alias, 
                branch=git_branch, 
                remote_url=git_repository_url, 
                remote_dir=local_source_dir, 
                filter_quest=quest_filter, 
                filter_task=task_filter,
                filter_to=args.destiny,
                writeable=writeable)
            rep_actions.print_end_msg()
        except ValueError as e:
            print(f"Erro ao adicionar fonte: {e}")

    @staticmethod
    def remote_filter(args: argparse.Namespace):
        name: str = args.name
        quests: list[str] | None = args.quest
        tasks: list[str] | None = args.task
        clear: bool = args.clear
        if clear and (quests or tasks):
            print("Erro: --clear não pode ser usado com --quest ou --task")
            return
        settings = Settings(args.globaldir)
        repo, _ = Main.load_repo(args.changedir)
        if repo is None:
            return
        rep_actions = RepSourceActions(settings, repo)
        rep_actions.remote_filter(alias=name, filter_quest=quests, filter_task=tasks, clear=clear, filter_to=args.destiny)

    @staticmethod
    def clear_cache(args: argparse.Namespace):
        repo, _ = Main.load_repo(args.changedir)
        if repo is None:
            print("Nenhum repositório TKO encontrado.")
            return
        repo.cache.clear_cache()

    @staticmethod
    def reset_config(args: argparse.Namespace):
        sp = Settings(args.globaldir).reset().save_settings()
        print(sp.get_settings_file())

    @staticmethod
    def reset_languages(args: argparse.Namespace):
        sp = Settings(args.globaldir)
        sp.get_languages_settings().reset().save_file_settings()
        print(sp.get_languages_file())

    @staticmethod
    def config(args: argparse.Namespace):
        settings = Settings(args.globaldir)
        param = ConfigParams()
        param.side = args.side
        param.down = args.down
        param.images = args.images
        param.editor = args.editor
        param.borders = args.borders
        param.timeout = args.timeout
        CmdConfig.execute(settings, param)

    @staticmethod
    def list(args: argparse.Namespace):
        settings = Settings(args.globaldir)
        print(str(settings))

class Parser:
    def __init__(self):
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(prog='tko',
                                                                       description=f'tko {__version__}', add_help=False)
        
        self.parser.add_argument( "-h", "--help", action="help", help="Show help message and exit" )
        self.subparsers = self.parser.add_subparsers(title='subcommands', metavar='COMMAND', help='DESCRIPTION')

        self.parent_manip = Parser.create_parent_manip()
        self.parent_basic = Parser.create_parent_basic()

        self.add_parser_global()
        self.create_parent_basic()
        self.create_parent_manip()
        self.add_parser_rep_actions()
        self.add_parser_task()
        self.add_parser_config()
        self.add_parser_reset()
        self.add_parser_collect()
        self.add_parser_run()
        self.add_parser_build()
        self.add_parser_class()

    def add_parser_global(self):
        self.parser.add_argument('-G', '--globaldir', metavar='DIR', type=Path, help='Global config directory')
        self.parser.add_argument('-C', '--changedir', metavar='DIR', type=Path, default=Path('.'), help='Repository directory')
        self.parser.add_argument('-w', '--width', metavar='WIDTH', type=int, help="Terminal width")
        self.parser.add_argument('-v', "--version", action='store_true', help='Show version and exit')
        self.parser.add_argument('-m', "--mono", action='store_true', help='Disable colors')
        self.parser.add_argument('-D', '--debug', action='store_true', help='Enable debug mode')

    @staticmethod
    def create_parent_basic():
        parent_basic = argparse.ArgumentParser(add_help=False)
        parent_basic.add_argument('-i', '--index', metavar="I", type=int, help='Run a specific test index')
        parent_basic.add_argument('-p', '--pattern', metavar="P", type=str, default='@.in @.sol',
                                  help='Input/output file pattern (default: "@.in @.sol")')
        return parent_basic

    @staticmethod
    def create_parent_manip():
        parent_manip = argparse.ArgumentParser(add_help=False)
        parent_manip.add_argument('--width', '-w', type=int, help="Terminal width")
        parent_manip.add_argument('--unlabel', '-u', action='store_true', help='Remove all labels')
        parent_manip.add_argument('--number', '-n', action='store_true', help='Number labels')
        parent_manip.add_argument('--sort', '-s', action='store_true', help="Sort test cases by input size")
        parent_manip.add_argument('--pattern', '-p', metavar="@.in @.out", type=str, default='@.in @.sol',
                                  help='Input/output file pattern (default: "@.in @.sol")')
        return parent_manip

    def add_parser_run(self):
        parser_run = self.subparsers.add_parser('run', help='Runs a task in raw terminal', parents=[self.parent_basic], add_help=False)
        parser_run.add_argument( "-h", "--help", action="help", help="Show help message and exit" )
        parser_run.add_argument('target_list', metavar='TARGET', type=str, nargs='*', help='Solvers files, test cases or directories containing them')
        parser_run.add_argument('-f', '--filter', action='store_true', help='Filter solver files in temporary directory before running')
        parser_run.add_argument('-e', '--eval', action='store_true', help='Show percentage of passed tests')
        parser_run.add_argument('-c', '--compact', action='store_true', help='Hide test case descriptions in failures')

        group_n = parser_run.add_mutually_exclusive_group()
        group_n.add_argument('-n', '--none', action='store_true', help='Hide all failures')
        group_n.add_argument('-a', '--all', action='store_true', help='Show all failures')

        # add an exclusive group for diff mode
        group = parser_run.add_mutually_exclusive_group()
        group.add_argument('-d', '--down', action="store_true", help="Diff mode: top-to-bottom")
        group.add_argument('-s', '--side', action="store_true", help="Diff mode: side-by-side")
        parser_run.set_defaults(func=Main.run)

    def add_parser_task(self):
        parser_task = self.subparsers.add_parser('task', help='Manage individual tasks', add_help=False)
        parser_task.add_argument( "-h", "--help", action="help", help="Show help message and exit" )
        subpar_task = parser_task.add_subparsers(title='subcommands', metavar='COMMAND', help='DESCRIPTION')

        parser_open = subpar_task.add_parser('open', parents=[self.parent_basic], help='Open a task in tui')
        parser_open.add_argument("-f", "--filter", action='store_true', help='Filter solver files in temporary directory before running')
        parser_open.add_argument('target_list', metavar='T', type=str, nargs='*', help='Solvers, test cases or directories to load')
        parser_open.set_defaults(func=Main.task_open)

        parser_list = subpar_task.add_parser('list', parents=[self.parent_basic], help='List tasks')
        parser_list.add_argument('-g', '--global-cache', action='store_true', help='Use global cache for remote URL sources')
        parser_list.add_argument('-u', '--update', action='store_true', help='Force update remote URL sources')
        parser_list.add_argument("-a", '--all', action='store_true', help='Show all tasks')
        parser_list.set_defaults(func=Main.task_list)

    def add_parser_reset(self):
        parser_reset = self.subparsers.add_parser('reset', help='Reset configuration', add_help=False)
        parser_reset.add_argument( "-h", "--help", action="help", help="Show help message and exit" )
        subpar = parser_reset.add_subparsers(title='subcommands', metavar='COMMAND', help='DESCRIPTION')
    
        reset_cache = subpar.add_parser('cache', help='Clear configuration cache')
        reset_cache.set_defaults(func=Main.clear_cache)

        reset_config = subpar.add_parser('global', help='Reset global configuration to factory default')
        reset_config.set_defaults(func=Main.reset_config)

        reset_lang = subpar.add_parser('languages', help='Reset languages configuration to factory default')
        reset_lang.set_defaults(func=Main.reset_languages)

    def add_parser_config(self):
        parser_cfg = self.subparsers.add_parser('config', help='Configure settings', add_help=False)
        parser_cfg.add_argument( "-h", "--help", action="help", help="Show help message and exit" )
        subpar_repo = parser_cfg.add_subparsers(title='subcommands', metavar='COMMAND', help='DESCRIPTION') 

        cfg_set = subpar_repo.add_parser('set', help='Set default configuration values')

        g_diff = cfg_set.add_mutually_exclusive_group()
        g_diff.add_argument('--side', action='store_true', help='Set side_by_side diff mode')
        g_diff.add_argument('--down', action='store_true', help='Set up_to_down   diff mode')

        cfg_set.add_argument("--editor", metavar="cmd", type=str, help='Set editor command')
        cfg_set.add_argument("--borders", metavar="[0|1]", type=str, help='Enable borders')
        cfg_set.add_argument("--images", metavar="[0|1]", type=str, help='Enable images')
        cfg_set.add_argument("--timeout", metavar="sec", type=int, help='Set timeout')

        cfg_set.set_defaults(func=Main.config)

        cfg_list = subpar_repo.add_parser('list', help='List default configuration values')
        cfg_list.set_defaults(func=Main.list)

    def add_parser_class(self):
        parser_class = self.subparsers.add_parser('class', help='Manage class tasks', add_help=False)
        parser_class.add_argument( "-h", "--help", action="help", help="Show help message and exit" )
        subpar_class = parser_class.add_subparsers(title='subcommands', metavar='COMMAND', help='DESCRIPTION')

        collect_cmd = subpar_class.add_parser("collect", help="Colect and merge data from many repos")
        collect_cmd.add_argument("path", type=str, nargs="+", help="Paths to repos")
        collect_cmd.add_argument("--json", "-j", type=str, help="Path to save the extracted JSON data")
        collect_cmd.add_argument("--csv", "-c", type=str, help="Path to save the extracted CSV data")
        collect_cmd.add_argument("--block_prefix", "-b", type=str, help="Block prefix to insert in csv file")
        collect_cmd.set_defaults(func=CmdCollect.collect_batch)

        pull_cmd = subpar_class.add_parser("pull", help="Perform git pull in many repos using threads")
        pull_cmd.add_argument("path", type=str, nargs="+", help="Paths to repos")
        pull_cmd.add_argument("-t", "--threads", type=int)
        pull_cmd.set_defaults(func=pull_all_parallel_main)

    def add_parser_collect(self):
        parser_repo = self.subparsers.add_parser('collect', help='Collect evaluation data', add_help=False)
        parser_repo.add_argument( "-h", "--help", action="help", help="Show help message and exit" )
        subpar_collect = parser_repo.add_subparsers(title='subcommands', metavar='COMMAND', help='DESCRIPTION')

        # repo_update = subpar_repo.add_parser("update", parents=[self.parent_folder], help="Update repository cache")
        # repo_update.set_defaults(func=CmdRep.update)

        parser_task = subpar_collect.add_parser('task', help='Collect data from task', add_help=False)
        parser_task.add_argument( "-h", "--help", action="help", help="Show help message and exit" )
        parser_task.add_argument('label', type=str, help='Task label')
        parser_task.add_argument('graph', nargs=2, type=int, metavar=('WIDTH', 'HEIGHT'), help="Show task graph")
        parser_task.set_defaults(func=Main.collect_task)

        repo_collect = subpar_collect.add_parser("repo", help="Collect data from this repository")
        repo_collect.add_argument("--json", action='store_true', help="Collect as json data")
        repo_collect.add_argument("--resume", action='store_true', help="Collect resume")
        repo_collect.add_argument("--log", action='store_true', help="Collect history log")
        repo_collect.add_argument('--game', action='store_true', help="Collect game info")
        repo_collect.add_argument('--daily', action='store_true', help="Daily graph")
        repo_collect.add_argument('--width', type=int, default=100, help="Daily graph width")
        repo_collect.add_argument('--height', type=int, default=10, help="Daily graph height")
        repo_collect.add_argument('--color', type=int, default=1, help="Daily graph color [0|1]")
        repo_collect.set_defaults(func=CmdCollect.collect_main)

    def add_parser_rep_actions(self):
        parser_init = self.subparsers.add_parser('init', help='Initialize empty TKO repository', add_help=False)
        parser_init.add_argument( "-h", "--help", action="help", help="Show help message and exit" )
        parser_init.add_argument('-l', '--language', type=str, metavar=('LANG'), help='Default repository language (e.g. py, cpp, java, go)')
        parser_init.set_defaults(func=Main.init)

        parser_open = self.subparsers.add_parser('open', help='Open repository in interactive mode', add_help=False)
        parser_open.add_argument( "-h", "--help", action="help", help="Show help message and exit" )
        parser_open.add_argument('-g', '--global-cache', action='store_true', help='Use global cache for remote URL sources')
        parser_open.add_argument('-u', '--update', action='store_true', help='Force update remote URL sources')
        parser_open.add_argument('-o', '--offline', action='store_true', help='Offline mode')
        parser_open.set_defaults(func=Main.open)

        parser_source = self.subparsers.add_parser('remote', help='Manage remote task sources', add_help=False)
        parser_source.add_argument( "-h", "--help", action="help", help="Show help message and exit" )
        sub_source = parser_source.add_subparsers(title='subcommands', metavar='COMMAND', help='DESCRIPTION')
        # create subcommands inside source
        source_add = sub_source.add_parser("add", help="Add a new task source", add_help=False)
        source_add.add_argument( "-h", "--help", action="help", help="Show help message and exit" )
        source_add.add_argument('name', type=str, help='Name of the remote')
        source_add.add_argument('target', type=str, metavar=('TARGET'), help='Remote source: git URL, local directory or preset name (e.g. +fup, +ed, +poo)')
        source_add.add_argument('-q', '--quest', action='append', metavar=('QUEST_ID'), type=str, help='Load all tasks only from selected quests')
        source_add.add_argument('-t', '--task', action='append', metavar=('TASK_ID'), type=str, help='Only load tasks this tasks')
        source_add.add_argument('-d', '--destiny', type=str, help='Quest destination for filtered quests and tasks added with this source')
        
        source_add.add_argument('-b', '--branch', type=str, default='master', help='Branch name for git remote sources')
        source_add.add_argument('-w', '--write', action='store_true', help='Allow modifications for local directory remotes (default: readonly)')
        source_add.set_defaults(func=Main.remote_add)

        source_list = sub_source.add_parser("list", help="List remote task sources", add_help=False)
        source_list.add_argument( "-h", "--help", action="help", help="Show help message and exit" )
        source_list.set_defaults(func=Main.remote_lists)

        source_del = sub_source.add_parser("rm", help="Remove a remote task source", add_help=False)
        source_del.add_argument( "-h", "--help", action="help", help="Show help message and exit" )
        source_del.add_argument('name', type=str, help='Name of the remote to be removed')
        source_del.set_defaults(func=Main.remote_rm)

        source_filter = sub_source.add_parser("filter", help="Manage filters for a remote task source", add_help=False)
        source_filter.add_argument( "-h", "--help", action="help", help="Show help message and exit" )
        source_filter.add_argument('name', type=str, help='Name of the remote')
        source_filter.add_argument('-q', '--quest', action='append', metavar=('QUEST_ID'), type=str, help='Add quests to the filter list')
        source_filter.add_argument('-t', '--task', action='append', metavar=('TASK_ID'), type=str, help='Add tasks to the filter list')
        source_filter.add_argument('--clear', action='store_true', help='Clear all filters')
        source_filter.add_argument('-d', '--destiny', type=str, help='Filter destination')
        source_filter.set_defaults(func=Main.remote_filter)
        

    def add_parser_build(self):
        parser_build = self.subparsers.add_parser('build', help='Build repository artifacts', add_help=False)
        parser_build.add_argument( "-h", "--help", action="help", help="Show help message and exit" )
        subparsers = parser_build.add_subparsers(title='subcommands', metavar='COMMAND', help='DESCRIPTION')

        parser_b = subparsers.add_parser('tests', parents=[self.parent_manip], help='Build a test target', add_help=False)
        parser_b.add_argument( "-h", "--help", action="help", help="Show help message and exit" )
        parser_b.add_argument('target', metavar='T_OUT', type=str, help='Target to be built')
        parser_b.add_argument('target_list', metavar='T', type=str, nargs='+', help='Input test targets')
        parser_b.set_defaults(func=Main.build)

        # subparser for the 'build' command
        parser_r = subparsers.add_parser('mapi', help='Build .mapi file', add_help=False)
        parser_r.add_argument( "-h", "--help", action="help", help="Show help message and exit")
        parser_r.add_argument('targets', metavar='T', type=str, nargs='*', help='directories')
        parser_r.add_argument("--check", "-c", action="store_true", help="Check if the file needs to be rebuilt")
        parser_r.add_argument("--brief", "-b", action="store_true", help="Brief mode")
        # parser_r.add_argument("--pandoc", "-p", action="store_true", help="Use pandoc rather than python markdown")
        parser_r.add_argument("--remote", "-r", action="store_true", help="Search for remote.cfg file and create absolute links")
        parser_r.add_argument("--erase", "-e", action="store_true", help="Erase .md and .tio temp files")
        parser_r.add_argument("--debug", "-d", action='store_true', help="Display debug msgs")
        parser_r.set_defaults(func=build_main)

        # subparser for the 'indexer' command
        parser_i = subparsers.add_parser('indexer', help='Index Readme file', add_help=False)
        parser_i.add_argument( "-h", "--help", action="help", help="Show help message and exit")
        parser_i.add_argument('path', type=str, help='Path to Markdown file')
        parser_i.add_argument("base", type=str, help="Folder with the problems")
        parser_i.set_defaults(func=indexer_main)

        # subparser for the 'html' command
        parser_h = subparsers.add_parser('html', help='Generate HTML file from markdown file', add_help=False)
        parser_h.add_argument( "-h", "--help", action="help", help="Show help message and exit")
        parser_h.add_argument('input', type=str, help='Input markdown file')
        parser_h.add_argument('output', type=str, help='Output HTML file')
        parser_h.add_argument('--title', type=str, default="Problema", help='Title of the HTML file')
        parser_h.set_defaults(func=html_main)

        # subparser for the 'mdpp' command
        parser_m = subparsers.add_parser('mdpp', help='Preprocessor for markdown files', add_help=False)
        parser_m.add_argument( "-h", "--help", action="help", help="Show help message and exit")
        parser_m.add_argument('targets', metavar='T', type=str, nargs='*', help='Readme files or None to default task behavior')
        parser_m.add_argument('--quiet', '-q', action="store_true", help='quiet mode')
        parser_m.add_argument('--clean', '-c', action="store_true", help='clean mode')
        parser_m.set_defaults(func=mdpp_main)

        # subparser for the 'older' command
        parser_o = subparsers.add_parser('older', help='Check if the source is newer than the target', add_help=False)
        parser_o.add_argument( "-h", "--help", action="help", help="Show help message and exit")
        parser_o.add_argument('targets', type=str, nargs='+', help='Target files or directories')
        parser_o.set_defaults(func=older_main)

        parser_diff = subparsers.add_parser('diff', help='Show diff for 2 inputs or files', add_help=False)
        parser_diff.add_argument( "-h", "--help", action="help", help="Show help message and exit")
        exclusive_group_target = parser_diff.add_mutually_exclusive_group(required=True)
        exclusive_group_target.add_argument('--path', '-f', action='store_true', help='Targets are paths')
        exclusive_group_target.add_argument('--text', '-t', action='store_true', help='Compare two texts')
        parser_diff.add_argument('target_a', type=str, help='First target to be compared')
        parser_diff.add_argument('target_b', type=str, help='Second target to be compared')
        exclusive_group = parser_diff.add_mutually_exclusive_group()
        exclusive_group.add_argument('--side', '-s', action='store_true', help="Diff mode side-by-side")
        exclusive_group.add_argument('--down', '-d', action='store_true', help="Diff mode up-to-down")
        parser_diff.set_defaults(func=Main.diff)

        # subparser for the 'redirect' command
        parser_rm = subparsers.add_parser('redirect', help='Create redirected markdown file', add_help=False)
        parser_rm.add_argument( "-h", "--help", action="help", help="Show help message and exit")
        parser_rm.add_argument('target', type=str, help='Directories')
        parser_rm.add_argument('--output', '-o', type=str, help='Output file')
        parser_rm.set_defaults(func=remote_main)

        # subparser for the 'filter' command
        parser_f = subparsers.add_parser('filter', help='Filter code removing answers', add_help=False)
        parser_f.add_argument( "-h", "--help", action="help", help="Show help message and exit")

        parser_f.add_argument('target', type=str, help='file or directory to process')
        parser_f.add_argument('-u', '--update', action="store_true", help='update source file')
        parser_f.add_argument('-c', '--cheat', action="store_true", help='recursive cheat mode cleaning comments on students files')
        parser_f.add_argument('-o', '--output', type=str, help='output target')
        parser_f.add_argument("-r", "--recursive", action="store_true", help="recursive mode")
        parser_f.add_argument("-f", "--force", action="store_true", help="force mode")
        parser_f.add_argument("-q", "--quiet", action="store_true", help="quiet mode")
        parser_f.add_argument("-i", "--indent", type=int, default=0, help="indent using spaces")
        parser_f.set_defaults(func=filter_main)

        parser_drafts = subparsers.add_parser('drafts', help='Create drafts for TKO task using src dir', add_help=False)
        parser_drafts.add_argument("-h", "--help", action="help", help="Show help message and exit")
        parser_drafts.set_defaults(func=build_drafts_main)


def execute(parser: argparse.ArgumentParser, args: argparse.Namespace) -> int:
    settings = Settings(args.globaldir)
    if args.width is not None:
        RawTerminal.set_terminal_size(args.width)
    settings.load_settings()

    if args.mono:
        AnsiColor.enabled = False
        RenderConfig.mode = RenderMode.PLAIN
    else:
        AnsiColor.enabled = True

    if args.debug:
        ic.configureOutput(includeContext=True, outputFunction=print)
        ic.enable()
        ic("Debug mode enabled")
    else:
        ic.disable()

    if args.version:
        if args.version:
            print("tko " + __version__)
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

if __name__ == '__main__':
    main()
