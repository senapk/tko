from __future__ import annotations

import argparse
import json
from pathlib import Path
from icecream import ic # type: ignore

from tko.cmds.cmd_task import CmdTask
from tko.cmds.cmd_collect import CollectMany, CollectSingle
from tko.cmds.cmd_open import CmdOpen
from tko.cmds.cmd_run import Run
from tko.cmds.cmd_build import CmdBuild
from tko.cmds.cmd_config import CmdConfig, ConfigParams
from tko.enums.diff_mode import DiffMode
from tko.feno.html import convert_markdown_to_html
from tko.feno.indexer import fix_readme
from tko.feno.older import Older
from tko.feno.remote_md import Absolute
from tko.feno.remote_md import Absolute
from tko.feno.title import FenoTitle
from tko.mico.collected import Collected
from tko.repository.game_coordinator import GameCoordinator
from tko.repository.repository_loader import RepositoryLoader
from tko.enums.diff_count import DiffCount
from tko.mico.pull import Pull
from tko.feno.build import build_all

from tko.util.param import Param
from tko.util.pattern_loader import PatternLoader

from tko.config.settings import Settings
from tko.cmds.cmd_diff import cmd_diff

from tko.repository.repository import Repository
from tko.repository.rep_paths import RepPaths
from tko.config.check_version import CheckVersion
from tko.repository.rep_starter import RepStarter
from tko.repository.rep_source_actions import RepSourceActions
from tko.repository.git_cache import GitCache
from tko.feno.filter import CodeFilter, DeepFilter
from tko.feno.mdpp import Action, Mdpp

class Task:
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

        settings = Settings(args.settings)
        if not args.side and not args.down:
            param.set_diff_mode(settings.app.diff_mode)
        elif args.side:
            param.set_diff_mode(DiffMode.SIDE)
        elif args.down:
            param.set_diff_mode(DiffMode.DOWN)
        target_list = [Path(target) for target in args.target_list]
        cmd_run = Run(settings, target_list, param)
        if args.eval:
            cmd_run.show_track_info().show_self_info()

        cmd_run.execute()

    @staticmethod
    def list(args: argparse.Namespace) -> None:
        settings = Settings(args.settings)
        repo, _ = Main.load_repo(args.changedir, show_warnings=True, auto_load=True, global_cache=args.global_cache, force_update=args.update)
        if repo is None:
            return
        action = CmdOpen(settings, repo, args.update)
        action.list(show_all = args.all)

    @staticmethod
    def open(args: argparse.Namespace) -> None:
        PatternLoader.pattern = args.pattern
        param = Param.Basic().set_index(args.index)
        settings = Settings(args.settings)
        param.set_diff_mode(settings.app.diff_mode)
        if args.filter:
            param.set_filter(True)
        cmd_run = Run(settings, args.target_list, param)
        cmd_run.set_curses()
        cmd_run.execute()

class Main:
    @staticmethod
    def load_repo(dir_path: Path, show_warnings: bool = True, auto_load: bool = True, global_cache: bool = False, force_update: bool = False, force_offline: bool = False) -> tuple[Repository | None, Path | None]:
        if global_cache:
            RepPaths.use_global_cache_folder = True
            print(f"Usando cache global em: {RepPaths('').get_cache_folder()}")
        dir_parent = RepPaths.rec_search_for_repo_parents(dir_path)
        if dir_parent is not None:
            mode = GitCache.UpdateMode.IF_OLDER
            if force_update:
                mode = GitCache.UpdateMode.ALWAYS
            elif force_offline:
                mode = GitCache.UpdateMode.NEVER
            repo = Repository(dir_parent, update_mode=mode, recursive_search=False)
            if auto_load:
                from tko.repository.repository_loader import RepositoryLoader
                from tko.repository.game_coordinator import GameCoordinator
                RepositoryLoader(repo).load_config()
                GameCoordinator(repo).load_game(verbose=True)
            return repo, dir_parent

        if show_warnings:
            print("Nenhum repositório TKO encontrado.")
        return None, None

    @staticmethod
    def open(args: argparse.Namespace):
        settings = Settings(args.settings)
        settings = Settings(args.settings)
        repo, _ = Main.load_repo(args.changedir, show_warnings=True, auto_load=True, global_cache=args.global_cache, force_update=args.update)
        if repo is None:
            return
        from tko.repository.repository_watcher import RepositoryWatcher
        watcher = RepositoryWatcher(repo).start_watching()
        action = CmdOpen(settings, repo, args.update)
        if not args.offline:
            if not CheckVersion(settings).is_updated():
                action.display_need_update()
        action.execute()
        watcher.stop_watching()

    @staticmethod
    def collect_task(args: argparse.Namespace):
        settings = Settings(args.settings)
        repo, _ = Main.load_repo(args.changedir, force_update=False)
        if repo is None:
            return
        width: int  = args.graph[0]
        height: int  = args.graph[1]
        CmdTask.show_graph(settings, repo, args.label, width, height)

    @staticmethod
    def update(args: argparse.Namespace):
        folder = Path(args.folder)
        if not folder.is_dir():
            print(f"Folder {folder} does not exist.")
            return
        rep = Repository(folder)
        if not rep.found():
            print(f"Folder {folder} is not a valid tko repository.")
            return

        RepositoryLoader(rep).load_config()
        GameCoordinator(rep).load_game(verbose=True)
        print(f"Repositório cache atualizado.")

    @staticmethod
    def init(args: argparse.Namespace):
        settings = Settings(args.settings)
        changedir: Path | None = args.changedir
        language: str | None = args.language
        rep_starter = RepStarter(settings=settings, folder=changedir, language=language)
        rep_starter.execute()

class Remote:
    @staticmethod
    def remote_list(args: argparse.Namespace):
        settings = Settings(args.settings)
        repo, _ = Main.load_repo(args.changedir)
        if repo is None:
            return
        rep_actions = RepSourceActions(settings, repo)
        rep_actions.remote_list()

    @staticmethod
    def remote_rm(args: argparse.Namespace):
        name: str = args.name
        settings = Settings(args.settings)
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
        task_filter: list[str] | None = None
        try:
            settings = Settings(args.settings)
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
                index=args.index,
                filter_quest=quest_filter, 
                filter_task=task_filter,
                filter_to=args.to,
                writeable=writeable)
            rep_actions.print_end_msg()
        except ValueError as e:
            print(f"Erro ao adicionar fonte: {e}")

    @staticmethod
    def remote_filter(args: argparse.Namespace):
        name: str = args.name
        quests: list[str] | None = args.quest
        tasks: list[str] | None = None
        clear: bool = args.clear
        if clear and (quests or tasks):
            print("Erro: --clear não pode ser usado com --quest ou --task")
            return
        settings = Settings(args.settings)
        repo, _ = Main.load_repo(args.changedir)
        if repo is None:
            return
        rep_actions = RepSourceActions(settings, repo)
        rep_actions.remote_filter(alias=name, filter_quest=quests, filter_task=tasks, clear=clear, filter_to=args.to)

    @staticmethod
    def remote_set(args: argparse.Namespace):
        name: str = args.name
        settings = Settings(args.settings)
        repo, _ = Main.load_repo(args.changedir)
        if repo is None:
            return
        rep_actions = RepSourceActions(settings, repo)
        rep_actions.remote_set(alias=name, target=args.target, index=args.index)

class Config:
    @staticmethod
    def clear_cache(args: argparse.Namespace):
        repo, _ = Main.load_repo(args.changedir)
        if repo is None:
            print("Nenhum repositório TKO encontrado.")
            return
        repo.git_cache.clear_cache()

    @staticmethod
    def reset_config(args: argparse.Namespace):
        sp = Settings(args.settings).reset().save_settings()
        print(sp.get_settings_file())

    @staticmethod
    def reset_languages(args: argparse.Namespace):
        sp = Settings(args.settings)
        sp.get_languages_settings().reset().save_file_settings()
        print(sp.get_languages_file())

    @staticmethod
    def config(args: argparse.Namespace):
        settings = Settings(args.settings)
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
        settings = Settings(args.settings)
        print(f"SettingsFile\n- {settings.settings_dir}")
        print(str(settings))

class Build:
    @staticmethod
    def tests(args: argparse.Namespace):
        settings = Settings(args.settings)
        PatternLoader.pattern = args.pattern
        manip = Param.Manip().set_unlabel(args.unlabel).set_to_sort(args.sort).set_to_number(args.number)
        build = CmdBuild(Path(args.target), [Path(x) for x in args.target_list], manip, settings)
        build.execute()

    @staticmethod
    def all(args: argparse.Namespace):
        build_all([Path(x) for x in args.targets], args.remote, args.check, args.erase, args.brief)

    @staticmethod
    def diff(args: argparse.Namespace):
        cmd_diff(args.target_a, args.target_b, args.side, args.path)

    @staticmethod
    def remote(args: argparse.Namespace):
        Absolute.convert_or_copy_or_print(args.target, args.output)

    @staticmethod
    def filter(args: argparse.Namespace):
        if args.cheat:
            args.recursive = True

        if args.recursive:
            CodeFilter.cf_recursive(args.target, args.output, force=args.force, cheat=args.cheat, quiet=args.quiet, indent=args.indent)
            exit()

        CodeFilter.cf_single_file(args.target, args.output, args.update, args.cheat)

    @staticmethod
    def drafts(args: argparse.Namespace):
        changedir = args.changedir
        here = Path(".").resolve() if changedir is None else Path(changedir).resolve()
        print(f"Updating drafts in {here}")
        source_src = CodeFilter.get_default_src_dir(here)
        drafts_dest = CodeFilter.get_source_drafts_dir(here)
        if source_src.is_dir():
            filter = DeepFilter().set_indent(4)
            filter.execute(source_src, drafts_dest, 5)
    
    @staticmethod
    def older(args: argparse.Namespace):
        print(Older.find_older(args.targets))

    @staticmethod
    def mdpp(args: argparse.Namespace):
        targets: list[Path] = [Path(x) for x in args.targets]
        if len(args.targets) == 0:
            targets = [Path("README.md")]
            print(f"Updating README.md in {Path().name}")

        action = Action.RUN if not args.clean else Action.CLEAN
        for target in targets:
            Mdpp.update_file(target, action, args.quiet)

    @staticmethod
    def html(args: argparse.Namespace):
        # Verifica se os arquivos têm as extensões corretas
        if not args.input.endswith('.md'):
            print("Erro: O arquivo de entrada Markdown deve ter a extensão .md")
            exit(1)
        if not args.output.endswith('.html'):
            print("Erro: O arquivo de saída HTML deve ter a extensão .html")
            exit(1)

        title: str = ""
        if args.title:
            title = args.title
        else:
            title = FenoTitle.extract_title(args.input)
        convert_markdown_to_html(title, args.input, args.output)

    @staticmethod
    def index(args: argparse.Namespace):
        fix_readme(
            index=Path(args.index), 
            base_dir=Path(args.base), 
            default_quest_name="sandbox", 
            verbose=True, 
            save_titles=args.save, 
            load_titles=args.load
        )
        return 0
    
class Collect:
    @staticmethod
    def collect_batch(args: argparse.Namespace):
        git_repo_list: list[Path] = [Path(x) for x in args.path]
        CollectMany.execute(git_repo_list, json_path=args.json, csv_path=args.csv, block_prefix=args.block_prefix)

    @staticmethod
    def collect_main(args: argparse.Namespace):
        params = CollectSingle.CollectParams()
        params.folder = Path() if args.changedir is None else Path(args.changedir)
        params.width = args.width
        params.height = args.height
        params.daily = args.daily
        params.resume = args.resume
        params.game = args.game
        params.log = args.log
        params.json_output = args.json
        params.colored = args.color
        data: Collected = CollectSingle.collect(params)

        if params.json_output:
            # print(yaml.dump(data))
            print(json.dumps(data.to_dict(), indent=4, ensure_ascii=False))

class Class:
    @staticmethod
    def pull_all_parallel_main(args: argparse.Namespace) -> None:
        path_list = [Path(p) for p in args.path]
        n_threads = args.threads if args.threads else 10
        Pull.pull_all_parallel(path_list, n_threads)
    